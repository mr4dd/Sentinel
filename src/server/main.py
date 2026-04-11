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
    content: list[str] | str | None

class DashBoardMetrics():
    def __init__(self):
        self.backlog = []

    def push(self, data: dict):
        print(data.get("client_id"))
        self.backlog.append(data)

    def get(self, client_id: str):
        data = []
        for i, elem in enumerate(self.backlog):
            if elem.get("client_id") == client_id:
                data.append(elem)
                self.backlog.pop(i)
        return data 

dash = DashBoardMetrics()

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
        dash.push({"client_id": log.client_id, "data_type": "logs", "content":log.content})
    except Exception as e:
        return {"status": "error", "code": e.__str__()}

    return {"status": "ok"}

@app.post("/stats")
async def upload_log(log: ClientMetrics):
    try:
        dbm.insertData("stats", log.content, log.client_id)
        dash.push({"client_id": log.client_id, "data_type": "stats", "content":log.content})
    except Exception as e:
        return {"status": "error", "code": e.__str__()}
    return {"status": "ok"}

@app.post("/network")
async def upload_log(log: ClientMetrics):
    try:
        dbm.insertData("pcap", log.content, log.client_id)
        dash.push({"client_id": log.client_id, "data_type": "pcap", "content":log.content})

    except Exception as e:
        return {"status": "error", "code": e.__str__()}
    
    return {"status": "ok"}

@app.post("/info")
async def get_info(clientmetrics: ClientMetrics):
    data = []
    try:
        data.append(dash.get("57b13204-35b1-11f1-8334-98af65699367"))
    except Exception as e:
        return {"status":"error", "code":e.__str__()}

    return {"status":"ok", "data": data}

if __name__ == "__main__":
    uvicorn.run(app)
