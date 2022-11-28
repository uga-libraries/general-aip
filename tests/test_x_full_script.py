"""Testing for the entire script.
Currently just tests for if the script works correctly on a batch of 3 folders.
May add tests for correctly stopping processing when errors are encountered.
For now, error handling that is part of other tests is sufficient."""

import datetime
import os
import re
import shutil
import subprocess
import unittest


class MyTestCase(unittest.TestCase):
    def setUp(self):
        """
        Copies a directory of test files, with folders for 3 AIPs, that is in the script repo
        so the original test files remain unchanged for future tests.

        Makes variables for expected values, since they are so long, to simplify code within the test.
        """
        # Make a copy of the test files.
        shutil.copytree('test_files', 'test_current')

        # Expected value for the paths of the files and folders in the test_current directory.
        self.dir_expected = ['test_current\\aips-to-ingest',
                             'test_current\\aip_directory',
                             'test_current\\fits-xml',
                             'test_current\\preservation-xml',
                             'test_current\\aip_log.csv',
                             'test_current\\aips-to-ingest\\manifest_test.txt',
                             'test_current\\aips-to-ingest\\test-001-er-000001_bag.1000.tar.bz2',
                             'test_current\\aips-to-ingest\\test-001-er-000002_bag.1000.tar.bz2',
                             'test_current\\aips-to-ingest\\test-001-er-000003_bag.1000.tar.bz2',
                             'test_current\\aip_directory\\test-001-er-000001_bag',
                             'test_current\\aip_directory\\test-001-er-000002_bag',
                             'test_current\\aip_directory\\test-001-er-000003_bag',
                             'test_current\\aip_directory\\metadata.csv',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\data',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\bag-info.txt',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\bagit.txt',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\manifest-md5.txt',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\manifest-sha256.txt',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\tagmanifest-md5.txt',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\tagmanifest-sha256.txt',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\data\\metadata',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\data\\objects',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\data\\metadata\\Flower2.JPG_fits.xml',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\data\\metadata\\test-001-er-000001_preservation.xml',
                             'test_current\\aip_directory\\test-001-er-000001_bag\\data\\objects\\Flower2.JPG',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\data',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\bag-info.txt',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\bagit.txt',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\manifest-md5.txt',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\manifest-sha256.txt',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\tagmanifest-md5.txt',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\tagmanifest-sha256.txt',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\data\\metadata',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\data\\objects',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\data\\metadata\\New Text Document.txt_fits.xml',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\data\\metadata\\overview-tree.html_fits.xml',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\data\\metadata\\test-001-er-000002_preservation.xml',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\data\\objects\\New Text Document.txt',
                             'test_current\\aip_directory\\test-001-er-000002_bag\\data\\objects\\overview-tree.html',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\data',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\bag-info.txt',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\bagit.txt',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\manifest-md5.txt',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\manifest-sha256.txt',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\tagmanifest-md5.txt',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\tagmanifest-sha256.txt',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\data\\metadata',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\data\\objects',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\data\\metadata\\Test PDF.pdf_fits.xml',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\data\\metadata\\test-001-er-000003_preservation.xml',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\data\\metadata\\Worksheet.csv_fits.xml',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\data\\objects\\Spreadsheet',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\data\\objects\\Test PDF.pdf',
                             'test_current\\aip_directory\\test-001-er-000003_bag\\data\\objects\\Spreadsheet\\Worksheet.csv',
                             'test_current\\fits-xml\\test-001-er-000001_combined-fits.xml',
                             'test_current\\fits-xml\\test-001-er-000002_combined-fits.xml',
                             'test_current\\fits-xml\\test-001-er-000003_combined-fits.xml',
                             'test_current\\preservation-xml\\test-001-er-000001_preservation.xml',
                             'test_current\\preservation-xml\\test-001-er-000002_preservation.xml',
                             'test_current\\preservation-xml\\test-001-er-000003_preservation.xml']

        # Expected value for the aip_log.csv.
        today = datetime.date.today()
        header = 'Time Started,AIP ID,Files Deleted,Objects Folder,Metadata Folder,FITS Tool Errors,FITS Combination ' \
                 'Errors,Preservation.xml Made,Preservation.xml Valid,Bag Valid,Package Errors,Manifest Errors,' \
                 'Processing Complete\n'
        row1 = f'{today},test-001-er-000001,No files deleted,Successfully created objects folder,Successfully ' \
               f'created metadata folder,No FITS tools errors,Successfully created combined-fits.xml,Successfully ' \
               f'created preservation.xml,Preservation.xml valid on {today},Bag valid on {today},Successfully made ' \
               f'package,Successfully added AIP to manifest,Successfully completed processing\n'
        row2 = f'{today},test-001-er-000002,No files deleted,Successfully created objects folder,Successfully created ' \
               f'metadata folder,No FITS tools errors,Successfully created combined-fits.xml,Successfully created ' \
               f'preservation.xml,Preservation.xml valid on {today},Bag valid on {today},Successfully made package,' \
               f'Successfully added AIP to manifest,Successfully completed processing\n'
        row3 = f'{today},test-001-er-000003,No files deleted,Successfully created objects folder,Successfully created ' \
               f'metadata folder,No FITS tools errors,Successfully created combined-fits.xml,Successfully created ' \
               f'preservation.xml,Preservation.xml valid on {today},Bag valid on {today},Successfully made package,' \
               f'Successfully added AIP to manifest,Successfully completed processing\n'
        self.log_expected = [header, row1, row2, row3]

    def tearDown(self):
        """
        Deletes the copy of files used for testing, along with the script outputs for the test.
        """
        shutil.rmtree('test_current')

    def test_script(self):
        """
        Runs the entire script on the test files.
        Results for testing are the contents of the test_current folder and the AIP log.
        """
        # Runs the script.
        script_path = os.path.join('..', 'scripts', 'general_aip.py')
        aip_dir = os.path.join(os.getcwd(), 'test_current', 'aip_directory')
        subprocess.run(f'python {script_path} {aip_dir}', shell=True)

        # First result for testing is the paths of every folder and file in test_current.
        # To allow for an exact comparison, edits the file size in the filename for .tar.bz2 files,
        # which vary each time they are made.
        dir_result = []
        for root, dirs, files in os.walk('test_current'):
            for directory in dirs:
                dir_result.append(os.path.join(root, directory))
            for file in files:
                if root == 'test_current\\aips-to-ingest' and file.endswith('.tar.bz2'):
                    file = re.sub(r'_bag.\d+.', '_bag.1000.', file)
                dir_result.append(os.path.join(root, file))

        # Second result for testing is the contents of the aip_log.csv file.
        # To allow for an exact comparison, removes the time portion of timestamps ( HH:MM:SS.######),
        # which just leaves the date (YYYY-MM-DD).
        with open(os.path.join('test_current', 'aip_log.csv'), 'r') as log:
            log_rows = log.readlines()
        log_result = []
        for row in log_rows:
            new_row = re.sub(r' \d{2}:\d{2}:\d{2}.\d{6}', '', row)
            log_result.append(new_row)

        self.assertEqual(dir_result, self.dir_expected, 'Difference in test_current directory contents.')
        self.assertEqual(log_result, self.log_expected, 'Difference in aip_log.csv')


if __name__ == '__main__':
    unittest.main()
