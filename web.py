import os
from flask import Flask
from datetime import datetime


app = Flask(__name__)


@app.get("/")
def index():
return "ok"


@app.get("/health")
def health():
return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}


def run_web():
port = int(os.getenv("PORT", "10000"))
app.run(host="0.0.0.0", port=port)