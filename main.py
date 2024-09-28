import contract, flask
from flask import Flask

app=Flask(__name__)

@app.get("/")
def main():
    return ""

app.run(host="127.0.0.1", port=7777)