#!/usr/bin/env python3
from jiraConnectionFactory import JiraSession
import urllib.request
import urllib.parse
import urllib.error
import datetime as dt

# TODO: Remove duplication of constants
base_url = "https://tasks.novarumcloud.com/"
api_url = base_url + "rest/api/2"

def getContentForQuery(query_filter):
    jql_websafe_query = urllib.parse.quote(query_filter)
    # Search for the defined filters
    response_list = sesh.get(api_url + "/search?jql=" + jql_websafe_query)
    return(response_list.json())

def getChoiceAfterPresenting(content):
    for issue in content['issues']:
        print("{}: {}".format(issue["key"], issue["fields"]["summary"]))
        choice = input("-?- Do you want to pool time into this one? /y/\n")
        if choice == "y":
            return(issue)
    print("-!- You should have chosen where to pool time. Nothing to do, exiting.")
    exit(1)

def getRemainingTime(content, targetIssue_key):
    '''Takes all the tickets that have been worked all today, calculates the total time spent today, then
    returns how much needs logging up to 7.5 hours
    '''
    totalTimeLoggedToday = 0
    # Get the worklogs for the issue
    allWorklogs = sesh.get(api_url + "/issue/" + targetIssue_key + "/worklog").json()
    # Has some other info at top level regarding all the worklogs in general, but we only everything from one
    for worklog in allWorklogs["worklogs"]:
        timeStarted = worklog.get("created")
        if timeStarted == today:
            totalTimeLoggedToday += worklog.get("timeSpentSeconds")

    return(totalTimeLoggedToday)

def addWorklog(targetIssue_key, time_to_pool):
    payload = {
        "comment": "In-between miscellaneous work",
        "started": dt.datetime.now().strftime("%Y-%m-%dT%X.000+0000"),
        "timeSpentSeconds": time_to_pool  # TODO: time spent should be calculated from the 7.5 remaining hours
    }
    print(api_url + "/issue/" + targetIssue_key + "/worklog")
    postOutcome = sesh.post(api_url + "/issue/" + targetIssue_key + "/worklog", json=payload)
    if postOutcome.status_code == 201:
        print("-=- Time logged well.")
    else:
        print("-!- Problem with error code {}".format(postOutcome.status_code))


if __name__ == "__main__":
    with JiraSession() as sesh:
        print("-=- Finding tickets with time logged today...")
        query_todaysLoggedTickets = "worklogAuthor = currentUser() AND worklogDate = endOfDay() "
        content = getContentForQuery(query_todaysLoggedTickets)
        targetIssue = getChoiceAfterPresenting(content)
        print("-=- Logging time into the chosen ticket {}...".format(targetIssue["key"]))
        timeToBalance = getRemainingTime(content, targetIssue["key"])
        # addWorklog(targetIssue["key"], timeToBalance)
