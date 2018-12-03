"""
Base unittest class
"""

import unittest
import sys

class BaseTestCase(unittest.TestCase):
    """
    Base testcase
    """
    def tearDown(self):
        """
        TearDown
        """
        # clean up all the imported modules from jumpscale (we know that its not clean and it does not clean up all the refences)
        for module in sorted([item for item in sys.modules.keys() if 'Jumpscale' in item], reverse=True):
            del sys.modules[module]