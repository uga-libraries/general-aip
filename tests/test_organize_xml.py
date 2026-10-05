"""Testing for the function organize_xml, which takes an AIP class instance as input and
deletes, copies, or moves the XML files created to produce the preservation.xml file."""
import os
import shutil
import unittest
from aip_functions import AIP, organize_xml
from test_script import make_directory_list


class TestOrganizeXML(unittest.TestCase):

    def tearDown(self):
        """If they are present, deletes the test AIP and XML copied or moved by the function."""

        aip_path = os.path.join(os.getcwd(), 'organize_xml', 'test_coll2_001')
        if os.path.exists(aip_path):
            shutil.rmtree(aip_path)

        aips_staging = os.path.join(os.getcwd(), 'staging_for_tests')
        xml_paths = [os.path.join(aips_staging, 'fits-xmls', 'test_coll2_001_combined-fits.xml'),
                     os.path.join(aips_staging, 'preservation-xmls', 'test_coll2_001_preservation.xml')]
        for xml_path in xml_paths:
            if os.path.exists(xml_path):
                os.remove(xml_path)

    def test_typical(self):
        """Test for the function as it is typically used (not no-file-info workflow)"""
        # Makes the test input and runs the function.
        # A copy of the AIP is made since this test should alter the contents of the AIP metadata folder.
        aips_dir = os.path.join(os.getcwd(), 'organize_xml')
        aips_staging = os.path.join(os.getcwd(), 'staging_for_tests')
        aip = AIP(aips_dir, 'test', None, 'coll-2', 'aip-folder', 'general', 'test_coll2_001', 'title', 'InC', 1, True)
        shutil.copytree(os.path.join(aips_dir, 'typical', 'test_coll2_001_copy'),
                        os.path.join(aips_dir, 'test_coll2_001'))
        organize_xml(aip, aips_staging)

        # Tests the metadata folder contains only the expected files.
        metadata_path = os.path.join(os.getcwd(), 'organize_xml', 'test_coll2_001', 'metadata')
        result = make_directory_list(metadata_path)
        expected = [os.path.join(metadata_path, 'filename.txt_fits.xml'),
                    os.path.join(metadata_path, 'test_coll2_001_preservation.xml')]
        self.assertEqual(expected, result, "Problem with typical, metadata")

        # Tests the FITS folder on staging has the expected file.
        result = os.path.exists(os.path.join(aips_staging, 'fits-xmls', 'test_coll2_001_combined-fits.xml'))
        self.assertEqual(True, result, "Problem with typical, fits-xmls")

        # Tests the preservation xml folder on staging has the expected file.
        result = os.path.exists(os.path.join(aips_staging, 'preservation-xmls', 'test_coll2_001_preservation.xml'))
        self.assertEqual(True, result, "Problem with typical, preservation-xmls")


if __name__ == "__main__":
    unittest.main()
