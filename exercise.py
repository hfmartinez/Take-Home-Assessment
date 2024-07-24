"""
Script exercise.py

Searches jira for tickets which have a description containing attribution and strips that info away.

Usage:
    python exercise.py

Description:
    This script interacts with the Jira API to retrieve and list all
    issues matching specified search parameters (description and project).
    It then generates a CSV file named 'Jira_Cleanup.csv', containing the key,
    ID, and summary of each matching issue found.

Module Dependencies:
    This script requires the following modules:
    - csv
    - requests
    - json
    - re

Author:
    Heberth Martinez
    heberthfabianmartinez@gmail.com
    Jul 24 2024
"""

import csv
import requests
import json
import re


def query_jira() -> list[dict]:
    """
    Fetches issues from Jira API based on static search parameters and return the list of issues.

    Args:
        None

    Returns:
        list: A list of dictionaries representing processed data.
            Each dictionary contains the following keys:
                - 'id' (int): Numeric identifier.
                - 'key' (str): Unique identifier.
                - 'description' (str): Description of the Jira issue.
                - 'summary' (str): Summary or description of the data element.

    Description:
        This function interacts with the Jira API to retrieve issues that match the specified description
        and belong to the given project.

        Additional information:
        - Authentication to the Jira API is done using a Basic Authentication scheme.
        - The function assumes the Jira API base endpoint is located at 'https://jira.epicgames.com/rest/api/latest/search'.
        - The function uses pagination to handle large result sets from Jira efficiently.
        - Access the Jira API documentation at this location: 'https://developer.atlassian.com/server/jira/platform/rest/v10000/api-group-search/#api-api-2-search-get'.
    """
    offset = 0
    more_pages = True
    headers = {"Authorization": f"Basic hunter2="}
    issues = []

    # pagination to handle large results
    while more_pages:
        # url definition including the filters and the fields to return
        url = f'https://jira.epicgames.com/rest/api/latest/search?fields=id,key,description,summary&jql=project = LOL and description ~ "Contributed by:"&maxResults=1000&startAt={offset}'
        response = requests.request("GET", url, headers=headers)
        issues += response.json().get("issues", [])
        offset += 1000
        if response.json().get("total", 0) < offset:
            more_pages = False
    return issues


def update_description(issue_key: str, description: str) -> bool:
    """
    Update the description of a Jira issue identified by `issue_key`.

    Args:
        issue_key (str): The key or identifier of the Jira issue to update.
        description (str): The new description to set for the Jira issue.

    Returns:
        bool: True

    Description:
        This function updates the description of a Jira issue specified by `issue_key`
        using the Jira REST API. It sends a PUT request to the Jira API endpoint
        with the updated description in the request payload.

        Additional information:
        - Authentication to the Jira API is done using a Basic Authentication scheme.
        - The function assumes the Jira API endpoint is located at 'https://jira.epicgames.com/rest/api/latest/issue/{issue_key}'.
        - Access the Jira API documentation at this location: 'https://developer.atlassian.com/server/jira/platform/rest/v10000/api-group-issue/#api-api-2-issue-issueidorkey-put'.
    """
    url = f"https://jira.epicgames.com/rest/api/latest/issue/{issue_key}"
    payload = json.dumps({"fields": {"description": f"{description}"}})
    headers = {
        "Authorization": f"Basic hunter2=",
        "Content-Type": "application/json",
    }
    response = requests.request("PUT", url, headers=headers, data=payload)
    return True


def add_to_report(issue: dict) -> None:
    """
    Append information about a Jira issue to the 'Jira_Cleanup.csv' report file.

    Args:
        issue (dict): Dictionary containing information about a Jira issue.
            It should have the following structure:
            {
                "key": str,             # Jira issue key
                "id": int,              # Jira issue ID
                "fields": {
                    "summary": str      # Summary or description of the Jira issue
                }
            }

    Returns:
        None

    Description:
        This function takes a dictionary representing a Jira issue (`issue`) and extracts
        the issue key, ID, and summary. It then appends this information to a CSV file named
        'Jira_Cleanup.csv'. If the file doesn't exist, it will be created.

        Note:
        - The CSV file is formatted with the following columns: 'key', 'id', 'summary'.
        - Each call to this function appends a new row to the CSV file with information
          from the provided Jira issue dictionary.
    """
    data = (
        issue.get("key"),
        issue.get("id"),
        issue.get("fields", {}).get("summary", ""),
    )
    with open("Jira_Cleanup.csv", "a") as out:
        csv_out = csv.writer(out)
        csv_out.writerow(data)


def main() -> None:
    """
    Fetches data from Jira, updates report and descriptions accordingly.

    This function orchestrates the main workflow:
    1. Queries Jira to retrieve a list of issues.
    2. Iterates over each issue in the results.
        - Adds each issue's key, ID, and summary to a CSV report file.
        - Updates the description of the issue in Jira by removing a specific pattern.
    3. No return value; results are directly written to 'Jira_Cleanup.csv'.

    Returns:
        None

    Description:
        This script fetches data from Jira using the `query_jira` function, processes each retrieved issue,
        and performs two main tasks:
        - Adds information about each issue to a CSV report ('Jira_Cleanup.csv') using `add_to_report` function.
        - Updates the description of each issue in Jira by modifying the original description to remove
          specific pattern using `update_description` function.

        Notes:
            - The `add_to_report` function appends data to 'Jira_Cleanup.csv', creating the file if it does not exist.
    """

    results = query_jira()
    for result in results:
        add_to_report(result)
        description = result.get("fields", {}).get("description", "")
        update_description(
            result.get("key"), re.sub(r"\nContributed by: .*\n", "", description)
        )


if __name__ == "__main__":
    main()
