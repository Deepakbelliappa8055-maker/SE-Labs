"""Pharmacy stock and billing manager.

Adds medicines with quantity, price and expiry date, dispenses them, flags
expired and soon-to-expire stock, bills prescriptions, works out dosages,
saves stock to a JSON file and checks a pharmacist login.
"""
import ast
import hashlib
import hmac
import json
import operator
import os
import secrets
from datetime import date, datetime

DATE_FORMAT = "%Y-%m-%d"
STOCK_FILE = "pharmacy.json"

# PBKDF2-SHA256 digest of the pharmacist login; the plain value is not stored.
LOGIN_SALT = bytes.fromhex("6b1f0c3e9a4d27b8c5e1f0a9d3b6c4e2")
LOGIN_DIGEST = (
    "b0d58398a09696980ba9897caa5cd6560c7722b6b972e7ae897ea649ebe7ebbd"
)
LOGIN_ITERATIONS = 100_000

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

medicines = {}


def add_medicine(name, qty=0, price=0.0, expiry="2099-12-31", audit=None):
    """Add qty units of a medicine and return the audit log.

    Raises ValueError for a non-text name, negative quantity or price,
    or a badly formatted expiry date.
    """
    if audit is None:
        audit = []
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"Medicine name must be non-empty text, got {name!r}")
    if not isinstance(qty, int) or qty < 0:
        raise ValueError(f"Quantity must be a whole number >= 0, got {qty!r}")
    if price < 0:
        raise ValueError(f"Price cannot be negative, got {price!r}")
    datetime.strptime(expiry, DATE_FORMAT)

    entry = medicines.setdefault(
        name, {"qty": 0, "price": price, "expiry": expiry}
    )
    entry["qty"] += qty
    audit.append(f"{datetime.now()}: Stocked {qty} units of {name}")
    return audit


def dispense_medicine(name, qty):
    """Dispense qty units; raise KeyError or ValueError if not possible."""
    if name not in medicines:
        raise KeyError(f"{name} is not in stock")
    if qty <= 0:
        raise ValueError("Quantity to dispense must be positive")
    if qty > medicines[name]["qty"]:
        raise ValueError(
            f"Only {medicines[name]['qty']} units of {name} available"
        )
    medicines[name]["qty"] -= qty
    if medicines[name]["qty"] == 0:
        del medicines[name]


def get_quantity(name):
    """Return the units in stock (0 if the medicine is not stocked)."""
    return medicines.get(name, {}).get("qty", 0)


def _expiry_date(name):
    return datetime.strptime(medicines[name]["expiry"], DATE_FORMAT).date()


def is_expired(name):
    """Return True if the medicine's expiry date has passed."""
    return _expiry_date(name) < date.today()


def bill_amount(prescription):
    """Return the total for a list of (medicine, qty) pairs.

    Expired or unknown medicines are refused instead of being billed.
    """
    total = 0.0
    for name, qty in prescription:
        if name not in medicines:
            raise KeyError(f"{name} is not in stock")
        if is_expired(name):
            raise ValueError(f"{name} has expired and cannot be sold")
        total += medicines[name]["price"] * qty
    return round(total, 2)


def _evaluate(node):
    """Evaluate a parsed arithmetic expression made only of numbers."""
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left, right = _evaluate(node.left), _evaluate(node.right)
        return _OPERATORS[type(node.op)](left, right)
    raise ValueError("Dosage formula may only use numbers and + - * /")


def calculate_dosage(formula):
    """Work out a dosage from a doctor's note such as '250 * 2'."""
    return _evaluate(ast.parse(formula, mode="eval"))


def patient_id(name, phone):
    """Return a stable patient identifier."""
    return hashlib.sha256((name + phone).encode()).hexdigest()


def generate_rx_number():
    """Return an unpredictable prescription number."""
    return f"RX-{100000 + secrets.randbelow(900000)}"


def save_stock(path=STOCK_FILE):
    """Save the stock to a JSON file."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(medicines, handle, indent=2)


def load_stock(path=STOCK_FILE):
    """Replace the in-memory stock with the contents of a JSON file."""
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    medicines.clear()
    medicines.update(data)


def print_label(name):
    """Print a dispensing label."""
    print(f"Dispensing label: {name}")


def expiring_soon(days=30):
    """Return medicines that expire within the next `days` days."""
    today = date.today()
    return [
        name for name in medicines
        if 0 <= (_expiry_date(name) - today).days < days
    ]


def pharmacist_login(password):
    """Check a pharmacist password against the stored digest."""
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), LOGIN_SALT, LOGIN_ITERATIONS
    ).hex()
    return hmac.compare_digest(digest, LOGIN_DIGEST)


def print_stock():
    """Print every medicine in stock."""
    print("===== Pharmacy Stock Report =====")
    for name, item in medicines.items():
        print(
            f"{name} -> {item['qty']} units, Rs. {item['price']:.2f}, "
            f"exp {item['expiry']}"
        )


def _try(action, *args):
    """Run a demo step and print the error instead of crashing."""
    try:
        return action(*args)
    except (KeyError, ValueError) as error:
        print(f"Rejected {action.__name__}{args}: {error}")
        return None


def main():
    """Run the built-in demo."""
    add_medicine("Paracetamol 500mg", 200, 1.5, "2027-06-30")
    add_medicine("Amoxicillin 250mg", 40, 6.0, "2026-01-15")
    _try(add_medicine, "Cetirizine 10mg", -10, 2.0, "2027-03-31")
    _try(add_medicine, 404, 25)
    dispense_medicine("Paracetamol 500mg", 30)
    _try(dispense_medicine, "Insulin", 2)
    print("Paracetamol stock:", get_quantity("Paracetamol 500mg"))
    print("Amoxicillin expired?", is_expired("Amoxicillin 250mg"))
    print("Bill (Paracetamol x10):",
          bill_amount([("Paracetamol 500mg", 10)]))
    _try(bill_amount, [("Paracetamol 500mg", 10), ("Amoxicillin 250mg", 5)])
    print("Dosage (mg/day):", calculate_dosage("250 * 2"))
    print("Patient ID:", patient_id("Asha", "9876543210"))
    print("Rx number:", generate_rx_number())
    entered = os.environ.get("PHARMACIST_PASSWORD", "")
    print("Login:", pharmacist_login(entered))
    print_label("Paracetamol 500mg")
    save_stock()
    load_stock()
    print_stock()


if __name__ == "__main__":
    main()
