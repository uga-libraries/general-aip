"""Testing for the function make_output_directories, which creates three directories in the current directory.
It does not have any inputs and returns nothing."""

import os
import unittest
from scripts.aip_functions import make_output_directories


class TestMakeOutputDirectories(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the three script output folders.
        """
        os.rmdir(os.path.join('..', 'aips-to-ingest'))
        os.rmdir(os.path.join('..', 'fits-xml'))
        os.rmdir(os.path.join('..', 'preservation-xml'))

    def test(self):
        """
        Test for running the function.
        Result for testing is a list of new folders in the parent directory of the current directory.
        """
        # Saves a list of what is in the parent directory before and after the function
        # to use for calculating the result of the function.
        parent_directory_before = os.listdir('..')
        make_output_directories()
        parent_directory_after = os.listdir('..')

        # Calculates the difference between the two directory prints and sorts so the values are predictable.
        result = list(set(parent_directory_after) - set(parent_directory_before))
        result.sort()

        expected = ['aips-to-ingest', 'fits-xml', 'preservation-xml']

        self.assertEqual(result, expected, 'Problem with make_output_directories')


if __name__ == '__main__':
    unittest.main()
