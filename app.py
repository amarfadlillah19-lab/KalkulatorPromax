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

    return res, formula, steps

def calc_basis(op, data):
    val = data.get("value", "")

    if op == "dec-to-bin":
        n = int(val)
        res = bin(n)[2:]
        formula = f"Decimal {n} → Binary"
        steps = [f"Langkah 1: Ambil nilai decimal = {n}", f"Langkah 2: Bagi 2 berulang kali dan catat sisa", f"Langkah 3: Hasil = {res}"]
    elif op == "dec-to-oct":
        n = int(val)
        res = oct(n)[2:]
        formula = f"Decimal {n} → Octal"
        steps = [f"Langkah 1: Ambil nilai decimal = {n}", f"Langkah 2: Bagi 8 berulang kali dan catat sisa", f"Langkah 3: Hasil = {res}"]
    elif op == "dec-to-hex":
        n = int(val)
        res = hex(n)[2:].upper()
        formula = f"Decimal {n} → Hexadecimal"
        steps = [f"Langkah 1: Ambil nilai decimal = {n}", f"Langkah 2: Bagi 16 berulang kali dan catat sisa", f"Langkah 3: Hasil = {res}"]
    elif op == "bin-to-dec":
        n = str(val)
        res = int(n, 2)
        formula = f"Binary {n} → Decimal"
        steps = [f"Langkah 1: Ambil nilai binary = {n}", f"Langkah 2: Kalikan setiap bit dengan 2^n", f"Langkah 3: Hasil = {res}"]
    elif op == "oct-to-dec":
        n = str(val)
        res = int(n, 8)
        formula = f"Octal {n} → Decimal"
        steps = [f"Langkah 1: Ambil nilai octal = {n}", f"Langkah 2: Kalikan setiap digit dengan 8^n", f"Langkah 3: Hasil = {res}"]
    elif op == "hex-to-dec":
        n = str(val)
        res = int(n, 16)
        formula = f"Hexadecimal {n} → Decimal"
        steps = [f"Langkah 1: Ambil nilai hex = {n}", f"Langkah 2: Kalikan setiap digit dengan 16^n", f"Langkah 3: Hasil = {res}"]
    elif op == "bin-to-oct":
        n = str(val)
        dec = int(n, 2)
        res = oct(dec)[2:]
        formula = f"Binary {n} → Octal"
        steps = [f"Langkah 1: Binary {n} → Decimal = {dec}", f"Langkah 2: Decimal {dec} → Octal", f"Langkah 3: Hasil = {res}"]
    elif op == "bin-to-hex":
        n = str(val)
        dec = int(n, 2)
        res = hex(dec)[2:].upper()
        formula = f"Binary {n} → Hexadecimal"
        steps = [f"Langkah 1: Binary {n} → Decimal = {dec}", f"Langkah 2: Decimal {dec} → Hex", f"Langkah 3: Hasil = {res}"]
    elif op == "oct-to-bin":
        n = str(val)
        dec = int(n, 8)
        res = bin(dec)[2:]
        formula = f"Octal {n} → Binary"
        steps = [f"Langkah 1: Octal {n} → Decimal = {dec}", f"Langkah 2: Decimal {dec} → Binary", f"Langkah 3: Hasil = {res}"]
    elif op == "hex-to-bin":
        n = str(val)
        dec = int(n, 16)
        res = bin(dec)[2:]
        formula = f"Hexadecimal {n} → Binary"
        steps = [f"Langkah 1: Hex {n} → Decimal = {dec}", f"Langkah 2: Decimal {dec} → Binary", f"Langkah 3: Hasil = {res}"]
    else:
        raise ValueError("Operasi basis tidak dikenal")

    return res, formula, steps

def calc_suhu(op, data):
    val = float(data.get("value", 0))

    if op == "c-to-f":
        res = (val * 9/5) + 32
        formula = f"({val}°C × 9/5) + 32"
        steps = [f"Langkah 1: Ambil suhu Celcius = {val}", f"Langkah 2: {val} × 9/5 = {val*9/5}", f"Langkah 3: {val*9/5} + 32 = {res}°F"]
    elif op == "c-to-k":
        res = val + 273.15
        formula = f"{val}°C + 273.15"
        steps = [f"Langkah 1: Ambil suhu Celcius = {val}", f"Langkah 2: {val} + 273.15 = {res}K"]
    elif op == "c-to-r":
        res = val * 4/5
        formula = f"{val}°C × 4/5"
        steps = [f"Langkah 1: Ambil suhu Celcius = {val}", f"Langkah 2: {val} × 4/5 = {res}°R"]
    elif op == "f-to-c":
        res = (val - 32) * 5/9
        formula = f"({val}°F - 32) × 5/9"
        steps = [f"Langkah 1: Ambil suhu Fahrenheit = {val}", f"Langkah 2: {val} - 32 = {val-32}", f"Langkah 3: {val-32} × 5/9 = {res}°C"]
    elif op == "f-to-k":
        res = (val - 32) * 5/9 + 273.15
        formula = f"({val}°F - 32) × 5/9 + 273.15"
        steps = [f"Langkah 1: Ambil suhu Fahrenheit = {val}", f"Langkah 2: ({val} - 32) × 5/9 = {(val-32)*5/9}", f"Langkah 3: {(val-32)*5/9} + 273.15 = {res}K"]
    elif op == "f-to-r":
        res = (val - 32) * 4/9
        formula = f"({val}°F - 32) × 4/9"
        steps = [f"Langkah 1: Ambil suhu Fahrenheit = {val}", f"Langkah 2: {val} - 32 = {val-32}", f"Langkah 3: {val-32} × 4/9 = {res}°R"]
    elif op == "k-to-c":
        res = val - 273.15
        formula = f"{val}K - 273.15"
        steps = [f"Langkah 1: Ambil suhu Kelvin = {val}", f"Langkah 2: {val} - 273.15 = {res}°C"]
    elif op == "k-to-f":
        res = (val - 273.15) * 9/5 + 32
        formula = f"({val}K - 273.15) × 9/5 + 32"
        steps = [f"Langkah 1: Ambil suhu Kelvin = {val}", f"Langkah 2: {val} - 273.15 = {val-273.15}", f"Langkah 3: {val-273.15} × 9/5 + 32 = {res}°F"]
    elif op == "k-to-r":
        res = (val - 273.15) * 4/5
        formula = f"({val}K - 273.15) × 4/5"
        steps = [f"Langkah 1: Ambil suhu Kelvin = {val}", f"Langkah 2: {val} - 273.15 = {val-273.15}", f"Langkah 3: {val-273.15} × 4/5 = {res}°R"]
    elif op == "r-to-c":
        res = val * 5/4
        formula = f"{val}°R × 5/4"
        steps = [f"Langkah 1: Ambil suhu Reamur = {val}", f"Langkah 2: {val} × 5/4 = {res}°C"]
    elif op == "r-to-f":
        res = val * 9/4 + 32
        formula = f"({val}°R × 9/4) + 32"
        steps = [f"Langkah 1: Ambil suhu Reamur = {val}", f"Langkah 2: {val} × 9/4 = {val*9/4}", f"Langkah 3: {val*9/4} + 32 = {res}°F"]
    elif op == "r-to-k":
        res = val * 5/4 + 273.15
        formula = f"({val}°R × 5/4) + 273.15"
        steps = [f"Langkah 1: Ambil suhu Reamur = {val}", f"Langkah 2: {val} × 5/4 = {val*5/4}", f"Langkah 3: {val*5/4} + 273.15 = {res}K"]
    else:
        raise ValueError("Konversi suhu tidak dikenal")

    return round(res, 4), formula, steps

def calc_kurs(op, data):
    val = float(data.get("value", 0))
    currency = op.replace("idr-to-", "").upper()
    rate = CURRENCY_RATES.get(currency, 0)

    if rate == 0:
        raise ValueError("Mata uang tidak dikenal")

    res = val * rate
    formula = f"{val} IDR × {rate} {currency}/IDR"
    steps = [
        f"Langkah 1: Ambil nilai IDR = Rp {val:,.2f}",
        f"Langkah 2: Rate {currency} = {rate} (statis)",
        f"Langkah 3: {val} × {rate} = {res:.6f} {currency}"
    ]
    return round(res, 6), formula, steps

def calc_bonus(op, data):
    val = int(data.get("value", 0))

    if op == "faktorial":
        if val < 0: raise ValueError("Faktorial negatif tidak valid!")
        if val > 170: raise ValueError("Nilai terlalu besar!")
        res = math.factorial(val)
        formula = f"{val}!"
        steps = [f"Langkah 1: Ambil nilai n = {val}", f"Langkah 2: Hitung {val}! = {' × '.join(str(i) for i in range(1, min(val+1, 11)))}{' × ...' if val > 10 else ''}", f"Langkah 3: Hasil = {res}"]
    elif op == "fibonacci":
        if val < 0: raise ValueError("Fibonacci negatif tidak valid!")
        if val > 10000: raise ValueError("Nilai terlalu besar!")

        def fib(n):
            if n == 0: return 0
            if n == 1: return 1
            a, b = 0, 1
            for _ in range(2, n+1):
                a, b = b, a+b
            return b

        res = fib(val)
        formula = f"F({val})"

        # Buat deret
        deret = []
        a, b = 0, 1
        for i in range(val+1):
            if i == 0: deret.append(0)
            elif i == 1: deret.append(1)
            else:
                a, b = b, a+b
                deret.append(b)

        steps = [
            f"Langkah 1: Ambil nilai n = {val}",
            f"Langkah 2: Deret: {', '.join(str(x) for x in deret[:min(10, len(deret))])}{', ...' if len(deret) > 10 else ''}",
            f"Langkah 3: F({val}) = {res}"
        ]
    else:
        raise ValueError("Operasi bonus tidak dikenal")

    return res, formula, steps

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
