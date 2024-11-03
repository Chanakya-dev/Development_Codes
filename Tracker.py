import requests

# Your Google Apps Script Web App URL for POST requests
post_url = 'https://script.google.com/macros/s/AKfycbwPJGLgGs90ElZAL6bOE2109_SHQrT7efS4m8ArDGO1qynK5EAft6wOk7i9LNilmEUb/exec'

# Fetch team data from Google Sheets using the GET URL
get_url = 'https://script.google.com/macros/s/AKfycbzhvkipYZQnhU_reWDWhbT1Hgqub5r9L7Ge5b5zbxZQpuCu58PTZoV7WuKAuL-ajjmo/exec'
response = requests.get(get_url)

# Checking the response
if response.status_code == 200:
    # Get the JSON response for team data
    team_data = response.json()
    print("Team Data:", team_data)
else:
    print("Error:", response.status_code, response.text)

def initialize_output_structure(teams):
    output = {}
    for team_name, members in teams.items():
        output[team_name] = []
        for member in members:
            output[team_name].append({
                "Member Name": member["name"],
                "PR Status": "No PR",  # Default
                "Main Status": "No PR",  # Default
                "Assignment Status": "Not Done",  # Default
                "Score": 0  # Default
            })
    return output

def fetch_pull_requests(owner, repo):
    GITHUB_API_URL = f'https://api.github.com/repos/{owner}/{repo}/pulls?state=all'
    HEADERS = {'Authorization': 'token YOUR_ACCESS_TOKEN'}  # Use your personal access token
    response = requests.get(GITHUB_API_URL, headers=HEADERS)

    if response.status_code == 200:
        return response.json()  # Returns a list of pull requests
    else:
        print(f"Error fetching pull requests: {response.status_code}")
        return []

def analyze_prs(prs, output, teams):
    for pr in prs:  # Iterate through all pull requests
        pr_user = pr["user"]["login"]  # Get the GitHub username of the PR creator
        matched = False  # Track if a member matched

        for team_name, members in teams.items():
            for member in members:
                if pr_user == member["username"]:  # Compare with the member's GitHub username
                    matched = True
                    if pr["state"] == "closed":
                        output[team_name].append({
                            "Member Name": member["name"],
                            "PR Status": "Closed by " + (pr["merged_by"]["login"] if pr.get("merged_by") else "Closed"),
                            "Main Status": "No PR",  # Customize as per your logic
                            "Assignment Status": "Met Expectations",  # Customize as per your logic
                            "Score": 5  # Customize based on your scoring criteria
                        })
                    elif pr["state"] == "open":
                        output[team_name].append({
                            "Member Name": member["name"],
                            "PR Status": "Open",
                            "Main Status": "No PR",  # Customize as per your logic
                            "Assignment Status": "Outstanding",  # Customize as per your logic
                            "Score": 10  # Customize based on your scoring criteria
                        })
                    break  # Break if matched to avoid duplicate entries

        if not matched:  # If no match found, log the PR
            for team_name in output.keys():
                output[team_name].append({
                    "Member Name": "Unknown User",  # Or whatever logic you want
                    "PR Status": "PR by " + pr_user,
                    "Main Status": "No PR",  # Customize as per your logic
                    "Assignment Status": "Not Applicable",  # Customize as per your logic
                    "Score": 0  # No score for unmatched PRs
                })

if __name__ == "__main__":
    # Replace 'your_org' and 'your_repo' with your actual organization and repository
    owner = "django"
    repo = "django"

    # Fetch pull requests
    prs = fetch_pull_requests(owner, repo)

    # Initialize output structure with team data fetched from Google Apps Script
    output = initialize_output_structure(team_data)
    
    # Analyze pull requests and update the output
    analyze_prs(prs, output, team_data)

    # Send the output data to Google Apps Script
    response = requests.post(post_url, json=output)

    # Check the response
    if response.status_code == 200:
        print("Data successfully sent to Google Sheet.")
    else:
        print("Error:", response.status_code, response.text)
