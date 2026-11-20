# Lab 7 – Fuzzing for Input Validation Bugs

Repo assigned: `L6_L7_53_bike_share_rental` (LAB7)

- `bike_share_rental_parser.py` – fixed module: all three functions return `None` for invalid input instead of crashing
- `test_bike_share_rental_parser.py` – Hypothesis fuzz test for each function
- `PES1UG24CS143_DeepakB_LAB7.pdf` – screenshots SS1–SS4 and reflection answers
- `SS1.png` … `SS4.png` – screenshots

```bash
pip install hypothesis pytest
python bike_share_rental_parser.py
pytest test_bike_share_rental_parser.py
```

Hypothesis found 8 crashing inputs in the original module (`''`, `':'`, `','`, `None`, …).
