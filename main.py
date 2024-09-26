from flask import request, redirect
from monster import render, tokeniser, parser, Flask
import sys, json

app = Flask(__name__)

@app.get("/")
def home():
    return render("index", locals()|globals())

app.run(host="0.0.0.0", port=int(sys.argv[1]))