"""Testing for the function log, which takes either the string 'header' or an AIP instance
and adds a row to the aip log with the information.

The log is updated after each step in the script.
These tests are for if information is written to a CSV correctly.
They are not testing if the correct information is saved to the log after each step."""

import os
import unittest
from scripts.aip_functions import AIP, log


class MyTestCase(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the log so a new one can be made for the next test.
        """
        os.remove(os.path.join('..', 'aip_log.csv'))

    def test_header(self):
        """
        Test for making the log file with a header.
        """
        log('header')
        with open(os.path.join('..', 'aip_log.csv'), 'r') as file:
            result = file.readlines()
        expected = ['Time Started,AIP ID,Files Deleted,Objects Folder,Metadata Folder,FITS Tool Errors,FITS Combination Errors,Preservation.xml Made,Preservation.xml Valid,Bag Valid,Package Errors,Manifest Errors,Processing Complete\n']
        self.assertEqual(expected, result, 'Problem with header')

    def test_one_aip(self):
        """
        Test for making the log file with information from one AIP.
        To save time, updates some items in the AIP's log variable without running the workflow steps.
        """
        log('header')
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'one-tar-folder', 'one-tar', 'title', 1, to_zip=False)
        aip.log['Deletions'] = 'No files deleted'
        aip.log['ObjectsError'] = 'Objects folder already exists in original files'
        aip.log['Complete'] = 'Error during processing'
        log(aip.log)
        # TODO: the first column is a time stamp, so can't do an exact comparison without removing it.
        # Read as a CSV so easier to edit? Time stamp is YYYY-MM-DD ##:##:##.######
        with open(os.path.join('..', 'aip_log.csv'), 'r') as file:
            result = file.readlines()
        expected = ['Time Started,AIP ID,Files Deleted,Objects Folder,Metadata Folder,FITS Tool Errors,FITS Combination Errors,Preservation.xml Made,Preservation.xml Valid,Bag Valid,Package Errors,Manifest Errors,Processing Complete\n',
                    'Started: time,one-tar,No files deleted,Objects folder already exists in original files,n/a,n/a,n/a,n/a,n/a,n/a,n/a,n/a,Error during processing\n']
        self.assertEqual(expected, result, 'Problem with one aip')


if __name__ == '__main__':
    unittest.main()
