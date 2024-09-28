from flask import request, redirect
from monster import render, tokeniser, parser, Flask
import sys, json
import secrets_parser

secrets=secrets_parser.parse("variables.txt")

app = Flask(__name__)

@app.get("/")
def home():
    return render("index", locals()|globals())

app.run(host="127.0.0.1", port=int(sys.argv[1]))