from workflow1_ad_creator import ad_creator_app
from workflow2_sales_funnel import sales_funnel_app
from config import gspread_client

def run_ad_creator():
    print("\n" + "="*50)
    print("🚀 STARTING WORKFLOW 1: AI-POWERED AD CREATOR 🚀")
    print("="*50)
    
    inputs = {"product_id": 1}
    
    if gspread_client:
        ad_creator_app.invoke(inputs)
        print("\n✅ Ad Creator Workflow Finished. Check the 'Generated_Ads' tab in your Google Sheet.")
    else:
        print("\n❌ Ad Creator Workflow Skipped: Google Sheets client not initialized.")


def run_sales_funnel():
    print("\n" + "="*50)
    print("🚀 STARTING WORKFLOW 2: AUTOMATED SALES FUNNEL 🚀")
    print("="*50)
    
    sample_lead_data = {
        "full_name": "Jamie Rivera",
        "email": "divyamtalwar15@gmail.com",
        "ad_source": "Instagram ad about 'sophisticated social drinks'"
    }
    
    inputs = {"lead_data": sample_lead_data}
    
    if gspread_client:
        sales_funnel_app.invoke(inputs)
        print("\n✅ Sales Funnel Workflow Finished. Check the 'Leads' tab, your email inbox, and your Slack channel.")
    else:
        print("\n❌ Sales Funnel Workflow Skipped: Google Sheets client not initialized.")


if __name__ == "__main__":    
    run_ad_creator()
    
    run_sales_funnel()
    
    print("\n" + "="*50)
    print("🎉 ALL WORKFLOWS COMPLETE 🎉")
    print("="*50)