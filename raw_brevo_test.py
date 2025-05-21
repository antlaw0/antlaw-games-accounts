import os
import requests
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("BREVO_API_KEY")
print("Loaded API key:", api_key)

headers = {
    "accept": "application/json",
    "api-key": api_key,
    "content-type": "application/json"
}

data = {
    "sender": {"name": "Test App", "email": "antlawgames@gmail.com"},
    "to": [{"email": "antlaw0@gmail.com"}],
    "subject": "Test Email Without SDK",
    "htmlContent": "<p>This is a test email sent via direct Brevo API.</p>"
}

response = requests.post("https://api.brevo.com/v3/smtp/email", json=data, headers=headers)

print("Status code:", response.status_code)
print("Response body:", response.text)
