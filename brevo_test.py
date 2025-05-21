from dotenv import load_dotenv
from sib_api_v3_sdk.configuration import Configuration
from sib_api_v3_sdk.api_client import ApiClient
from sib_api_v3_sdk.api.transactional_emails_api import TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail
from sib_api_v3_sdk.rest import ApiException
import os
load_dotenv()

#init variables
BREVOAPIKEY= os.getenv("BREVO_API_KEY")
toEmail="antlaw0@gmail.com"
fromEmail="antlawgames@gmail.com"
print("Loaded API key:", BREVOAPIKEY)

# Configure API key
configuration = Configuration()
configuration.api_key['api-key'] = BREVOAPIKEY

# Initialize API client manually (no context manager)
api_client = ApiClient(configuration)
api_instance = TransactionalEmailsApi(api_client)

# Construct email
email = SendSmtpEmail(
    to=[{"email": toEmail}],
    sender={"name": "Test App", "email": fromEmail},
    subject="Test Email",
    html_content="<p>This is a test email sent via Brevo SDK</p>"
)

# Send and print result
try:
    response = api_instance.send_transac_email(email)
    print("Sent:", response)
except ApiException as e:
    print("Error sending email:", e)
