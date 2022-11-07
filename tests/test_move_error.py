"""Testing for the function move_error, which takes an error name (string) and a path to a folder as input,
makes a folder with the error name if one doesn't already exist, and moves the folder to the error folder."""

import os
import shutil
import unittest
from scripts.aip_functions import move_error


class TestMoveError(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the error folder for a clean start to the next test.
        All AIP folders should be in the error folder at this point and don't need to be deleted separately.
        """
        shutil.rmtree(os.path.join('..', 'errors'))

    def test_no_previous_error(self):
        """
        Test for moving a folder into an error folder when there is no pre-existing errors folder.
        """
        self.assertEqual(True, False)

    def test_previous_error_diff_type(self):
        """
        Test for moving a folder into an error folder when there is a pre-existing errors folder
        but there is not a pre-existing error folder of the same error type.
        """
        self.assertEqual(True, False)

    def test_previous_error_same_type(self):
        """
        Test for moving a folder into an error folder when there is a pre-existing errors folder
        and there is a pre-existing error folder of the same error type.
        """
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
