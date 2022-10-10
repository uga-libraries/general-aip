"""Testing for the function make_output_directories, which creates three directories in the current directory.
It does not have any inputs and returns nothing."""

import os
import unittest
from scripts.aip_functions import make_output_directories


class TestMakeOutputDirectories(unittest.TestCase):

    def test(self):
        """
        Test for running the function.
        The result to be tested is the folders in the parent directory of the current directory after the function runs.
        """
        make_output_directories()
        result = []
        parent = os.path.dirname(os.getcwd())
        for item in os.listdir(parent):
            if item in ('aips-to-ingest', 'fits-xml', 'preservation-xml'):
                result.append(item)
        expected = ['aips-to-ingest', 'fits-xml', 'preservation-xml']
        self.assertEqual(result, expected, 'Problem with make_output_directories')
        os.rmdir(os.path.join(parent, 'aips-to-ingest'))
        os.rmdir(os.path.join(parent, 'fits-xml'))
        os.rmdir(os.path.join(parent, 'preservation-xml'))


if __name__ == '__main__':
    unittest.main()