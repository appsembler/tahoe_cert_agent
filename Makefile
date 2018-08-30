all:
	virtualenv .test-ve -p python2.7
	./.test-ve/bin/pip install -r test_requirements.txt
	./.test-ve/bin/flake8 cert_agent
	cd cert_agent && ../.test-ve/bin/python manage.py check
	cd cert_agent && ../.test-ve/bin/python manage.py test

.PHONY: all
