NOSE:=nosetests --all-modules -s --with-coverage --cover-package=cpk

null:

test_unit:

	$(NOSE) tests/unit

test_integration:

	$(NOSE) tests/integration

test_all: test_unit test_integration
