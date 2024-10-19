from app.models.github_user import GithubUser
from pydantic import BaseModel
from typing import Optional
from uagents import Agent, Context, Model
from app.db.session import SessionLocal
from app.schemas import User as UserSchema, GithubUser as GithubUserSchema, LinkedinUser as LinkedinUserSchema
from app.agents.github_scraper_agent_helper import get_github_user_2_degree_network
import asyncio


github_agent = Agent(
    name="github_scraper",
    port=8001,
    seed="github_scraper_seed",
    endpoint="http://localhost:8001/submit",
)


GITHUB_AGENT_ADDRESS = None


class GithubRequest(Model):
    username: str
    token: Optional[str] = None


class Response(Model):
    text: str


# @github_agent.on_interval(period=24*60*60)
# async def daily_scrape(ctx: Context):
#     ctx.logger.info("Starting daily scrape")
#     try:
#         db = SessionLocal()
#         try:
#             github_users = db.query(GithubUser).all()
#             for github_user in github_users:
#                 get_github_user_2_degree_network(github_user.username, github_user.token, db)
#                 await asyncio.sleep(1)
#             ctx.logger.info("Daily scrape completed successfully")
#         finally:
#             db.close()
#     except Exception as e:
#         ctx.logger.error(f"Error during daily scrape: {str(e)}")


@github_agent.on_event("startup")
async def startup(ctx: Context):
    global GITHUB_AGENT_ADDRESS
    ctx.logger.info(f"Starting up {github_agent.name}")
    ctx.logger.info(f"With address: {github_agent.address}")
    GITHUB_AGENT_ADDRESS = github_agent.address
    ctx.logger.info(f"And wallet address: {github_agent.wallet.address()}")


@github_agent.on_query(model=GithubRequest, replies={Response})
async def query_handler(ctx: Context, sender: str, _query: GithubRequest):
    ctx.logger.info("Query received")
    try:
        db = SessionLocal()
        try:
            if _query.username:
                get_github_user_2_degree_network(_query.username, _query.token, db)
            await ctx.send(sender, Response(text="success"))
        finally:
            db.close()

    except Exception as e:
        ctx.logger.error(f"Error processing query: {str(e)}")
        await ctx.send(sender, Response(text="fail"))
 
if __name__ == "__main__":
    github_agent.run()
