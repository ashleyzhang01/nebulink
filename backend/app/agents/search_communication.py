from classifier import classifier_agent
from uagents import Agent, Bureau, Context, Model
import asyncio
import uuid

class QueryRequest(Model):
    query: str

class QueryResponse(Model):
    optimized_query: str

class Message(Model):
    query: str
    return_address: str
    message_id: str

main_agent = Agent(name="main_agent", port=8010, seed="main seed", endpoint=["http://localhost:8010/submit"])

bureau = Bureau()
bureau.add(main_agent)
bureau.add(classifier_agent)

@main_agent.on_rest_post("/optimize_query", QueryRequest, QueryResponse)
async def optimize_query_endpoint(ctx: Context, req: QueryRequest) -> QueryResponse:
    query = req.query

    loop = asyncio.get_event_loop()
    future = loop.create_future()

    message_id = str(uuid.uuid4())

    if not hasattr(main_agent, 'futures'):
        main_agent.futures = {}
    main_agent.futures[message_id] = future

    ctx.logger.info(query)

    await ctx.send(
        classifier_agent.address,
        Message(query=query, return_address=main_agent.address, message_id=message_id)
    )

    optimized_query = await future

    return QueryResponse(optimized_query=optimized_query)

@main_agent.on_rest_get("/test", QueryResponse)
async def handle_test(ctx: Context) -> QueryResponse:
    return "test"

@main_agent.on_message(model=Message)
async def handle_response(ctx: Context, sender: str, msg: Message):
    message_id = msg.message_id
    optimized_query = msg.query

    if hasattr(main_agent, 'futures') and message_id in main_agent.futures:
        future = main_agent.futures.pop(message_id)
        future.set_result(optimized_query)
    else:
        ctx.logger.error(f"Received response with unknown message_id: {message_id}")

if __name__ == "__main__":
    main_agent.run()
