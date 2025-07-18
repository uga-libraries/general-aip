"""Testing for the function move_error, which moves an AIP to an error folder."""

import os
import shutil
import unittest
from aip_functions import move_error


def errors_directory_print():
    """Makes and returns a list with the filepath for every folder in the aips-with-errors folder"""
    result = []
    for root, dirs, files in os.walk(os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors')):
        for directory in dirs:
            result.append(os.path.join(root, directory))
    return result


class TestMoveError(unittest.TestCase):

    def tearDown(self):
        """Deletes the aips-with-errors folder, which contains all test AIPs"""
        shutil.rmtree(os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors'))

    def test_no_previous_error(self):
        """Test for moving a folder into an error folder when there is no pre-existing aips-with-errors folder"""
        # Makes test input and runs the function.
        os.mkdir('aip1')
        move_error('error_type', os.path.join(os.getcwd(), 'aip1'), os.path.join(os.getcwd(), 'aip_staging_location'))

        # Tests that the aips-with-errors folder contains the expected error folder and AIP folder.
        result = errors_directory_print()
        expected = [os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip1')]
        self.assertEqual(result, expected, "Problem with no previous error")

    def test_previous_error_diff_type(self):
        """Test for moving a folder into an error folder when there is a pre-existing aips-with-errors folder
        but there is not a pre-existing error folder for the error type"""
        # Makes test input and runs the function.
        os.makedirs(os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip1'))
        os.mkdir('aip2')
        move_error('error_two', os.path.join(os.getcwd(), 'aip2'), os.path.join(os.getcwd(), 'aip_staging_location'))

        # Tests that the aips-with-errors folder contains the expected error folders and AIP folders.
        result = errors_directory_print()
        expected = [os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_two'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip1'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_two', 'aip2')]
        self.assertEqual(result, expected, "Problem with previous error, different type")

    def test_previous_error_same_type(self):
        """Test for moving a folder into an error folder when there is a pre-existing aips-with-errors folder
        and there is a pre-existing error folder for the error type"""
        # Makes test input and runs the function.
        os.makedirs(os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip1'))
        os.mkdir('aip2')
        move_error('error_type', os.path.join(os.getcwd(), 'aip2'), os.path.join(os.getcwd(), 'aip_staging_location'))

        # Tests that the aips-with-errors folder contains the expected error folder and AIP folders.
        result = errors_directory_print()
        expected = [os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip1'),
                    os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'error_type', 'aip2')]
        self.assertEqual(result, expected, "Problem with previous error, same type")


if __name__ == "__main__":
    unittest.main()
