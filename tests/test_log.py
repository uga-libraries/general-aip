"""Testing for the function log, which takes either the string "header" or an AIP instance
and adds a row to the aip log with the information.

These tests are for if information is written to a CSV correctly.
Tests for functions with error handling include testing if the correct information is saved to the log."""

import os
import pandas as pd
import unittest
from aip_functions import AIP, log


def aip_log_list():
    """Reads an aip_log.csv and returns a list of lists (each row), replacing na with text for easier comparison"""
    df = pd.read_csv(os.path.join(os.getcwd(), 'aip_log.csv'))
    df = df.fillna('BLANK')
    row_list = [df.columns.to_list()] + df.values.tolist()
    return row_list


class TestLog(unittest.TestCase):

    def setUp(self):
        """Variable with the header row value, which is used in each test"""
        self.header = ['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                       'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made',
                       'Preservation.xml Valid', 'Bag Valid', 'Package Errors', 'Manifest Errors',
                       'Processing Complete']

    def tearDown(self):
        """Deletes the log, if present"""
        if os.path.exists('aip_log.csv'):
            os.remove('aip_log.csv')

    def test_header(self):
        """Test for making a new log file with a header"""
        # Creates the log.
        log('header', os.getcwd())

        # Test for the log contents.
        result = aip_log_list()
        expected = [self.header]
        self.assertEqual(expected, result, "Problem with header")

    def test_one_aip(self):
        """Test for making a log file with information from one AIP"""
        # Creates the log and ass values for the AIP.
        aips_dir = os.getcwd()
        log('header', aips_dir)
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'aip-folder', 'general', 'aip-1', 'title', 1, to_zip=False)
        aip.log['Deletions'] = 'No files deleted'
        aip.log['ObjectsError'] = 'Objects folder already exists in original files'
        aip.log['Complete'] = 'Error during processing'
        log(aip.log, aips_dir)

        # Test for the log contents.
        result = aip_log_list()
        expected = [self.header,
                    [str(aip.log['Started']), 'aip-1', 'No files deleted',
                     'Objects folder already exists in original files', 'BLANK', 'BLANK', 'BLANK', 'BLANK',
                     'BLANK', 'BLANK', 'BLANK', 'BLANK', 'Error during processing']]
        self.assertEqual(expected, result, "Problem with one aip")

    def test_multiple_aips(self):
        """Test for making the log file with information from two AIPs"""
        # Creates the log and adds values for the first AIP.
        aips_dir = os.getcwd()
        log('header', aips_dir)
        aip1 = AIP(aips_dir, 'dept', None, 'coll-1', 'aip-1-folder', 'general', 'aip-1', 'title-1', 1, to_zip=False)
        aip1.log['Deletions'] = 'No files deleted'
        aip1.log['ObjectsError'] = 'Objects folder already exists in original files'
        aip1.log['Complete'] = 'Error during processing'
        log(aip1.log, aips_dir)

        # Adds values for the second AIP to the log.
        aip2 = AIP(os.getcwd(), 'dept', None, 'coll-1', 'aip-2-folder', 'general', 'aip-2', 'title-2', 1, to_zip=False)
        aip2.log['Deletions'] = 'No files deleted'
        aip2.log['ObjectsError'] = 'Successfully created objects folder'
        aip2.log['MetadataError'] = 'Successfully created metadata folder'
        aip2.log['FITSTool'] = 'No FITS tool errors'
        aip2.log['FITSError'] = 'Successfully created combined-fits.xml'
        aip2.log['PresXML'] = 'Successfully created preservation.xml'
        aip2.log['PresValid'] = 'Preservation.xml valid on 2022-10-31 13:14:15.123456'
        aip2.log['BagValid'] = 'Bag valid on 2022-10-13 14:15:16.789123'
        aip2.log['Package'] = 'Successfully made package'
        aip2.log['Manifest'] = 'Successfully added AIP to manifest.'
        aip2.log['Complete'] = 'Successfully completed processing'
        log(aip2.log, aips_dir)

        # Test for the log contents.
        result = aip_log_list()
        expected = [self.header,
                    [str(aip1.log['Started']), 'aip-1', 'No files deleted',
                     'Objects folder already exists in original files', 'BLANK', 'BLANK', 'BLANK', 'BLANK',
                     'BLANK', 'BLANK', 'BLANK', 'BLANK', 'Error during processing'],
                    [str(aip2.log['Started']), 'aip-2', 'No files deleted', 'Successfully created objects folder',
                     'Successfully created metadata folder', 'No FITS tool errors',
                     'Successfully created combined-fits.xml', 'Successfully created preservation.xml',
                     'Preservation.xml valid on 2022-10-31 13:14:15.123456',
                     'Bag valid on 2022-10-13 14:15:16.789123', 'Successfully made package',
                     'Successfully added AIP to manifest.', 'Successfully completed processing']]
        self.assertEqual(expected, result, "Problem with multiple aips")


if __name__ == "__main__":
    unittest.main()
