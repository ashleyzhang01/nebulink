from uagents import Agent, Context
from uagents import Model
import os


class Message(Model):
    message: str


Gemini_Address = os.getenv("GEMINI_ADDRESS")

user = Agent(
    name="user",
    port=8000,
    seed="user secret phrase",
    endpoint=["http://localhost:8000/submit"],
)

@user.on_event("startup")
async def agent_address(ctx: Context):
    ctx.logger.info(user.address)
    message = str(input("You:"))
    await ctx.send(Gemini_Address, Message(message=message))


@user.on_message(model=Message)
async def handle_query_response(ctx: Context, sender: str, msg: Message):
    message = str(input("You:"))
    await ctx.send(sender, Message(message=message))