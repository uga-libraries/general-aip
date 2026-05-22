import os
import pandas as pd
import shutil
import subprocess
import unittest


def file_to_list(file_path):
    """Return a list with the CSV contents to use for comparing to expected results"""
    df = pd.read_csv(file_path, delimiter='  ', header=None)
    file_list = df.values.tolist()
    return file_list


class MyTestCase(unittest.TestCase):

    # def tearDown(self):
    #     """Deletes the copy of files used for testing and new or updated manifest.txt"""
    #     test_data = os.path.join(os.getcwd(), 'script_finish_aip', 'aip_dir')
    #     if os.path.exists(test_data):
    #         shutil.rmtree(test_data)

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
        # TODO I'm suspecting it may not be the same every time. Maybe number of lines is enough?
        result = file_to_list(os.path.join(test_data, 'manifest.txt'))
        expected = ['md5tbd', 'test-999-er-111111_bag.sizetbd.tar.bz2']
        self.assertEqual(result, expected, "Problem with test for has_manifest")


if __name__ == '__main__':
    unittest.main()
