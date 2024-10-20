from app.models.linkedin_organization import LinkedinOrganization
from app.schemas.linkedin_organization import LinkedinOrganization as LinkedinOrganizationSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
from typing import Dict, List
from app.utils.github_scraper import GithubScraper
from app.schemas.message import GeneralMessageSchema
import requests
import os

router = APIRouter(prefix="/network", tags=["network"])

def check_for_hallucination(message: str, connection_info: str, common_link: str) -> bool:
    system_message = """
    You are an AI tasked with detecting hallucinations in generated messages. 
    Analyze the given message and determine if it contains any information not present in or not inferable from the provided connection information or common link.
    Respond with 'HALLUCINATION' if you detect any fabricated or unsupported information, otherwise respond with 'NO HALLUCINATION'.
    """

    user_message = f"Message: {message}\nConnection Info: {connection_info}\nCommon Link: {common_link}"

    url = "https://api.hyperbolic.xyz/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.getenv("HYPERBOLIC_API_KEY")
    }
    data = {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "model": "meta-llama/Meta-Llama-3-70B-Instruct",
        "max_tokens": 10,
        "temperature": 0.1
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()['choices'][0]['message']['content'].strip().upper()
    
    return result == "HALLUCINATION"

@router.get("/message", response_model=GeneralMessageSchema)
async def draft_message(
    query: str,
    connection_info: str,
    common_with_connection:str
): 
    system_message = """
    Given what kind of person the user is looking for (user query), your job is to craft a personalized message to a specific person based on a common link with that person.

    Carefully consider the connection's personal information and the user's common link with that connection. Do not use information that you are not given regarding their common link or personal connection.

    Keep this message relatively short under 200 words but make sure to emphasize all the key points.

    Simply output the message so I can directly take your entire response and send it to the person.
    """

    user_message = f"user query: {query}, connection's information: {connection_info}, common link with connection: {common_with_connection}"

    url = "https://api.hyperbolic.xyz/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.getenv("HYPERBOLIC_API_KEY")
    }
    data = {
        "messages": [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "model": "meta-llama/Meta-Llama-3-70B-Instruct",
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
    } 

    for attempt in range(3):
        response = requests.post(url, headers=headers, json=data)
        message = response.json()['choices'][0]['message']['content']
        
        if not check_for_hallucination(message, connection_info, common_with_connection):
            return message
        
        print(f"Hallucination detected, attempt {attempt + 1}/{3}")

    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']