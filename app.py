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
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    category = data.get("category")
    operation = data.get("operation")

    try:
        if category == "aritmatika":
            result, formula, steps = calc_aritmatika(operation, data)
        elif category == "logika":
            result, formula, steps = calc_logika(operation, data)
        elif category == "basis":
            result, formula, steps = calc_basis(operation, data)
        elif category == "suhu":
            result, formula, steps = calc_suhu(operation, data)
        elif category == "kurs":
            result, formula, steps = calc_kurs(operation, data)
        elif category == "bonus":
            result, formula, steps = calc_bonus(operation, data)
        else:
            return jsonify({"error": "Kategori tidak dikenal"}), 400

        entry = {
            "category": category,
            "operation": operation,
            "formula": formula,
            "result": result,
            "steps": steps
        }
        add_history(entry)

        return jsonify({
            "result": result,
            "formula": formula,
            "steps": steps,
            "history": get_history()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/history", methods=["GET"])
def get_hist():
    return jsonify({"history": get_history()})

@app.route("/clear-history", methods=["POST"])
def clear_history():
    session["history"] = []
    session.modified = True
    return jsonify({"success": True})

def calc_aritmatika(op, data):
    a = float(data.get("a", 0))
    b = float(data.get("b", 0))

    if op == "+":
        res = a + b
        formula = f"{a} + {b}"
        steps = [f"Langkah 1: Ambil nilai A = {a}", f"Langkah 2: Ambil nilai B = {b}", f"Langkah 3: {a} + {b} = {res}"]
    elif op == "-":
        res = a - b
        formula = f"{a} - {b}"
        steps = [f"Langkah 1: Ambil nilai A = {a}", f"Langkah 2: Ambil nilai B = {b}", f"Langkah 3: {a} - {b} = {res}"]
    elif op == "*":
        res = a * b
        formula = f"{a} × {b}"
        steps = [f"Langkah 1: Ambil nilai A = {a}", f"Langkah 2: Ambil nilai B = {b}", f"Langkah 3: {a} × {b} = {res}"]
    elif op == "/":
        if b == 0: raise ValueError("Pembagian oleh nol!")
        res = a / b
        formula = f"{a} ÷ {b}"
        steps = [f"Langkah 1: Ambil nilai A = {a}", f"Langkah 2: Ambil nilai B = {b}", f"Langkah 3: {a} ÷ {b} = {res}"]
    elif op == "^":