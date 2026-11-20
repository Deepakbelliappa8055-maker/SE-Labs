# Lab 5 – Issues Found and Fixed

**Name:** Deepak B  **SRN:** PES1UG24CS143  **File:** `pharmacy_manager.py`

Line numbers refer to the original file. High and medium severity first.

| # | Issue | Tool / Code | Type | Severity | Line(s) | Description | Fix Approach |
|---|-------|-------------|------|----------|---------|-------------|--------------|
| 1 | Shell command injection | Bandit B605 | Security | High | 68 | `os.system("echo ... " + name)` runs the medicine name through a shell, so a name like `x; del *` would run a command. | Replaced with `print(f"Dispensing label: {name}")`; no shell is started. |
| 2 | Weak MD5 hash | Bandit B324 | Security | High | 51 | Patient IDs used MD5, which is broken and easy to collide. | Switched to `hashlib.sha256`. |
| 3 | `eval()` on doctor's note | Bandit B307, Pylint W0123 | Security | Medium | 48 | Any Python code in the formula string would be executed. | Parse with `ast` and evaluate only numbers and `+ - * /`; anything else raises `ValueError`. |
| 4 | Unsafe `pickle` load | Bandit B301, B403 | Security | Medium | 3, 57–64 | Loading a pickle file can run arbitrary code if the file is tampered with. | Store stock as JSON with `json.dump` / `json.load`. |
| 5 | Hard-coded password | Bandit B105 | Security | Low | 11, 79 | `DB_PASSWORD = "pharma@123"` sits in plain text in the source. | Store only a salted PBKDF2-SHA256 digest, compare with `hmac.compare_digest`, read the entered password from the `PHARMACIST_PASSWORD` environment variable. |
| 6 | Predictable Rx numbers | Bandit B311 | Security | Low | 54 | `random.randint` is guessable. | Use `secrets.randbelow`. |
| 7 | Errors silently swallowed | Bandit B110, Pylint W0702, Flake8 E722 | Bug | Medium | 23–28 | `except: pass` hides every error, so dispensing an unknown medicine (Insulin) silently does nothing. | Check stock explicitly and raise `KeyError` / `ValueError` with a clear message. |
| 8 | Mutable default argument | Pylint W0102 | Bug | Medium | 13 | `audit=[]` is shared between calls, so the log keeps growing across unrelated calls. | Default to `None` and create a new list inside the function. |
| 9 | Negative stock accepted | Logic (seen in output) | Bug | Medium | 13–20, 94 | Demo stocked Cetirizine with −10 units and the report printed `-10 units`. | Validate quantity (whole number ≥ 0) and price (≥ 0); raise `ValueError` otherwise. |
| 10 | Non-text medicine name accepted | Logic (seen in output) | Bug | Medium | 13, 95 | `addMedicine(404, 25)` created a medicine called `404`. | Require a non-empty string name. |
| 11 | Expired medicine billed | Logic (seen in output) | Bug | Medium | 40–44 | Amoxicillin (expired) was billed at Rs. 30 in the Rs. 45 total. | `bill_amount` refuses expired or unknown medicines. |
| 12 | Over-dispensing | Logic | Bug | Medium | 22–26 | Dispensing more than in stock just deleted the entry. | Raise `ValueError` if the quantity is more than what is available. |
| 13 | Files opened without `with` | Pylint R1732 | Quality | Low | 57, 62 | File handles may be left open if an error occurs. | Use `with open(..., encoding="utf-8")`. |
| 14 | `global` statement | Pylint W0603 | Quality | Low | 63 | `load_stock` rebinds the global dict. | Update the existing dict with `clear()` + `update()`. |
| 15 | Naming, docstrings, redundant if/else | Pylint C0103, C0114, C0116, R1703, R1705, R1710, C0209 | Style | Low | whole file | camelCase names, no docstrings, `if x: return True else: return False`, %-formatting. | snake_case names, module and function docstrings, `return <condition>`, f-strings. |
| 16 | Module runs on import | Pylint/Flake8 E305 | Quality | Low | 108 | `main()` ran whenever the file was imported. | Wrap in `if __name__ == "__main__":`. |
| 17 | Unused imports, spacing, long lines | Flake8 F401, E302, E501 | Style | Low | 2, 6, many | `sys`, `logging` unused; one blank line between functions; lines over 79 chars. | Removed imports, two blank lines between definitions, wrapped long lines. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 4.83 / 10 | **10.00 / 10** |
| Bandit | 8 issues (2 High, 2 Medium, 4 Low) | **No issues identified** |
| Flake8 | 22 warnings | **0 warnings** |
