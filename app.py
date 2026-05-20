import os
from flask import Flask, render_template, request, jsonify, session
from functools import reduce
import math

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Rate statis mata uang (per 1 IDR)
CURRENCY_RATES = {
    "USD": 0.000061,
    "EUR": 0.000057,
    "SGD": 0.000082,
    "JPY": 0.0091,
    "GBP": 0.000048,
    "AUD": 0.000093,
    "CNY": 0.00044,
    "MYR": 0.00028,
    "KRW": 0.082,
    "THB": 0.0021
}

def get_history():
    return session.get("history", [])

def add_history(entry):
    history = get_history()
    history.insert(0, entry)
    if len(history) > 50:
        history = history[:50]
    session["history"] = history
    session.modified = True

@app.route("/")
def index():
    session.setdefault("history", [])