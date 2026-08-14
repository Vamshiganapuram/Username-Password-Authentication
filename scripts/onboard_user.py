import os
import sys
import requests

DOMAIN = os.environ["AUTH0_DOMAIN"]
CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
CONNECTION = os.environ["AUTH0_CONNECTION"]

email = sys.argv[1]
password = sys.argv[2]

# 1. Get Management API token
token_response = requests.post(
    f"https://{DOMAIN}/oauth/token",
    json={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "audience": f"https://{DOMAIN}/api/v2/",
        "grant_type": "client_credentials"
    }
)

token_response.raise_for_status()
token = token_response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. Create user with metadata
user_response = requests.post(
    f"https://{DOMAIN}/api/v2/users",
    headers=headers,
    json={
        "connection": CONNECTION,
        "email": email,
        "password": password,
        "email_verified": False,
        "user_metadata": {
            "onboarding_status": "completed"
        },
        "app_metadata": {
            "department": "Engineering",
            "onboarded_by": "GitHub Actions"
        }
    }
)

user_response.raise_for_status()

user = user_response.json()

print("User created successfully")
print("User ID:", user["user_id"])

# 3. Find the default User role
roles_response = requests.get(
    f"https://{DOMAIN}/api/v2/roles",
    headers=headers
)

roles_response.raise_for_status()

roles = roles_response.json()

user_role = next(
    (role for role in roles if role["name"] == "User"),
    None
)

if not user_role:
    raise Exception("User role not found")

# 4. Assign User role
role_response = requests.post(
    f"https://{DOMAIN}/api/v2/users/{user['user_id']}/roles",
    headers=headers,
    json={
        "roles": [user_role["id"]]
    }
)

role_response.raise_for_status()

print("Default role assigned successfully")
print("Role:", user_role["name"])

# 5. Display final result
print("\n========== ONBOARDING COMPLETE ==========")
print("Email:", email)
print("Role:", user_role["name"])
print("Metadata: Added")
print("Status: Success")