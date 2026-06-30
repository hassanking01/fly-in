FILE = "./maps/easy/01_linear_path.txt"
run:
	python3 fly-in.py $(FILE)

install:
	pip install -r requirements.txt


lint:	
	python3 -m flake8 --exclude=.venv
	python3 -m mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	python3 -m flake8
	python3 -m mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --strict .

clean:
	rm -rf __pycache__
	rm -rf .mypy_cache