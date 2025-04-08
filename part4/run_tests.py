import unittest
from tests.test_place import TestPlace

if __name__ == '__main__':
    # Create a test suite containing the TestPlace class
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPlace)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)