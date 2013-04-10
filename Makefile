NOSE:=nosetests --all-modules

null:

test_unit:

	$(NOSE) tests/unit

test_integration:

	$(NOSE) tests/integration

test_all: test_unit test_integration
