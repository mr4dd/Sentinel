import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from util.dbcontroller import database_manager as dbm

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class ClientMetrics(BaseModel):
    client_id: str
    content: list[str] | str

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    message = "Malformed Request Body"
    return PlainTextResponse(message, status_code=400)

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.post("/logs")
async def upload_log(log: ClientMetrics):
    try:
        dbm.insertData("logs", log.content, log.client_id)
    except Exception as e:
        return {"status": "error", "code": e.__str__()}

    return {"status": "ok"}

@app.post("/stats")
async def upload_log(log: ClientMetrics):
    try:
        dbm.insertData("stats", log.content, log.client_id)
    except Exception as e:
        return {"status": "error", "code": e.__str__()}
    return {"status": "ok"}

@app.post("/network")
async def upload_log(log: ClientMetrics):
    try:
        dbm.insertData("pcap", log.content, log.client_id)
    except Exception as e:
        return {"status": "error", "code": e.__str__()}
    
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app)
