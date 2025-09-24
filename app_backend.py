from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI(title = "Living Ledger Backend")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return JSONResponse(content={"filename": file.filename})

@app.get("/")
def read_root():
    return {"message": "Living Ledger Backend is running!"}