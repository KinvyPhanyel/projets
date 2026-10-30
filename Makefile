.PHONY: check serve examples

check:
	python3 automation/check_portfolio.py

serve:
	python3 automation/serve_lab.py

examples:
	python3 automation/check_portfolio.py --output site/demo-results.json --export-examples
