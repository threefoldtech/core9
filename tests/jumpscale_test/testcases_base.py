import time, signal, logging
from datetime import timedelta
from unittest import TestCase
from nose.tools import TimeExpired


class TestcasesBase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lg = self.log()

    def setUp(self):
        self._testID = self._testMethodName
        self._startTime = time.time()

        def timeout_handler(signum, frame):
            raise TimeExpired('Timeout expired before end of test %s' % self._testID)

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(540)

    def tearDown(self):
        pass

    def log(self):
        logger = logging.getLogger('JumpScale')
        if not logger.handlers:
            fileHandler = logging.FileHandler('test_suite.log', mode='w')
            formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)
        return logger

