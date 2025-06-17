import os
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from langchain_openai import ChatOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

SHEET_NAME = "AI_Marketing_System"
CREDENTIALS_FILE = "credentials.json"
SCOPE = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7, api_key=OPENAI_API_KEY)
vision_llm = ChatOpenAI(model="gpt-4-vision-preview", max_tokens=1024, api_key=OPENAI_API_KEY)

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    gspread_client = gspread.authorize(creds)
    print("Google Sheets client initialized successfully.")
except Exception as e:
    print(f"Error initializing Google Sheets client: {e}")
    gspread_client = None