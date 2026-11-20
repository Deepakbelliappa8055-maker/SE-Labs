# Lab 6 – Code and Branch Coverage: Bike Share Rental

Repo assigned: `L6_L7_53_bike_share_rental`

```bash
pip install coverage pytest
coverage run -m pytest CodeCoverageTest_bike_share_rental_application.py
coverage report -m
coverage run --branch -m pytest BranchCoverageTest_bike_share_rental_application.py
coverage report -m
```

| Test file | Tests | Result |
|-----------|-------|--------|
| `CodeCoverageTest_bike_share_rental_application.py` | 16 | 100% statement coverage |
| `BranchCoverageTest_bike_share_rental_application.py` | 40 | 100% statement and branch coverage (30/30 branches) |

Terminal output screenshots are in `evidence/`.
