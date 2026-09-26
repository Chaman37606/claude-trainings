# Code Formatter

Format and lint Python code in the project.

## Format with Black
```bash
pip install black -q && black . --exclude '__pycache__|\.venv' && echo "✓ Code formatted with Black"
```

## Check with Flake8
```bash
pip install flake8 -q && flake8 . --exclude '__pycache__,.venv' --max-line-length=100 || true
```

## Format with Autopep8
```bash
pip install autopep8 -q && autopep8 --in-place --aggressive --aggressive -r . && echo "✓ Code formatted with autopep8"
```

## Check with Pylint
```bash
pip install pylint -q && pylint **/*.py --disable=C0111,R0903 | head -50 || true
```

## Format Python Files
```bash
python -m py_compile *.py && echo "✓ All Python files compiled successfully"
```

## Sort Imports
```bash
pip install isort -q && isort . && echo "✓ Imports sorted"
```

## Full Cleanup (Black + isort)
```bash
pip install black isort -q && isort . && black . --exclude '__pycache__|\.venv' && echo "✓ Full code cleanup completed"
```
