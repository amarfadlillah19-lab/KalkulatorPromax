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
        res = a ** b
        formula = f"{a} ^ {b}"
        steps = [f"Langkah 1: Ambil nilai A = {a}", f"Langkah 2: Ambil nilai B = {b} (pangkat)", f"Langkah 3: {a} ^ {b} = {res}"]
    elif op == "sqrt":
        if a < 0: raise ValueError("Akar negatif tidak valid!")
        res = math.sqrt(a)
        formula = f"√{a}"
        steps = [f"Langkah 1: Ambil nilai A = {a}", f"Langkah 2: Hitung akar kuadrat dari {a}", f"Langkah 3: √{a} = {res}"]
    elif op == "mod":
        res = a % b
        formula = f"{a} mod {b}"
        steps = [f"Langkah 1: Ambil nilai A = {a}", f"Langkah 2: Ambil nilai B = {b}", f"Langkah 3: {a} % {b} = {res}"]
    elif op == "floor":
        if b == 0: raise ValueError("Floor division oleh nol!")
        res = a // b
        formula = f"{a} // {b}"
        steps = [f"Langkah 1: Ambil nilai A = {a}", f"Langkah 2: Ambil nilai B = {b}", f"Langkah 3: floor({a} / {b}) = {res}"]
    else:
        raise ValueError("Operator aritmatika tidak dikenal")

    return round(res, 6) if isinstance(res, float) else res, formula, steps

def calc_logika(op, data):
    a = data.get("a", "")
    b = data.get("b", "")

    # Coba parse sebagai boolean atau integer
    def parse_logic(val):
        if isinstance(val, bool): return val
        if isinstance(val, str):
            if val.lower() in ("true", "1", "yes", "on"): return True
            if val.lower() in ("false", "0", "no", "off", ""): return False
        try:
            return int(val)
        except:
            return bool(val)

    val_a = parse_logic(a)
    val_b = parse_logic(b) if b != "" else None

    # Jika integer dan bukan boolean string, lakukan bitwise
    use_bitwise = isinstance(val_a, int) and not isinstance(a, bool) and a not in ("true", "false", "True", "False")

    if use_bitwise and val_b is not None and isinstance(val_b, int) and not isinstance(b, bool):
        if op == "AND": res = val_a & val_b; formula = f"{val_a} & {val_b}"
        elif op == "OR": res = val_a | val_b; formula = f"{val_a} | {val_b}"
        elif op == "XOR": res = val_a ^ val_b; formula = f"{val_a} ^ {val_b}"
        elif op == "NAND": res = ~(val_a & val_b); formula = f"~({val_a} & {val_b})"
        elif op == "NOR": res = ~(val_a | val_b); formula = f"~({val_a} | {val_b})"
        elif op == "NOT": res = ~val_a; formula = f"~{val_a}"
        else: raise ValueError("Operator logika tidak dikenal")
        steps = [f"Langkah 1: Konversi A = {a} → {val_a} (integer)", f"Langkah 2: Konversi B = {b} → {val_b} (integer)" if val_b is not None else f"Langkah 2: Hanya gunakan A = {val_a}", f"Langkah 3: {formula} = {res}"]
    else:
        # Boolean logic
        if op == "AND":
            if val_b is None: raise ValueError("AND memerlukan 2 input")
            res = val_a and val_b; formula = f"{val_a} AND {val_b}"
        elif op == "OR":
            if val_b is None: raise ValueError("OR memerlukan 2 input")
            res = val_a or val_b; formula = f"{val_a} OR {val_b}"
        elif op == "XOR":
            if val_b is None: raise ValueError("XOR memerlukan 2 input")
            res = bool(val_a) ^ bool(val_b); formula = f"{bool(val_a)} XOR {bool(val_b)}"
        elif op == "NAND":
            if val_b is None: raise ValueError("NAND memerlukan 2 input")
            res = not (val_a and val_b); formula = f"NOT ({val_a} AND {val_b})"
        elif op == "NOR":
            if val_b is None: raise ValueError("NOR memerlukan 2 input")
            res = not (val_a or val_b); formula = f"NOT ({val_a} OR {val_b})"
        elif op == "NOT":
            res = not val_a; formula = f"NOT {val_a}"
        else:
            raise ValueError("Operator logika tidak dikenal")
        steps = [f"Langkah 1: Konversi A = {a} → {bool(val_a)} (boolean)", f"Langkah 2: Konversi B = {b} → {bool(val_b)} (boolean)" if val_b is not None else f"Langkah 2: Hanya gunakan A = {bool(val_a)}", f"Langkah 3: {formula} = {res}"]