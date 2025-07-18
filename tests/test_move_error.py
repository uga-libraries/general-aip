"""Testing for the function move_error, which takes an error name (string) and a path to a folder as input,
makes a folder with the error name if one doesn't already exist, and moves the folder to the error folder."""

import os
import shutil
import unittest
from aip_functions import move_error


def errors_directory_print():
    """
    Makes and returns a list with the filepath for every folder in the aips-with-errors folder.
    The aips-with-errors folder should be in the parent directory of the current directory.
    This is used to compare the move_error function's actual results to the expected results.
    """
    result = []
    for root, dirs, files in os.walk(os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors')):
        for directory in dirs:
            result.append(os.path.join(root, directory))
    return result


class TestMoveError(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the aips-with-errors folder.
        All test AIP folders should be in the error folder at this point and don't need to be deleted separately.
        """
        shutil.rmtree(os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors'))

    def test_no_previous_error(self):
        """
        Test for moving a folder into an error folder when there is no pre-existing aips-with-errors folder.
        Result for testing is a list of paths for every folder in the aips-with-errors folder.
        """
        os.mkdir('aip1')
        move_error('error_type', os.path.join(os.getcwd(), 'aip1'), os.path.join(os.getcwd(), 'aip_staging_location'))

        result = errors_directory_print()

        expected = [os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip1')]

        self.assertEqual(result, expected, "Problem with no previous error")

    def test_previous_error_diff_type(self):
        """
        Test for moving a folder into an error folder when there is a pre-existing aips-with-errors folder
        but there is not a pre-existing error folder of the same error type.
        Result for testing is a list of paths for every folder in the aips-with-errors folder.
        """
        os.makedirs(os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip1'))
        os.mkdir('aip2')
        move_error('error_two', os.path.join(os.getcwd(), 'aip2'), os.path.join(os.getcwd(), 'aip_staging_location'))

        result = errors_directory_print()

        expected = [os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_two'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip1'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_two', 'aip2')]

        self.assertEqual(result, expected, "Problem with previous error, different type")

    def test_previous_error_same_type(self):
        """
        Test for moving a folder into an error folder when there is a pre-existing aips-with-errors folder
        and there is a pre-existing error folder of the same error type.
        Result for testing is a list of paths for every folder in the aips-with-errors folder.
        """
        os.makedirs(os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip1'))
        os.mkdir('aip2')
        move_error('error_type', os.path.join(os.getcwd(), 'aip2'), os.path.join(os.getcwd(), 'aip_staging_location'))

        result = errors_directory_print()

        expected = [os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip1'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip2')]

        self.assertEqual(result, expected, "Problem with previous error, same type")


if __name__ == "__main__":
    unittest.main()
