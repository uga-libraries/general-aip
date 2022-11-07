"""Testing for the function log, which takes either the string 'header' or an AIP instance
and adds a row to the aip log with the information.

The log is updated after each step in the script.
These tests are for if information is written to a CSV correctly.
They are not testing if the correct information is saved to the log after each step."""

import datetime
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
        To allow for exact comparison, gets the time from the log which should be in the expected results.
        To save time, updates some items in the AIP's log variable without running the workflow steps.
        """
        log('header')
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'one-tar-folder', 'one-tar', 'title', 1, to_zip=False)
        aip.log['Deletions'] = 'No files deleted'
        aip.log['ObjectsError'] = 'Objects folder already exists in original files'
        aip.log['Complete'] = 'Error during processing'
        log(aip.log)
        with open(os.path.join('..', 'aip_log.csv'), 'r') as file:
            result = file.readlines()
        expected = ['Time Started,AIP ID,Files Deleted,Objects Folder,Metadata Folder,FITS Tool Errors,FITS Combination Errors,Preservation.xml Made,Preservation.xml Valid,Bag Valid,Package Errors,Manifest Errors,Processing Complete\n',
                    f'{aip.log["Started"]},one-tar,No files deleted,Objects folder already exists in original files,n/a,n/a,n/a,n/a,n/a,n/a,n/a,n/a,Error during processing\n']
        self.assertEqual(expected, result, 'Problem with one aip')

    def test_multiple_aips(self):
        """
        Test for making the log file with information from three AIPs.
        To allow for exact comparison, gets the time from the log which should be in the expected results.
        To save time, updates some items in the AIP's log variable without running the workflow steps.
        """
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

        with open(os.path.join('..', 'aip_log.csv'), 'r') as file:
            result = file.readlines()

        header_expected = ['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                           'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made',
                           'Preservation.xml Valid', 'Bag Valid', 'Package Errors', 'Manifest Errors',
                           'Processing Complete\n']
        aip1_expected = [str(aip1.log['Started']), 'aip-1', 'No files deleted', 'Objects folder already exists in original files',
                         'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'Error during processing\n']
        aip2_expected = [str(aip2.log['Started']), 'aip-2', 'No files deleted', 'Successfully created objects folder',
                         'Successfully created metadata folder', 'No FITS tool errors',
                         'Successfully created combined-fits.xml', 'Successfully created preservation.xml',
                         'Preservation.xml is not valid (see log in error folder)', 'n/a', 'n/a', 'n/a',
                         'Error during processing\n']
        aip3_expected = [str(aip3.log['Started']), 'aip-3', 'No files deleted', 'Successfully created objects folder',
                         'Successfully created metadata folder', 'No FITS tool errors',
                         'Successfully created combined-fits.xml', 'Successfully created preservation.xml',
                         'Preservation.xml valid on 2022-10-31 13:14:15.123456',
                         'Bag valid on 2022-10-13 14:15:16.789123', 'Successfully made package',
                         'Successfully added AIP to manifest.', 'Successfully completed processing\n']
        expected = [",".join(header_expected), ",".join(aip1_expected), ",".join(aip2_expected), ",".join(aip3_expected)]
        self.assertEqual(expected, result, 'Problem with multiple aips')


if __name__ == '__main__':
    unittest.main()
