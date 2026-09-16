from fastapi import FastAPI

app = FastAPI(title="Car Computer API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
