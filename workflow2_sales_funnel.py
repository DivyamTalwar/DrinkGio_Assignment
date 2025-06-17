import smtplib
import requests
from typing import TypedDict
from datetime import datetime
from email.message import EmailMessage
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

from config import llm, gspread_client, SHEET_NAME, GMAIL_USER, GMAIL_APP_PASSWORD, SLACK_WEBHOOK_URL

class SalesFunnelState(TypedDict):
    lead_data: dict
    personalized_email_body: str

def capture_lead_in_sheet(state: SalesFunnelState):
    print("---NODE: CAPTURING LEAD---")
    lead = state['lead_data']
    sheet = gspread_client.open(SHEET_NAME).worksheet("Leads")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [lead['full_name'], lead['email'], timestamp, lead['ad_source']]
    sheet.append_row(row)
    print(f"Lead {lead['email']} captured.")
    return {}

def personalize_welcome_email(state: SalesFunnelState):
    print("---NODE: PERSONALIZING EMAIL---")
    prompt = ChatPromptTemplate.from_template(
        """You are a friendly brand ambassador. Write a warm, welcoming email to a new lead.
        The user, {full_name}, just signed up from an ad about '{ad_source}'.
        Personalize the email to reflect that interest. End with a CTA to check out our special offer at https://your-landing-page.com/offer.
        Keep it short, friendly, and exciting."""
    )
    chain = prompt | llm | StrOutputParser()
    email_body = chain.invoke(state['lead_data'])
    print("Personalized email content created.")
    return {"personalized_email_body": email_body}

def send_welcome_email(state: SalesFunnelState):
    print("---NODE: SENDING WELCOME EMAIL---")
    msg = EmailMessage()
    msg.set_content(state['personalized_email_body'])
    msg['Subject'] = "Welcome to the Club! ✨"
    msg['From'] = GMAIL_USER
    msg['To'] = state['lead_data']['email']
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email sent successfully to {state['lead_data']['email']}")
    except Exception as e:
        print(f"Error sending email: {e}")
    return {}

def notify_team_on_slack(state: SalesFunnelState):
    print("---NODE: NOTIFYING TEAM ON SLACK---")
    lead = state['lead_data']
    message = {"text": f"🎉 New Lead! 🎉\nName: {lead['full_name']}\nEmail: {lead['email']}\nSource: {lead['ad_source']}"}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=message)
        print("Slack notification sent.")
    except Exception as e:
        print(f"Error sending Slack notification: {e}")
    return {}

workflow = StateGraph(SalesFunnelState)
workflow.add_node("capture_lead", capture_lead_in_sheet)
workflow.add_node("personalize_email", personalize_welcome_email)
workflow.add_node("send_email", send_welcome_email)
workflow.add_node("notify_team", notify_team_on_slack)

workflow.set_entry_point("capture_lead")
workflow.add_edge("capture_lead", "personalize_email")
workflow.add_edge("personalize_email", "send_email")
workflow.add_edge("send_email", "notify_team")
workflow.add_edge("notify_team", END)

sales_funnel_app = workflow.compile()