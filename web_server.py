from fastapi import FastAPI

app = FastAPI()


@app.get("/api/v1.0/check-status")
async def root():
    return {"Alive": True}
