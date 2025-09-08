"""Testing for the function make_preservation_xml, which takes an AIP class instance as input and
makes the preservation.xml metadata file from the cleaned-fits.xml file already in the AIP metadata folder.
There is error handling throughout for XML transformation.

There is a test for each AIP ID format, since the stylesheet for making the preservation.xml
uses the ID to calculate additional values."""

import fileinput
import os
import pandas as pd
import shutil
import unittest
from configuration import NAMESPACE
from aip_functions import AIP, log, make_preservation_xml


def read_preservation_xml(aip):
    """
    Reads the preservation.xml produced by the test, replaces the UGA URI with default text uri,
    and returns the resulting string to use for testing if the function produced the correct XML.
    """
    xml_path = os.path.join(aip.directory, aip.id, 'metadata', f'{aip.id}_preservation.xml')
    with fileinput.FileInput(xml_path, inplace=True) as file:
        for line in file:
            print(line.replace(NAMESPACE, 'http://uri'), end="")
    with open(xml_path, 'r') as open_xml:
        read_pres_xml = open_xml.read()
    return read_pres_xml


def read_xml(path):
    """
    Reads an XML file, either from the function output or the expected file stored in the repo,
    so they can be fully compared with each other
    """
    with open(path, 'r') as result_file:
        read_file = result_file.read()
    return read_file


class TestMakePreservationXML(unittest.TestCase):

    def tearDown(self):
        """If they are present, deletes the script outputs."""

        # Deletes any preservation.xml files.
        aip_ids = ('harg-0000-web-202108-0001', 'magil-ggp-2472041-2022-05', 'rabbitbox_0003',
                   'rbrl-025-er-000001', 'rbrl-025-er-000002', 'rbrl-025-er-000003', 'test-er-01')
        for aip_id in aip_ids:
            xml_path = os.path.join(os.getcwd(), 'make_preservation_xml', aip_id, 'metadata',
                                    f'{aip_id}_preservation.xml')
            if os.path.exists(xml_path):
                os.remove(xml_path)

        # Deletes the AIP log.
        log_path = os.path.join(os.getcwd(), 'make_preservation_xml', "aip_log.csv")
        if os.path.exists(log_path):
            os.remove(log_path)

        # Deletes the errors folder.
        errors_path = os.path.join(os.getcwd(), 'staging', 'aips-with-errors')
        if os.path.exists(errors_path):
            shutil.rmtree(errors_path)

    def test_bmac(self):
        """Test for an AIP from BMAC, which calculates file id differently"""
        # Makes the test input and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'make_preservation_xml')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'bmac', 'mp4', 'rabbitbox', 'folder', 'av', 'rabbitbox_0003', 'rabbitbox_0003', 1, True)
        make_preservation_xml(aip, staging_dir)

        # Compares the preservation.xml created by the function to a xml file with the expected values.
        result = read_preservation_xml(aip)
        expected = read_xml(os.path.join(aips_dir, 'expected_preservation_xml', f'{aip.id}_preservation.xml'))
        self.assertEqual(expected, result, "Problem with test for bmac")

    def test_error(self):
        """Test for an AIP without the cleaned FITS XML, which causes a Saxon error"""
        # Makes the test input and runs the function.
        # A copy of the AIP is made since this test should move it to an error folder.
        # The AIP log is updated as if previous steps have run correctly.
        aips_dir = os.path.join(os.getcwd(), 'make_preservation_xml')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'test', None, 'test', 'folder', 'general', 'test-er-01', 'title', 1, True)
        aip.log = {'Started': '2025-08-13 2:15PM', 'AIP': 'test-er-01', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'n/a', 'PresValid': 'n/a', 'BagValid': 'n/a', 'Package': 'n/a', 'Manifest': 'n/a',
                   'Complete': 'n/a'}
        log('header', aips_dir)
        shutil.copytree(os.path.join(aips_dir, 'test-er-01_copy'), os.path.join(aips_dir, 'test-er-01'))
        make_preservation_xml(aip, staging_dir)

        # Verifies the log is created and has the expected values.
        # Output has a different line separator (\r\n or \n) depending on the OS the test is run on.
        log_df = pd.read_csv(os.path.join(aips_dir, 'aip_log.csv'))
        log_df = log_df.fillna('BLANK')
        result = [log_df.columns.tolist()] + log_df.values.tolist()
        expected = [[['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                      'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                      'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                     ['2025-08-13 2:15PM', 'test-er-01', 'No files deleted', 'Success', 'Success', 'BLANK', 'Success',
                      f'Issue when creating preservation.xml. Saxon error: Source file '
                      f'{os.path.join(aips_dir, "test-er-01", "metadata", "test-er-01_cleaned-fits.xml")} '
                      f'does not exist\r\n', 'BLANK', 'BLANK', 'BLANK', 'BLANK', 'Error during processing']],
                    [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                      'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                      'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                     ['2025-08-13 2:15PM', 'test-er-01', 'No files deleted', 'Success', 'Success', 'BLANK', 'Success',
                      f'Issue when creating preservation.xml. Saxon error: Source file '
                      f'{os.path.join(aips_dir, "test-er-01", "metadata", "test-er-01_cleaned-fits.xml")} '
                      f'does not exist\n', 'BLANK', 'BLANK', 'BLANK', 'BLANK', 'Error during processing']]]
        self.assertIn(result, expected, "Problem with test for error, log")

        # Verifies the AIP folder was moved to the error folder.
        result = os.path.exists(os.path.join(staging_dir, 'aips-with-errors', 'pres_xml_saxon_error', 'test-er-01'))
        self.assertEqual(result, True, "Problem with test for error, error folder")

    def test_format_dup(self):
        """Test for an AIP with multiple files of the same format"""
        # Makes the test input and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'make_preservation_xml')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'russell', None, 'rbrl-025', 'folder', 'general', 'rbrl-025-er-000003', 'Dups', 1, True)
        make_preservation_xml(aip, staging_dir)

        # Compares the preservation.xml created by the function to a xml file with the expected values.
        result = read_preservation_xml(aip)
        expected = read_xml(os.path.join(aips_dir, 'expected_preservation_xml', f'{aip.id}_preservation.xml'))
        self.assertEqual(expected, result, "Problem with test for multiple files")

    def test_multiple_files(self):
        """Test for an AIP with multiple files"""
        # Makes the test input and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'make_preservation_xml')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'russell', None, 'rbrl-025', 'folder', 'general', 'rbrl-025-er-000002', 'Multi', 1, True)
        make_preservation_xml(aip, staging_dir)

        # Compares the preservation.xml created by the function to a xml file with the expected values.
        result = read_preservation_xml(aip)
        expected = read_xml(os.path.join(aips_dir, 'expected_preservation_xml', f'{aip.id}_preservation.xml'))
        self.assertEqual(expected, result, "Problem with test for multiple files")

    def test_single_file(self):
        """Test for an AIP with a single file"""
        # Makes the test input and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'make_preservation_xml')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'russell', None, 'rbrl-025', 'folder', 'general', 'rbrl-025-er-000001', 'Single', 1, True)
        make_preservation_xml(aip, staging_dir)

        # Compares the preservation.xml created by the function to a xml file with the expected values.
        result = read_preservation_xml(aip)
        expected = read_xml(os.path.join(aips_dir, 'expected_preservation_xml', f'{aip.id}_preservation.xml'))
        self.assertEqual(expected, result, "Problem with test for single file")

    def test_web_hargrett(self):
        """Test for a web AIP from Hargrett with no collection"""
        # Makes the test input and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'make_preservation_xml')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'hargrett', None, 'harg-0000', 'folder', 'web', 'harg-0000-web-202108-0001',
                  'Hargrett Web without Collection', 1, True)
        make_preservation_xml(aip, staging_dir)

        # Compares the preservation.xml created by the function to a xml file with the expected values.
        result = read_preservation_xml(aip)
        expected = read_xml(os.path.join(aips_dir, 'expected_preservation_xml', f'{aip.id}_preservation.xml'))
        self.assertEqual(expected, result, "Problem with test for web, hargrett")

    def test_web_magil(self):
        """Test for a web AIP from MAGIL, which never has a collection"""
        # Makes the test input and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'make_preservation_xml')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'magil', None, 'magil-0000', 'folder', 'web', 'magil-ggp-2472041-2022-05', 'Web', 1, True)
        make_preservation_xml(aip, staging_dir)

        # Compares the preservation.xml created by the function to a xml file with the expected values.
        result = read_preservation_xml(aip)
        expected = read_xml(os.path.join(aips_dir, 'expected_preservation_xml', f'{aip.id}_preservation.xml'))
        self.assertEqual(expected, result, "Problem with test for web, magil")


if __name__ == "__main__":
    unittest.main()
