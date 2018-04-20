#!/usr/bin/env python3
from jiraConnectionFactory import JiraSession
import urllib.request
import urllib.parse
import urllib.error

# TODO: Remove duplication of constants
base_url = "https://tasks.novarumcloud.com/"
api_url = base_url + "rest/api/2"

def getContentForQuery(query_filter):
    jql_websafe_query = urllib.parse.quote(query_filter)
    # Search for the defined filters
    response_list = sesh.get(api_url + "/search?jql=" + jql_websafe_query)
    return(response_list.json())

def getChoiceAfterPresenting(content):
    i = 1
    for issue in content['issues']:
        print("#{} {}: {}".format(i, issue["key"], issue["fields"]["summary"]))
        i += 1
    choice = 1  # TODO: This is a placeholder
    return(choice)


if __name__ == "__main__":
    with JiraSession() as sesh:
        print("TODO: Find tickets with time logged today, ala tempo sheet")
        query_todaysLoggedTickets = "worklogAuthor = currentUser() AND worklogDate = endOfDay() "
        content = getContentForQuery(query_todaysLoggedTickets)
        poolingTarget = getChoiceAfterPresenting(content)
