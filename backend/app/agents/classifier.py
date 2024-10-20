from uagents import Agent, Context, Model
import requests
import os

class Message(Model):
    query: str
    return_address: str
    message_id: str

classifier_agent = Agent(
    name="classifier", 
    port=8002,
    seed="classifier seed", 
    endpoint=["http://localhost:8002/submit"]
)

@classifier_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Starting up {classifier_agent.name}")
    ctx.logger.info(f"With address: {classifier_agent.address}")
    ctx.logger.info(f"And wallet address: {classifier_agent.wallet.address()}")

@classifier_agent.on_message(model=Message)
async def classify_query(ctx: Context, sender: str, msg: Message):
    print("entered classify_query")
    query = msg.query
    return_address = msg.return_address
    message_id = msg.message_id

    ctx.logger.info(f"Classifier received query: {query}")
    system_message = """
    Based on the input, determine if the user is looking for someone who works at a specific company or someone who is skilled/experienced in a certain area. 
    You are simply classifying whether the user is doing a company-first search or something else. 
    You must only output “company” or “other” with no additional text so this can be passed in as a parameter. This is critical.

    If the user is looking for someone who works at a company, their queries will always include a company name or include the word company like so:
    “Who is working at Google”
    “Software engineer at Google”
    "Who is working at a biotech startup"

    Otherwise, their queries do not mention a specific company or request one, and instead they ask for specific skills or projects they worked on like so:
    “Someone who’s good at low level programming”
    “People working on ai interpretability”

    Again, you must only respond with “company” or “other”.

    For example,
    Input: Who is working at Google
    Output: company

    input: Someone who’s good at low level programming
    output: other
    """
    
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
                "content": query
            }
        ],
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
    }
    
    response = requests.post(url, headers=headers, json=data)
    ctx.logger.info(response)
    classification = response.json()['choices'][0]['message']['content']
    ctx.logger.info(f"Classification result: {classification}")



def classify_query_func(query: str):
    system_message = """
    Based on the input, determine if the user is looking for a company or an individual.
    You must only output “company” or "individual" with no additional text so this can be passed in as a parameter. This is critical.

    If the user is looking for a company, their queries will always include a company name or include the word company or a synonym (like startup) like so:
    “Companies in biotech"
    "ai startups"

    If the user is looking for an individual, their queries will ask for the individuals of some kind of speciality:
    “Someone who’s good at low level programming”
    “People working on ai interpretability”

    Again, you must only respond with “company” or "individual".

    For example,
    Input: companies in biotech
    Output: company

    input: Someone who’s good at low level programming
    output: individual

    """
    
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
                "content": query
            }
        ],
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']
