import requests

# Test the API
response = requests.post(
    "http://localhost:8000/ask-agent",
    json={
        "user_id": 1,
        "message": "Create a task for API documentation"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")