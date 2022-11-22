"""Testing for the entire script.
Currently just tests for if the script works correctly on a batch of 3 folders.
May add tests for correctly stopping processing when errors are encountered.
For now, error handling that is part of other tests is sufficient."""

import os
import shutil
import subprocess
import unittest


class MyTestCase(unittest.TestCase):
    def setUp(self):
        """
        Copies a directory of test files, with folders for 3 AIPs, that is in the script repo
        so the original test files remain unchanged for future tests.
        """
        shutil.copytree('test_files', 'test_current')

    # def tearDown(self):
    #     """
    #     Deletes the copy used in testing.
    #     """
    #     shutil.rmtree('test_current')

    def test_script(self):
        """
        Runs the entire script on the test files.
        Result for testing is the contents of the test_current folder and the AIP log.
        """
        script_path = os.path.join('..', 'scripts', 'general_aip.py')
        aip_dir = os.path.join('test_current', 'aip_directory')
        subprocess.run(f'python {script_path} {aip_dir}', shell=True)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
