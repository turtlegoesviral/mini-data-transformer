import json
from pathlib import Path

import requests

# API configuration
BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 600  # seconds

# Store authentication token
auth_token = None


def register_user(username: str, password: str, email: str):
    """Register a new user."""
    print("Registering user...")
    response = requests.post(
        "http://localhost:8000/api/v1/auth/register", json={"username": username, "password": password, "email": email}
    )
    response.raise_for_status()
    print("User registration successful")


def login(username: str, password: str):
    """Login to get authentication token."""
    global auth_token
    print("Logging in to get authentication token...")

    response = requests.post(
        "http://localhost:8000/api/v1/auth/token", data={"username": username, "password": password}
    )
    response.raise_for_status()

    token_data = response.json()
    auth_token = f"{token_data['token_type']} {token_data['access_token']}"
    print("Successfully obtained authentication token")


def get_auth_headers():
    """Get headers with authentication token."""
    if not auth_token:
        raise ValueError("Not authenticated. Please login first.")
    return {"Authorization": auth_token}


def test_transform_api():
    # API endpoint
    url = "http://localhost:8000/api/v1/transform"

    # Sample pipeline configuration
    pipeline = {
        "input_path": "data/observations.csv",
        "transformations": [
            {
                "name": "uppercase",
                "params": {
                    "columns": ["PATIENT", "ENCOUNTER", "DESCRIPTION"],
                },
            },
            {
                "name": "map",
                "params": {"mappings": {"VALUE": "VALUE_NUMERIC"}},
            },
            {
                "name": "filter",
                "params": {"column": "VALUE_NUMERIC", "operator": "==", "value": 1},
            },
        ],
    }

    try:
        # Prepare the data for the request
        data = {"pipeline": json.dumps(pipeline)}

        # Make the POST request with authentication
        headers = {"Authorization": auth_token} if auth_token else {}
        print("Sending request...")
        response = requests.post(
            url,
            data=data,
            headers=headers,
            timeout=300,  # 5 minutes timeout
        )

        # Check if the request was successful
        response.raise_for_status()

        # Print the response
        result = response.json()
        print("Success! Response:")
        print(f"Total items: {result['total']}")
        print(f"Page: {result['page']}")
        print(f"Items per page: {result['size']}")
        print(f"Total pages: {result['pages']}")
        print("\nFirst few items:")
        for item in result["items"][:5]:
            print(item)

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during API request: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
    except IOError as e:
        print(f"Error occurred while reading file: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Register and login with test credentials
    username = "testuser"
    password = "testpass123"
    email = "test@example.com"

    try:
        register_user(username, password, email)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400 and "Username already registered" in str(e.response.json()):
            print("User already exists, proceeding with login...")
        else:
            raise e

    login(username, password)

    # Then test the transform API
    test_transform_api()
