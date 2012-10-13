init:
	python setup.py develop
	pip install -r requirements.txt

test: init
	coverage run --source=righteous,tests/unit -m unittest2 discover -v tests.unit

ci: test
	pep8 setup.py righteous tests > pep8.report
	pyflakes docs righteous tests setup.py > pyflakes.report
	coverage html

documentation:
	cd docs; make html
