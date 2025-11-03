"""Testing for the function validate_preservation_xml, which takes an AIP class instance as input and
validates the preservation.xml metadata file already in the AIP metadata folder.
There is error handling for if the preservation.xml file is missing or not valid."""
from datetime import date
import os
import pandas as pd
import shutil
import unittest
from aip_functions import AIP, log, validate_preservation_xml
from test_script import make_aip_log_list


class TestValidatePreservationXML(unittest.TestCase):

    def tearDown(self):
        """Deletes the AIP log, AIP copies used for error testing, and errors folder, if made"""

        log_path = os.path.join(os.getcwd(), 'validate_preservation_xml', 'aip_log.csv')
        if os.path.exists(log_path):
            os.remove(log_path)

        errors_path = os.path.join(os.getcwd(), 'staging', 'aips-with-errors')
        if os.path.exists(errors_path):
            shutil.rmtree(errors_path)

        for aip in ['test_c01_003', 'test_c01_004']:
            aip_path = os.path.join(os.getcwd(), 'validate_preservation_xml', aip)
            if os.path.exists(aip_path):
                shutil.rmtree(aip_path)

    def test_valid(self):
        """Test for successfully validating a preservation.xml file"""
        # Makes the test input and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'validate_preservation_xml')
        aip = AIP(aips_dir, 'test', None, 'test_c01', 'folder', 'general', 'test_c01_001', 'title', 1, True)
        validate_preservation_xml(aip, os.path.join(os.getcwd(), 'staging'))

        # Test for the AIP Log: preservation.xml is made.
        result = aip.log['PresXML']
        expected = 'Successfully created preservation.xml'
        self.assertEqual(expected, result, "Problem with valid, log: PresXML")

        # Test for the AIP Log: preservation.xml is valid.
        # Removes the timestamp (last 16 characters) from result for a consistent expected value.
        result = aip.log['PresValid'][:-16]
        expected = f'Preservation.xml valid on {date.today()}'
        self.assertEqual(expected, result, "Problem with valid, log: PresValid")

    def test_valid_multiple_rights(self):
        """Test for successfully validating a preservation.xml file with multiple rights statements (and one file)"""
        # Makes the test input and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'validate_preservation_xml')
        aip = AIP(aips_dir, 'test', None, 'test_c01', 'folder', 'general', 'test_c01_002', 'title', 1, True)
        validate_preservation_xml(aip, os.path.join(os.getcwd(), 'staging'))

        # Test for the AIP Log: preservation.xml is made.
        result = aip.log['PresXML']
        expected = 'Successfully created preservation.xml'
        self.assertEqual(expected, result, "Problem with valid with multiple rights, log: PresXML")

        # Test for the AIP Log: preservation.xml is valid.
        # Removes the timestamp (last 16 characters) from result for a consistent expected value.
        result = aip.log['PresValid'][:-16]
        expected = f'Preservation.xml valid on {date.today()}'
        self.assertEqual(expected, result, "Problem with valid with multiple rights, log: PresValid")

    def test_error_missing(self):
        """Test for error handling if the preservation.xml file is missing"""
        # Makes the test input and runs the function.
        # A copy of the AIP is made since this test should move it to an error folder.
        # The AIP log is updated as if previous steps have run correctly.
        aips_dir = os.path.join(os.getcwd(), 'validate_preservation_xml')
        aip = AIP(aips_dir, 'test', None, 'test_c01', 'folder', 'general', 'test_c01_003', 'title', 1, True)
        aip.log = {'Started': '2025-08-13 02:35:00.000000', 'AIP': 'test_c01_003', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'n/a', 'PresValid': 'n/a', 'BagValid': 'n/a', 'Package': 'n/a', 'Manifest': 'n/a',
                   'Complete': 'n/a'}
        log('header', aips_dir)
        shutil.copytree(os.path.join(aips_dir, 'test_c01_003_copy'), os.path.join(aips_dir, 'test_c01_003'))
        validate_preservation_xml(aip, os.path.join(os.getcwd(), 'staging'))

        # Test for if the AIP folder is in the error folder.
        result = os.path.exists(os.path.join(os.getcwd(), 'staging', 'aips-with-errors', 'preservationxml_not_found',
                                             'test_c01_003'))
        self.assertEqual(result, True, "Problem with error: missing, move to error folder")

        # Test for the contents of the AIP log.
        # Must change the "/" in the xmllint output to "\" for it to match aips_dir.
        # Output is formatted differently depending on the OS the test is run on.
        result = make_aip_log_list(os.path.join(aips_dir, 'aip_log.csv'))
        aips_dir_backward = aips_dir.replace('/', '\\')
        expected = [[['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                     'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    ['2025-08-13', 'test_c01_003', 'No files deleted', 'Success', 'Success', 'BLANK', 'Success',
                     f'Preservation.xml was not created. xmllint error: warning: failed to load external entity '
                     f'"file:\\{aips_dir}\\test_c01_003\\metadata\\test_c01_003_preservation.xml"\r\n',
                     'BLANK', 'BLANK', 'BLANK', 'BLANK', 'Error during processing']],
                    [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                      'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                      'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                     ['2025-08-13', 'test_c01_003', 'No files deleted', 'Success', 'Success', 'BLANK', 'Success',
                      f'Preservation.xml was not created. xmllint error: warning: failed to load external entity '
                      f'"{aips_dir_backward}\\test_c01_003\\metadata\\test_c01_003_preservation.xml"\n',
                      'BLANK', 'BLANK', 'BLANK', 'BLANK', 'Error during processing']]]
        self.assertIn(result, expected, "Problem with error: missing, log")

    def test_error_not_valid(self):
        """Test for error handling if the preservation.xml file is not valid"""
        # Makes the test input and runs the function.
        # A copy of the AIP is made since this test should move it to an error folder.
        # The AIP log is updated as if previous steps have run correctly.
        aips_dir = os.path.join(os.getcwd(), 'validate_preservation_xml')
        aip = AIP(aips_dir, 'test', None, 'test_c01', 'folder', 'general', 'test_c01_004', 'title', 1, True)
        aip.log = {'Started': '2025-08-13 03:55:00.000000', 'AIP': 'test_c01_004', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'n/a', 'PresValid': 'n/a', 'BagValid': 'n/a', 'Package': 'n/a', 'Manifest': 'n/a',
                   'Complete': 'n/a'}
        log('header', aips_dir)
        shutil.copytree(os.path.join(aips_dir, 'test_c01_004_copy'), os.path.join(aips_dir, 'test_c01_004'))
        validate_preservation_xml(aip, os.path.join(os.getcwd(), 'staging'))

        # Test for if the AIP folder is in the error folder.
        result = os.path.exists(os.path.join(os.getcwd(), 'staging', 'aips-with-errors',
                                             'preservationxml_not_valid', 'test_c01_004'))
        self.assertEqual(result, True, "Problem with error: missing, move to error folder")

        # Test for the contents of the AIP log.
        result = make_aip_log_list(os.path.join(aips_dir, 'aip_log.csv'))
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                     'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    ['2025-08-13', 'test_c01_004', 'No files deleted', 'Success', 'Success', 'BLANK', 'Success',
                     'Successfully created preservation.xml', 'Preservation.xml is not valid (see log in error folder)',
                     'BLANK', 'BLANK', 'BLANK', 'Error during processing']]
        self.assertEqual(expected, result, "Problem with error: missing, aip log")

        # Test for the validation log.
        # Output is formatted differently depending on the OS the test is run on.
        log_path = os.path.join(os.getcwd(), 'staging', 'aips-with-errors', 'preservationxml_not_valid',
                                'test_c01_004_presxml_validation.txt')
        with open(log_path, 'r') as f:
            result = f.readlines()
        aips_dir_forward = aips_dir.replace('\\', '/')
        expected = [[f'file:/{aips_dir_forward}/test_c01_004/metadata/test_c01_004_preservation.xml:20: '
                     'element formatDesignation: Schemas validity error : Element '
                     "'{http://www.loc.gov/premis/v3}formatDesignation': Missing child element(s). "
                     'Expected is ( {http://www.loc.gov/premis/v3}formatName ).\n',
                     '\n',
                     f'file:/{aips_dir_forward}/test_c01_004/metadata/test_c01_004_preservation.xml:25: '
                     'element formatRegistryKey: Schemas validity error : Element '
                     "'{http://www.loc.gov/premis/v3}formatRegistryKey': This element is not "
                     'expected. Expected is ( {http://www.loc.gov/premis/v3}formatRegistryRole '
                     ').\n',
                     '\n',
                     f'file:/{aips_dir_forward}/test_c01_004/metadata/test_c01_004_preservation.xml:45: '
                     'element objectIdentifier: Schemas validity error : Element '
                     "'{http://www.loc.gov/premis/v3}objectIdentifier': Missing child element(s). "
                     'Expected is ( {http://www.loc.gov/premis/v3}objectIdentifierValue ).\n',
                     '\n',
                     f'file:/{aips_dir_forward}/test_c01_004/metadata/test_c01_004_preservation.xml:48: '
                     'element objectCategory: Schemas validity error : Element '
                     "'{http://www.loc.gov/premis/v3}objectCategory': [facet 'enumeration'] The "
                     "value 'error' is not an element of the set {'bitstream', 'file', "
                     "'intellectual entity', 'representation'}.\n",
                     '\n',
                     f'file:/{aips_dir_forward}/test_c01_004/metadata/test_c01_004_preservation.xml:60: '
                     'element formatDesignation: Schemas validity error : Element '
                     "'{http://www.loc.gov/premis/v3}formatDesignation': This element is not "
                     'expected. Expected is one of ( {http://www.loc.gov/premis/v3}formatRegistry, '
                     '{http://www.loc.gov/premis/v3}formatNote ).\n',
                     '\n',
                     f'{aips_dir}\\test_c01_004\\metadata\\test_c01_004_preservation.xml '
                     'fails to validate\n',
                     '\n',
                     '\n'],
                    [f"{aips_dir}/test_c01_004/metadata/test_c01_004_preservation.xml:20: "
                     "element formatDesignation: Schemas validity error : Element "
                     "'{http://www.loc.gov/premis/v3}formatDesignation': Missing child element(s). "
                     "Expected is ( {http://www.loc.gov/premis/v3}formatName ).\n",
                     f"{aips_dir}/test_c01_004/metadata/test_c01_004_preservation.xml:25: "
                     "element formatRegistryKey: Schemas validity error : Element "
                     "'{http://www.loc.gov/premis/v3}formatRegistryKey': This element is not "
                     "expected. Expected is ( {http://www.loc.gov/premis/v3}formatRegistryRole ).\n",
                     f"{aips_dir}/test_c01_004/metadata/test_c01_004_preservation.xml:45: "
                     "element objectIdentifier: Schemas validity error : Element "
                     "'{http://www.loc.gov/premis/v3}objectIdentifier': Missing child element(s). "
                     "Expected is ( {http://www.loc.gov/premis/v3}objectIdentifierValue ).\n",
                     f"{aips_dir}/test_c01_004/metadata/test_c01_004_preservation.xml:48: "
                     'element objectCategory: Schemas validity error : Element '
                     "'{http://www.loc.gov/premis/v3}objectCategory': [facet 'enumeration'] The "
                     "value 'error' is not an element of the set {'bitstream', 'file', "
                     "'intellectual entity', 'representation'}.\n",
                     f"{aips_dir}/test_c01_004/metadata/test_c01_004_preservation.xml:60: "
                     "element formatDesignation: Schemas validity error : Element "
                     "'{http://www.loc.gov/premis/v3}formatDesignation': This element is not "
                     "expected. Expected is one of ( {http://www.loc.gov/premis/v3}formatRegistry, "
                     "{http://www.loc.gov/premis/v3}formatNote ).\n",
                     f"{aips_dir}/test_c01_004/metadata/test_c01_004_preservation.xml fails to validate\n", "\n"]]
        self.assertIn(result, expected, "Problem with error: not valid, validation log")


if __name__ == "__main__":
    unittest.main()
