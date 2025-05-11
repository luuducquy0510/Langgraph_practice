from fastapi import FastAPI
from schemas import UserQuery
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agent_configs import stream_response

app = FastAPI()





@app.post("/conversation")
async def conversation(payload: UserQuery):
    """
    Endpoint to handle conversation with the agent.
    """
    async def stream():
        async for chunk in stream_response(payload.query):
            yield chunk
    return StreamingResponse(stream(), media_type="text/plain")




if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app
    uvicorn.run(app, host="127.0.1", port=3030)