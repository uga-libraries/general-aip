"""Testing for the function make_output_directories, which creates three directories in the current directory.
It does not have any inputs and returns nothing."""

import os
import unittest
from scripts.aip_functions import make_output_directories


class TestMakeOutputDirectories(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the three output folders.
        """
        os.rmdir(os.path.join('..', 'aips-to-ingest'))
        os.rmdir(os.path.join('..', 'fits-xml'))
        os.rmdir(os.path.join('..', 'preservation-xml'))

    def test(self):
        """
        Test for running the function.
        The result to be tested is the new folders in the parent directory of the current directory
        after the function runs.
        """
        parent_directory_before = os.listdir('..')
        make_output_directories()
        parent_directory_after = os.listdir('..')
        result = list(set(parent_directory_after) - set(parent_directory_before))
        result.sort()
        expected = ['aips-to-ingest', 'fits-xml', 'preservation-xml']
        self.assertEqual(result, expected, 'Problem with make_output_directories')


if __name__ == '__main__':
    unittest.main()
