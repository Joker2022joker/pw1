NOSE?=nosetests
NOSETESTS:=$(NOSE) --all-modules -s --with-coverage --cover-package=cpk

null:

test_unit:

	$(NOSETESTS) tests/unit

test_integration:

	$(NOSETESTS) tests/integration

test_all: test_unit test_integration
