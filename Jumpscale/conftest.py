import pytest


def pytest_addoption(parser):
    parser.addoption("--gevent", action="store_true",
                     help="run the tests only in case of that command line (marked with marker @gevent)")


def pytest_runtest_setup(item):
    if 'gevent' in item.keywords and not item.config.getoption("--gevent"):
        pytest.skip("need --gevent option to run this test")
