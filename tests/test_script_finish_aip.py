import os
import pandas as pd
import shutil
import subprocess
import unittest


def file_to_list(file_path):
    """Return a list with the zips in the manifest.txt for comparing to expected results
    Can't test the entire thing because the updated MD5 is different each time
    """
    df = pd.read_csv(file_path, delimiter='  ', header=None, names=['MD5', 'Zip_Path'])
    zip_list = df['Zip_Path'].values.tolist()
    return zip_list


class MyTestCase(unittest.TestCase):

    def tearDown(self):
        """Deletes the copy of files used for testing and new or updated manifest.txt"""
        test_data = os.path.join(os.getcwd(), 'script_finish_aip', 'aip_dir')
        if os.path.exists(test_data):
            shutil.rmtree(test_data)

    def test_has_manifest(self):
        """Test for when the completed AIP is added to an existing manifest.txt"""
        # Makes a copy of the test data, since it is altered by the function.
        test_data = os.path.join(os.getcwd(), 'script_finish_aip', 'aip_dir')
        shutil.copytree(os.path.join(os.getcwd(), 'script_finish_aip', 'has_manifest'), test_data)

        # Makes variables for arguments and runs the script.
        script_path = os.path.join('..', 'finish_aip.py')
        bag_path = os.path.join(test_data, 'test-999-er-111111_bag')
        subprocess.run(f'python {script_path} {bag_path}', shell=True)

        # Verifies the contents of manifest.txt
        result = file_to_list(os.path.join(test_data, 'manifest.txt'))
        expected = ['test-888-er-111111_bag.1502225.tar.bz2', 'test-999-er-111111_bag.9549.tar.bz2']
        self.assertEqual(result, expected, "Problem with test for has_manifest")

    def test_no_manifest(self):
        """Test for when a new manifest.txt is made for the completed AIP"""
        # Makes a copy of the test data, since it is altered by the function.
        test_data = os.path.join(os.getcwd(), 'script_finish_aip', 'aip_dir')
        shutil.copytree(os.path.join(os.getcwd(), 'script_finish_aip', 'no_manifest'), test_data)

        # Makes variables for arguments and runs the script.
        script_path = os.path.join('..', 'finish_aip.py')
        bag_path = os.path.join(test_data, 'test-999-er-111111_bag')
        subprocess.run(f'python {script_path} {bag_path}', shell=True)

        # Verifies the contents of manifest.txt
        result = file_to_list(os.path.join(test_data, 'manifest.txt'))
        expected = ['test-999-er-111111_bag.9549.tar.bz2']
        self.assertEqual(result, expected, "Problem with test for no_manifest")


if __name__ == '__main__':
    unittest.main()
