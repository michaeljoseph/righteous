import six

unittest = None
if six.PY3:
    import unittest
    unittest = unittest
else:
    import unittest2
    unittest = unittest2
