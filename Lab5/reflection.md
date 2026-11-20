# Lab 5 – Reflection

**Name:** Deepak B  **SRN:** PES1UG24CS143

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the Flake8 style warnings and the simple Bandit swaps: removing unused imports, adding blank lines, and replacing MD5 with SHA-256 or `random` with `secrets`. Each was a one-line change with an obvious answer.

The hardest was `eval()` in `calculateDosage`. Just deleting it would break the feature, and `ast.literal_eval` cannot do arithmetic like `250 * 2`. I had to walk the parsed expression and allow only numbers and `+ - * /`. The hard-coded password also took thought: removing the string was easy, but the login still had to work. I stored a salted PBKDF2 digest and read the entered password from an environment variable.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

Yes. After I replaced the plain password with a hash, Bandit still raised B105 "hardcoded password" because the variable was called `PASSWORD_HASH`. The check matches the word "password" in the name, but a salted digest is not a secret you can log in with. Renaming it to `LOGIN_DIGEST` cleared the warning.

B311 on `random` is also only a real problem here because Rx numbers should be unpredictable. In a game it would be harmless.

### 3. How would you integrate static analysis tools into your actual software development workflow?

I would run Flake8 and Pylint in a pre-commit hook so style problems never reach the repo, and use an editor plugin for instant feedback while typing. In CI (for example GitHub Actions), every pull request would run Pylint with a minimum score (such as 9.5), Flake8 with zero warnings and Bandit failing on any Medium or High issue. Shared config files would keep the rules the same for the whole team, with any `# nosec` or disable comment needing a short reason.

### 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Security:** no shell execution, no `eval`, no pickle loading, no plain-text password. Bandit went from 8 issues (2 High) to none.
- **Robustness:** bad input is now rejected with a clear message instead of corrupting stock. Before, the demo showed `Cetirizine -10 units`, a medicine called `404` and an expired medicine on the bill. Now each of these is refused, and dispensing an unknown medicine is reported instead of silently ignored.
- **Readability:** snake_case names, docstrings, f-strings and `with` blocks make the file easier to follow.
- **Scores:** Pylint went from 4.83 to 10.00/10 and Flake8 from 22 warnings to 0.

The tools did not catch the negative quantity or the expired-medicine billing; I only found those by reading the program's output. Static analysis helps a lot, but it does not replace running and reviewing the code.
