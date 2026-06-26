FILE = "./maps/challenger/01_the_impossible_dream.txt"

run:
	python3 app.py $(FILE)


lint:	
	python3 -m flake8
	python3 -m mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	python3 -m flake8
	python3 -m mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --strict .