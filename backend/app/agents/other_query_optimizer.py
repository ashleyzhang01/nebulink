from uagents import Agent, Context, Model
import requests
import os


class Message(Model):
    query: str
    return_address: str
    message_id: str

other_query_optimizer_agent = Agent(name="other_optimizer", port=8004, seed="other seed", endpoint=["http://localhost:8004/submit"])

@other_query_optimizer_agent.on_message(model=Message)
async def handle_other_query(ctx: Context, sender: str, msg: Message):
    system_message = """
    Given a user query, your role is to optimize it to query into a vector database of embeddings. 
    The user is looking for someone who has some kind of speciality, so you should use keywords that will best optimize for querying over a company descriptions and github repos. 

    For example, the user may ask "who is working in ai interpretability", you would optimize that to be "ai interpretability sparse autoencoders llm features representation probing"

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


def handle_other_query_func(query: str):
    system_message = """
    Given a user query, your role is to optimize it to query into a vector database of embeddings. 
    The user is looking for someone who has some kind of speciality, so you should use keywords that will best optimize for querying over a company descriptions and github repos. 

    For example, the user may ask "who is working in ai interpretability", you would optimize that to be "ai interpretability sparse autoencoders llm features representation probing"

    Simply output the optimized query without any additional text so your response can be directly used to query into the vector database.
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