from uagents import Agent, Bureau, Context, Model
import requests
import os


class Message(Model):
    query: str
    return_address: str
    message_id: str

company_query_optimizer_agent = Agent(
    name="company_optimizer", 
    port=8003,
    seed="company seed", 
    endpoint=["http://localhost:8003/submit"],
)

@company_query_optimizer_agent.on_message(model=Message)
async def handle_company_query(ctx: Context, sender: str, msg: Message):
    system_message = """
    Given a user query, your role is to optimize it to query into a vector database of embeddings. 
    The user is looking for a company or companies in a specific area, so you should use keywords that will best optimize for querying over a company's description (includes company name, industries, specialities, etc.). 
    If the user includes a specific company's name, make sure to include that name and additional keywords. If the user only mentions the area of the company they are looking for, just include keywords that may be the most relevant.

    For example, the user may ask "who is working at groq", you would optimize that to be "groq fast LLM inference LPU"

    Another example is: the user may ask "who is working at a biotech startup", you would optimize that to be "biotech protein ai modeling therapeutics"

    Simply output the optimized query without any additional text so your response can be directly used to query into the vector database.
    """

    query = msg.query
    return_address = msg.return_address
    message_id = msg.message_id

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
        "model": "meta-llama/Meta-Llama-3-70B-Instruct",
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
    } 

    response = requests.post(url, headers=headers, json=data)
    ctx.logger.info(response)
    optimized_query = response.json()['choices'][0]['message']['content']
    await ctx.send(
        return_address,
        Message(query=optimized_query, message_id=message_id)
    )
    ctx.logger.info(f"optimized query: {optimized_query}")