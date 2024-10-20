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

@router.get("/message", response_model=GeneralMessageSchema)
async def draft_message(
    query: str,
    connection_info: str,
    common_with_connection:str
): 
    system_message = """
    Given what kind of person the user is looking for (user query), your job is to craft a personalized message to a specific person based on a common link with that person.

    Carefully consider the connection's personal information and the user's common link with that connection.

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

    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']