"""
Searches jira for tickets which have a description containing attribution and strips that info away.
"""
import csv
import requests
import json
import re


def query_jira():
    offset = 0
    more_pages = True
    headers = {"Authorization": f"Basic hunter2="}
    issues = []
    while more_pages:
        url = f'https://jira.epicgames.com/rest/api/latest/search?fields=id,key,description,summary&jql=project = LOL and description ~ "Contributed by:"&maxResults=1000&startAt={offset}'
        response = requests.request("GET", url, headers=headers)
        issues += response.json().get("issues", [])
        offset += 1000
        if response.json().get("total", 0) < offset:
            more_pages = False
    return issues


def update_description(issue_key, description):
    url = f"https://jira.epicgames.com/rest/api/latest/issue/{issue_key}"
    payload = json.dumps({"fields": {"description": f"{description}"}})
    headers = {
        "Authorization": f"Basic hunter2=",
        "Content-Type": "application/json",
    }
    response = requests.request("PUT", url, headers=headers, data=payload)
    return True


def add_to_report(issue):
    data = (issue.get("key"), issue.get("id"), issue.get("fields", {}).get("summary", ""))
    with open("Jira_Cleanup.csv", "a") as out:
        csv_out = csv.writer(out)
        csv_out.writerow(data)


results = query_jira()
for result in results:
    add_to_report(result)
    description = result.get("fields", {}).get("description", "")
    update_description(result.get("key"), re.sub(r"\nContributed by: .*\n", "", description))
