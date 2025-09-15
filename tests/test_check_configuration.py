"""Testing for the function check_configuration, which tests the correctness of configuration.py.

Before running this test, rename the file tests/configuration_tests.py to tests/configuration.py
and after running this test, rename it back.
Otherwise, this configuration.py will be used for the other unit tests, causing all kinds of errors.

Since variables from configuration.py are imported when check_configuration is imported,
we haven't yet figured out how to test on variations of configuration.py.
Instead, this test has at least one of each possible error
and at least one of each variable type (path and not path) that is correct.
"""
import os
import unittest
from aip_functions import check_configuration


class MyTestCase(unittest.TestCase):
    def test_function(self):
        """
        Preliminary test for the function. See note above for details.
        """
        errors_list = check_configuration(os.getcwd())
        expected = ["AIP_STAGING variable is missing from the configuration file.",
                    "INGEST_SERVER variable is missing from the configuration file.",
                    "FITS path 'Z:\\FITS\\fits.bat' is not correct.",
                    f"FITS is not in the same directory as the aips_directory '{os.getcwd()}'.",
                    "SAXON path 'Z:\\Programs\\SaxonHE10-5J\\saxon-he-10.5.jar' is not correct.",
                    "MD5DEEP variable is missing from the configuration file.",
                    "GROUPS variable is missing from the configuration file."]
        self.assertEqual(expected, errors_list, "Problem with test for check_configuration function")


if __name__ == '__main__':
    unittest.main()
