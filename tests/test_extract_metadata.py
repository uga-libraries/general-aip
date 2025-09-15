"""Testing for the function extract_metadata, which takes an AIP class instance as input and
uses FITS to extract technical metadata."""

import os
import unittest
from aip_functions import AIP, extract_metadata
from test_script import make_directory_list


class TestExtractMetadata(unittest.TestCase):

    def tearDown(self):
        """Deletes the FITS error log and FITS files in the metadata folders, if present."""
        aips_directory = os.path.join(os.getcwd(), 'extract_metadata')
        file_paths = [os.path.join(aips_directory, 'aip-id-error', 'metadata', 'aip-id-error_fits-tool-errors_fitserr.txt'),
                      os.path.join(aips_directory, 'aip-id-error', 'metadata', 'not.xml_fits.xml'),
                      os.path.join(aips_directory, 'aip-id-multi', 'metadata', 'output.csv_fits.xml'),
                      os.path.join(aips_directory, 'aip-id-multi', 'metadata', 'output.json_fits.xml'),
                      os.path.join(aips_directory, 'aip-id-multi', 'metadata', 'Text.txt_fits.xml'),
                      os.path.join(aips_directory, 'aip-id-one', 'metadata', 'Text.txt_fits.xml')]
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_one_file(self):
        """Test for an AIP with one file"""
        # Makes test input and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'extract_metadata')
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'one_folder', 'general', 'aip-id-one', 'title', 1, True)
        extract_metadata(aip)

        # Test for the contents of the metadata folder.
        metadata_path = os.path.join(aips_dir, 'aip-id-one', 'metadata')
        result = make_directory_list(metadata_path)
        expected = [os.path.join(metadata_path, 'metadata.txt'),
                    os.path.join(metadata_path, 'Text.txt_fits.xml')]
        self.assertEqual(expected, result, "Problem with one file, metadata folder")

        # Test for the AIP log.
        result = aip.log['FITSTool']
        expected = 'No FITS tools errors'
        self.assertEqual(expected, result, "Problem with one file, log")

    def test_multiple_files(self):
        """Test for an AIP with multiple files of different formats (CSV, JSON, Plain text)"""
        # Makes test input and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'extract_metadata')
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'multi_folder', 'general', 'aip-id-multi', 'title', 1, True)
        extract_metadata(aip)

        # Test for the contents of the metadata folder.
        metadata_path = os.path.join(aips_dir, 'aip-id-multi', 'metadata')
        result = make_directory_list(metadata_path)
        expected = [os.path.join(metadata_path, 'metadata.txt'),
                    os.path.join(metadata_path, 'output.csv_fits.xml'),
                    os.path.join(metadata_path, 'output.json_fits.xml'),
                    os.path.join(metadata_path, 'Text.txt_fits.xml')]
        self.assertEqual(expected, result, "Problem with multiple files, metadata folder")

        # Test for the AIP log.
        result = aip.log['FITSTool']
        expected = 'No FITS tools errors'
        self.assertEqual(expected, result, "Problem with multiple files, log")

    def test_error_fits_tool(self):
        """Test for an AIP with a format that causes FITS to generate an error (text file with XML extension)"""
        # Makes test input and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'extract_metadata')
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'tool_error_folder', 'general', 'aip-id-error', 'title', 1, True)
        extract_metadata(aip)

        # Test for the contents of the metadata folder.
        metadata_path = os.path.join(aips_dir, 'aip-id-error', 'metadata')
        result = make_directory_list(os.path.join(aips_dir, 'aip-id-error', 'metadata'))
        expected = [os.path.join(metadata_path, 'aip-id-error_fits-tool-errors_fitserr.txt'),
                    os.path.join(metadata_path, 'metadata.txt'),
                    os.path.join(metadata_path, 'not.xml_fits.xml')]
        self.assertEqual(expected, result, "Problem with error, metadata folder")

        # Test for the FITS error log, which is if 3 phrases are in the file.
        # The contents of the entire file cannot be tested, since most are variable (timestamps and file paths).
        with open(os.path.join(aips_dir, 'aip-id-error', 'metadata', 'aip-id-error_fits-tool-errors_fitserr.txt')) as file:
            content = file.read()
            result = ('org.jdom.input.JDOMParseException' in content,
                      'Tool error processing file' in content,
                      'Content is not allowed in prolog.' in content)
        expected = (True, True, True)
        self.assertEqual(expected, result, "Problem with error, FITS tool log")

        # Test for the AIP log.
        result = aip.log['FITSTool']
        expected = 'FITS tools generated errors (saved to metadata folder)'
        self.assertEqual(expected, result, "Problem with error, AIP log")


if __name__ == "__main__":
    unittest.main()
