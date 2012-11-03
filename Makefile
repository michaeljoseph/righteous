test:
	rm -rf .coverage htmlcov
	python setup.py test 

pep8:
	pip install pep8==1.3.3
	pep8 setup.py righteous tests > pep8.report

pyflakes:
	pip install pyflakes==0.5.0
	pyflakes docs righteous tests setup.py > pyflakes.report 

ci: test pep8 pyflakes
	
documentation:
	pip install Sphinx==1.1.3
	cd docs; make html
