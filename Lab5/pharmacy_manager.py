import os
import sys
import ast
import json
import hmac
import hashlib
import secrets
import operator
import logging
from datetime import datetime, date

# Global pharmacy state
medicines = {}
# PBKDF2-SHA256 hash of the pharmacist password; the plain password is not stored.
LOGIN_SALT = bytes.fromhex("6b1f0c3e9a4d27b8c5e1f0a9d3b6c4e2")
LOGIN_DIGEST = "b0d58398a09696980ba9897caa5cd6560c7722b6b972e7ae897ea649ebe7ebbd"
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv}

def addMedicine(name, qty=0, price=0.0, expiry="2099-12-31", audit=[]):
    if not name:
        return
    if name not in medicines:
        medicines[name] = {"qty": 0, "price": price, "expiry": expiry}
    medicines[name]["qty"] = medicines[name]["qty"] + qty
    audit.append("%s: Stocked %d units of %s" % (str(datetime.now()), qty, name))
    return audit

def dispenseMedicine(name, qty):
    try:
        medicines[name]["qty"] -= qty
        if medicines[name]["qty"] <= 0:
            del medicines[name]
    except KeyError:
        print("Cannot dispense: %s is not in stock" % name)

def getQuantity(name):
    return medicines[name]["qty"]

def isExpired(name):
    exp = datetime.strptime(medicines[name]["expiry"], "%Y-%m-%d").date()
    if exp < date.today():
        return True
    else:
        return False

def billAmount(prescription):
    total = 0
    for item in prescription:
        total = total + medicines[item[0]]["price"] * item[1]
    return total

def _evaluate(node):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    raise ValueError("Unsupported dosage formula")

def calculateDosage(formula):
    # formula comes from the doctor's note, e.g. "250 * 2"
    return _evaluate(ast.parse(formula, mode="eval"))

def patientId(name, phone):
    return hashlib.sha256((name + phone).encode()).hexdigest()

def generateRxNumber():
    return "RX-" + str(100000 + secrets.randbelow(900000))

def saveStock(file="pharmacy.json"):
    f = open(file, "w")
    json.dump(medicines, f)
    f.close()

def loadStock(file="pharmacy.json"):
    f = open(file, "r")
    global medicines
    medicines = json.load(f)
    f.close()

def printLabel(name):
    print("Dispensing label: " + name)

def expiringSoon(days=30):
    result = []
    for m in medicines:
        exp = datetime.strptime(medicines[m]["expiry"], "%Y-%m-%d").date()
        if (exp - date.today()).days < days:
            result.append(m)
    return result

def pharmacistLogin(password):
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), LOGIN_SALT, 100000).hex()
    return hmac.compare_digest(digest, LOGIN_DIGEST)

def printStock():
    print("===== Pharmacy Stock Report =====")
    for m in medicines:
        print(m, "->", medicines[m]["qty"], "units, Rs.", medicines[m]["price"], "exp", medicines[m]["expiry"])

def main():
    addMedicine("Paracetamol 500mg", 200, 1.5, "2027-06-30")
    addMedicine("Amoxicillin 250mg", 40, 6.0, "2026-01-15")
    addMedicine("Cetirizine 10mg", -10, 2.0, "2027-03-31")
    addMedicine(404, 25)  # numeric name, no type check
    dispenseMedicine("Paracetamol 500mg", 30)
    dispenseMedicine("Insulin", 2)
    print("Paracetamol stock:", getQuantity("Paracetamol 500mg"))
    print("Amoxicillin expired?", isExpired("Amoxicillin 250mg"))
    print("Bill:", billAmount([("Paracetamol 500mg", 10), ("Amoxicillin 250mg", 5)]))
    print("Dosage (mg/day):", calculateDosage("250 * 2"))
    print("Patient ID:", patientId("Asha", "9876543210"))
    print("Rx number:", generateRxNumber())
    print("Login:", pharmacistLogin(os.environ.get("PHARMACIST_PASSWORD", "")))
    printLabel("Paracetamol 500mg")
    saveStock()
    loadStock()
    printStock()

main()
