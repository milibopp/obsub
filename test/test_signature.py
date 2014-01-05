'''
Test that the decorator correctly preserves the signature. Currently, this
is only possible for python3.
'''

import sys

try:
    from test.py3.test_signature import *
except ImportError:
    __test__ = False

