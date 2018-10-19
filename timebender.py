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
    if len(content['issues']) == 0:
        print("-!- Can't operate on 0 issues, log some time anywhere first.")
        exit(1)

    for issue in content['issues']:
        print("{}: {}".format(issue["key"], issue["fields"]["summary"]))
        choice = input("-?- Do you want to pool time into this one? /y/\n")
        if choice == "y":
            return(issue)
    print("-!- You should have chosen where to pool time. Let's do it again!\n")
    getChoiceAfterPresenting(content)

def stopNegativity(secondsToLog):
    '''Breaks the script if the seconds to log are negative, otherwise passes them on.'''
    if secondsToLog == 0:
        print("-!- Time has been logged correctly to the minute! Have a nice evening.\n")
        exit(0)
    elif secondsToLog < 0:
        print("-!- Somebody has been overzealous with logging time - remove/reduce some worklogs and try again.\n")
        exit(0)
    else:
        return(secondsToLog)

def getRemainingTime(content, whoami):
    '''Takes all the tickets that have been worked all today, calculates the total time spent today, then
    returns how much needs logging up to 7.5 hours
    '''
    today = dt.datetime.now().strftime("%Y-%m-%d")
    totalSecondsLoggedToday = 0
    totalSecondsToWork = 7.5 * 60 * 60
    for issue in content['issues']:
        # Get the worklogs for the current issue
        allWorklogs = sesh.get(api_url + "/issue/" + issue["key"] + "/worklog").json()
        # Has some other info at top level regarding all the worklogs in general, but we only everything from one
        for worklog in allWorklogs["worklogs"]:
            # Make sure we don't count other people's time
            author = worklog["author"]["name"]
            if author != whoami:
                continue

            timeStarted = worklog.get("created")
            if timeStarted[0:10] == today:
                worklogTimeSpent = worklog.get("timeSpentSeconds")
                totalSecondsLoggedToday += worklogTimeSpent
                print("-=- A worklog was found for today's worked on ticket {}; adding {} seconds to the total.".format(issue["key"],worklogTimeSpent))

    # Now that the time logged today is obtained, calculate how much time is left to distribute
    remainingSecondsToLog = totalSecondsToWork - totalSecondsLoggedToday
    print("-=- Total time found logged today: {} hours.".format(presentNicelyInHours(totalSecondsLoggedToday)))
    return(remainingSecondsToLog)

def presentNicelyInHours(seconds):
    inHours = seconds / 60 / 60
    inHours_delimited = round(inHours, 2)
    return(str(inHours_delimited))

def addWorklog(targetIssue_key, time_to_pool):
    payload = {
        "comment": "In-between miscellaneous work and analysis",
        "started": dt.datetime.now().strftime("%Y-%m-%dT%X.000+0000"),
        "timeSpentSeconds": time_to_pool  # TODO: time spent should be calculated from the 7.5 remaining hours
    }
    postOutcome = sesh.post(api_url + "/issue/" + targetIssue_key + "/worklog", json=payload)
    if postOutcome.status_code == 201:
        print("-=- Time successfully balanced up to 7.5 hours.")
    else:
        print("-!- Problem with error code {}".format(postOutcome.status_code))


if __name__ == "__main__":
    with JiraSession() as sesh:
        print("-=- Finding tickets with time logged today...")
        query_todaysLoggedTickets = "worklogAuthor = currentUser() AND worklogDate = endOfDay() "
        content = getContentForQuery(query_todaysLoggedTickets)

        print("-=- Calculating time spent across all tickets today... may take some time to filter through old and other people's worklogs for each issue...")
        remainingSecondsToLog = stopNegativity(getRemainingTime(content, sesh.auth[0]))

        print("-=- T i m e to choose which ticket to pool the remaining {} hours into...\n".format(presentNicelyInHours(remainingSecondsToLog)))
        targetIssue = getChoiceAfterPresenting(content)

        print("-=- Logging {} hours into the chosen ticket {}...".format(presentNicelyInHours(remainingSecondsToLog), targetIssue["key"]))
        addWorklog(targetIssue["key"], remainingSecondsToLog)
