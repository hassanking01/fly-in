FILE = "./maps/easy/01_linear_path.txt"

run:
	python3 fly-in.py $(FILE)


lint:	
	python3 -m flake8
	python3 -m mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	python3 -m flake8
	python3 -m mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --strict .
