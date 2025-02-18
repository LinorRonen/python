import gspread
import gitlab
import os
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")

print("Connecting to Google Sheets...")
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
print("Connected to Google Sheets.")

sheet = client.open("EmployeeData").sheet1
data = sheet.get_all_records()  

print("Raw data fetched:")
print(data)
print(f"Fetched {len(data)} employee records.")

# GitLab configuration
GITLAB_URL = "https://gitlab.com"
GROUP_ID = 97348160  

gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
print("Connected to GitLab.")

for employee in data:
    username = employee["username"]
    email = employee["email"]

    print(f"Processing employee: {username}")

    try:
        users = gl.users.list(search=username, get_all=True)
        if not users:
            print(f"User {username} not found in GitLab. Skipping...")
            continue

        user = users[0]  
        print(f"Found existing user: {user.username} (ID: {user.id})")

        group = gl.groups.get(GROUP_ID)

        existing_members = group.members.list(get_all=True)
        if any(member.id == user.id for member in existing_members):
            print(f"User {username} is already in the group.")
            continue

        group.members.create({"user_id": user.id, "access_level": 20})
        print(f"User {username} added to group with Reporter role.")

    except Exception as e:
        print(f"Error processing employee {username}: {e}")
