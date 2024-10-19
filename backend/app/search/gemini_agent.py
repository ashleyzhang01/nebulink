from uagents import Agent, Context
from uagents import Model
import google.generativeai as genai
import os


class Message(Model):
    message: str


Gemini_agent = Agent(
    name="Gemini Agent",
    port=8001,
    seed="Gemini Agent secret phrase",
    endpoint=["http://localhost:8001/submit"],
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = """
Based on the input, determine if the user is looking for someone who works at a specific company or someone who is skilled/experienced in a certain area. You are simply classifying whether the user is doing a company-first search or something else. You must only output “company” or “other” with no additional text so this can be passed in as a parameter. This is critical.

If the user is looking for someone who works at a specific company, their queries will always include a company name like so:
“Who is working at Google”
“Software engineer at Google”

Otherwise, their queries do not mention a specific company name like so:
“Someone who’s good at low level programming”
“People working on ai interpretability”

Again, you must only respond with “company” or “other”.

For example,
Input: Who is working at Google
Output: company

input: Someone who’s good at low level programming
output: other
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

chat = model.start_chat(history=[])

print("Chat session has started. Type 'quit' to exit.")

async def handle_message(user_message):
    try:
        print("entered func")
        response = chat.send_message(user_message)
        print(response)
        full_response_text = response['text']
        print(full_response_text)
    except Exception as e:
        print("error")
        full_response_text = f"Error occurred: {str(e)}"
    
    return "Gemini: " + full_response_text

#fix this call

@Gemini_agent.on_message(model=Message)
async def handle_query_response(ctx: Context, sender: str, msg: Message):
    response_message = await handle_message(msg.message)

    ctx.logger.info(response_message)

    await ctx.send(sender, Message(message=response_message))
