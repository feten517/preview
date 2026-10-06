from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

import random
import string
from pydantic import BaseModel, field_validator

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
url_db = {}

class URLRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, value):
        if not (value.startswith("http://") or value.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return value   

def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

@app.get("/")
def read_root():
    return {"message": "Snip is alive"}

@app.post("/shorten")
def shorten_url(request: URLRequest):
    code = generate_code()
    url_db[code] = request.url
    return {"short_code": code, "short_url": f"http://127.0.0.1:8000/{code}"}

@app.get("/{code}")
def redirect_to_url(code: str):
    if code in url_db:
        original_url = url_db[code]
        return RedirectResponse(url=original_url)
    return {"error": "Short code not found"}