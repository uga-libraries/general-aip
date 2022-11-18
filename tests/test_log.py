"""Testing for the function log, which takes either the string 'header' or an AIP instance
and adds a row to the aip log with the information.

These tests are for if information is written to a CSV correctly.
Tests for functions with error handling include testing if the correct information is saved to the log."""

import os
import unittest
from scripts.aip_functions import AIP, log


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """
        Variable with the header row value, which is used in each test.
        """
        self.header = 'Time Started,AIP ID,Files Deleted,Objects Folder,Metadata Folder,FITS Tool Errors,' \
                      'FITS Combination Errors,Preservation.xml Made,Preservation.xml Valid,Bag Valid,Package Errors,' \
                      'Manifest Errors,Processing Complete\n'

    def tearDown(self):
        """
        Deletes the log so a new one can be made for the next test.
        """
        os.remove(os.path.join('..', 'aip_log.csv'))

    def test_header(self):
        """
        Test for making the log file with a header.
        Result for testing is the content of the log file.
        """
        # Creates the log.
        log('header')

        # Result and expected are lists, with the text of each row as a list item.
        # The test of each row is a comma-separated string combining the values from each column.
        with open(os.path.join('..', 'aip_log.csv'), 'r') as file:
            result = file.readlines()

        expected = [self.header]

        self.assertEqual(expected, result, 'Problem with header')

    def test_one_aip(self):
        """
        Test for making the log file with information from one AIP.
        Result for testing is the content of the log file.
        """
        # Creates the log.
        # To save time, updates some items in the AIP's log variable without running the workflow steps.
        log('header')
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'one-tar-folder', 'one-tar', 'title', 1, to_zip=False)
        aip.log['Deletions'] = 'No files deleted'
        aip.log['ObjectsError'] = 'Objects folder already exists in original files'
        aip.log['Complete'] = 'Error during processing'
        log(aip.log)

        # Result and expected are lists, with the text of each row as a list item.
        # The test of each row is a comma-separated string combining the values from each column.
        with open(os.path.join('..', 'aip_log.csv'), 'r') as file:
            result = file.readlines()

        # Time from the log is used for an exact comparison.
        # Time changes each time the rest is run. The rest of the expected values are the same each time.
        aip_row = f'{str(aip.log["Started"])},one-tar,No files deleted,Objects folder already exists in original ' \
                  f'files,n/a,n/a,n/a,n/a,n/a,n/a,n/a,n/a,Error during processing\n'
        expected = [self.header, aip_row]

        self.assertEqual(expected, result, 'Problem with one aip')

    def test_multiple_aips(self):
        """
        Test for making the log file with information from three AIPs.
        Result for testing is the content of the log file.
        """
        # Creates the log.
        # To save time, updates some items in each AIP's log variable without running the workflow steps.
        log('header')
        aip1 = AIP(os.getcwd(), 'test', 'coll-1', 'aip-1-folder', 'aip-1', 'title-1', 1, to_zip=False)
        aip1.log['Deletions'] = 'No files deleted'
        aip1.log['ObjectsError'] = 'Objects folder already exists in original files'
        aip1.log['Complete'] = 'Error during processing'
        log(aip1.log)

        aip2 = AIP(os.getcwd(), 'test', 'coll-1', 'aip-2-folder', 'aip-2', 'title-2', 1, to_zip=False)
        aip2.log['Deletions'] = 'No files deleted'
        aip2.log['ObjectsError'] = 'Successfully created objects folder'
        aip2.log['MetadataError'] = 'Successfully created metadata folder'
        aip2.log['FITSTool'] = 'No FITS tool errors'
        aip2.log['FITSError'] = 'Successfully created combined-fits.xml'
        aip2.log['PresXML'] = 'Successfully created preservation.xml'
        aip2.log['PresValid'] = 'Preservation.xml is not valid (see log in error folder)'
        aip2.log['Complete'] = 'Error during processing'
        log(aip2.log)

        aip3 = AIP(os.getcwd(), 'test', 'coll-1', 'aip-3-folder', 'aip-3', 'title-3', 1, to_zip=False)
        aip3.log['Deletions'] = 'No files deleted'
        aip3.log['ObjectsError'] = 'Successfully created objects folder'
        aip3.log['MetadataError'] = 'Successfully created metadata folder'
        aip3.log['FITSTool'] = 'No FITS tool errors'
        aip3.log['FITSError'] = 'Successfully created combined-fits.xml'
        aip3.log['PresXML'] = 'Successfully created preservation.xml'
        aip3.log['PresValid'] = 'Preservation.xml valid on 2022-10-31 13:14:15.123456'
        aip3.log['BagValid'] = 'Bag valid on 2022-10-13 14:15:16.789123'
        aip3.log['Package'] = 'Successfully made package'
        aip3.log['Manifest'] = 'Successfully added AIP to manifest.'
        aip3.log['Complete'] = 'Successfully completed processing'
        log(aip3.log)

        # Result is a list, with the text of each row as a list item.
        # Result and expected are lists, with the text of each row as a list item.
        with open(os.path.join('..', 'aip_log.csv'), 'r') as file:
            result = file.readlines()

        # Time from the log is used for an exact comparison.
        # Time changes each time the rest is run. The rest of the expected values are the same each time.
        aip1_row = f'{str(aip1.log["Started"])},aip-1,No files deleted,Objects folder already exists in original ' \
                   f'files,n/a,n/a,n/a,n/a,n/a,n/a,n/a,n/a,Error during processing\n'

        aip2_row = f'{str(aip2.log["Started"])},aip-2,No files deleted,Successfully created objects folder,' \
                   f'Successfully created metadata folder,' \
                   f'No FITS tool errors,Successfully created combined-fits.xml,Successfully created ' \
                   f'preservation.xml,Preservation.xml is not valid (see log in error folder),n/a,n/a,n/a,' \
                   f'Error during processing\n'

        aip3_row = f'{str(aip3.log["Started"])},aip-3,No files deleted,Successfully created objects folder,' \
                   f'Successfully created metadata folder,' \
                   f'No FITS tool errors,Successfully created combined-fits.xml,Successfully created ' \
                   f'preservation.xml,Preservation.xml valid on 2022-10-31 13:14:15.123456,Bag valid on 2022-10-13 ' \
                   f'14:15:16.789123,Successfully made package,Successfully added AIP to manifest.,Successfully ' \
                   f'completed processing\n'
        expected = [self.header, aip1_row, aip2_row, aip3_row]

        self.assertEqual(expected, result, 'Problem with multiple aips')


if __name__ == '__main__':
    unittest.main()
