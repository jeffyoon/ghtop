#!/usr/local/bin/python3

import time
import json
import sys
import shutil
import urllib.request
import enlighten
import blessed

term = blessed.Terminal()

logfile = "log.txt"
url = "https://api.github.com/events"

def get_token():
    f = open("ghtoken.txt", "r")
    token = f.read()
    return token

def fetch_events():
    request = urllib.request.Request(url)
    request.add_header('Authorization', 'token %s' % str.strip(get_token()))
    response = urllib.request.urlopen(request)
    remaining_apis = int(response.headers['X-RateLimit-Remaining'])
    if remaining_apis < 1000:
        print("WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING ")
        print("Remaining calls: " + str(remaining_apis))
        print("WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING ")
    data = response.read()

    return json.loads(data)

def read_json_log(logfile):
    try:
        f = open(logfile, "r")
        data = f.read()
        f.close()
        return json.loads(data)
    except:
        return []

printed_event_ids = {}

def print_event(e, commits_counter):
    #print ansi_colors[hash(e["type"]) % len(ansi_colors)]

    #print e["type"]
    if e["id"] in printed_event_ids:
        return
    printed_event_ids[e["id"]] = 1

    login = e["actor"]["login"]
    repo = e["repo"]["name"][:15]

    if "bot" in login:
        return

    if e["type"] == "ReleaseEvent":
        tag = e["payload"]["release"]["tag_name"]
        print(term.white_on_firebrick3(login + " released " + tag + " of " + repo))
    elif e["type"] == "PublicEvent":
        return
    elif e["type"] == "ForkEvent":
        return
    elif e["type"] == "IssueEvent":
        return
    elif e["type"] == "IssueCommentEvent":
        issue = e["payload"]["issue"]
        print(term.green(login + " commented on issue #" + str(issue["number"]) + " on repo " + repo[:22] + " (\"" +  issue["title"][:50] + "...\")"))
    elif e["type"] == "PushEvent":
        commits = e["payload"]["commits"]
        for c in commits:
            commits_counter.update()
    elif e["type"] == "CreateEvent":
        return
    elif e["type"] == "PullRequestEvent":
        print(term.orange(login + " " + e["payload"]["action"] + " a pull request on repo " + repo[:20] + " (\"" +  e["payload"]["pull_request"]["title"][:50] + "...\")"))
        return
    elif e["type"] == "MemberEvent":
        return
       
def write_logs(events):
    f = open("tmp.log", "w")
    f.write(json.dumps(events, indent=2))
    f.close()
    shutil.move("tmp.log", logfile)

manager = enlighten.get_manager()
commits = manager.counter(desc='Commits', unit='commits', color='green')

while True:
    events = fetch_events()
    log = read_json_log(logfile)
    combined = log + events
    write_logs(combined)
    for x in combined:
        print_event(x, commits)
    time.sleep(1)