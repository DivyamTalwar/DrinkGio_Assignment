import json
from typing import TypedDict, List
from langchain_core.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END

from config import llm, vision_llm, gspread_client, SHEET_NAME

class AdCreatorState(TypedDict):
    product_id: int
    product_info: dict
    image_analysis: str
    generated_ads: List[dict]

def fetch_product_data(state: AdCreatorState):
    print("---NODE: FETCHING PRODUCT DATA---")
    product_id = state['product_id']
    sheet = gspread_client.open(SHEET_NAME).worksheet("Products")
    row = sheet.row_values(product_id + 1) # +1 to account for header row
    product_info = {
        "name": row[0], "description": row[1],
        "image_url": row[2], "target_audience": row[3]
    }
    return {"product_info": product_info}

def analyze_image(state: AdCreatorState):
    print("---NODE: ANALYZING IMAGE---")
    image_url = state['product_info']['image_url']
    msg = vision_llm.invoke(
        [HumanMessage(content=[
            {"type": "text", "text": "Analyze this product image for an ad. Describe the mood, tone, and key elements."},
            {"type": "image_url", "image_url": {"url": image_url}},
        ])]
    )
    analysis = msg.content
    print(f"Image Analysis Complete.")
    return {"image_analysis": analysis}

def generate_ad_variants(state: AdCreatorState):
    print("---NODE: GENERATING AD VARIANTS---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert marketing copywriter for a modern, sophisticated non-alcoholic beverage.
        Your target audience avoids alcohol but wants a complex, enjoyable drink.
        Generate 3 distinct ad variants (headline, primary_text, cta) based on the provided info.
        Output a valid JSON object with a single key "variants" which is a list of 3 ad variant objects."""),
        ("human", "Product Info: {product_info}\nImage Analysis: {analysis}")
    ])
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    result = chain.invoke({
        "product_info": state['product_info'],
        "analysis": state['image_analysis']
    })
    print(f"Generated {len(result['variants'])} ad variants.")
    return {"generated_ads": result['variants']}

def save_ads_to_sheet(state: AdCreatorState):
    print("---NODE: SAVING ADS TO GOOGLE SHEET---")
    sheet = gspread_client.open(SHEET_NAME).worksheet("Generated_Ads")
    for ad in state['generated_ads']:
        row = [
            state['product_info']['name'], ad['headline'],
            ad['primary_text'], ad['cta'], "PENDING REVIEW"
        ]
        sheet.append_row(row)
    print("Ads saved to sheet.")
    return {}

workflow = StateGraph(AdCreatorState)
workflow.add_node("fetch_product_data", fetch_product_data)
workflow.add_node("analyze_image", analyze_image)
workflow.add_node("generate_ad_variants", generate_ad_variants)
workflow.add_node("save_ads_to_sheet", save_ads_to_sheet)

workflow.set_entry_point("fetch_product_data")
workflow.add_edge("fetch_product_data", "analyze_image")
workflow.add_edge("analyze_image", "generate_ad_variants")
workflow.add_edge("generate_ad_variants", "save_ads_to_sheet")
workflow.add_edge("save_ads_to_sheet", END)

ad_creator_app = workflow.compile()