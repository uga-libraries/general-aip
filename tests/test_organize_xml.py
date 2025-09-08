"""Testing for the function organize_xml, which takes an AIP class instance as input and
deletes, copies, or moves the XML files created to produce the preservation.xml file."""
import os
import shutil
import unittest
from aip_functions import AIP, organize_xml


class TestOrganizeXML(unittest.TestCase):

    def tearDown(self):
        """If they are present, deletes the test AIP and XML copied or moved by the function."""

        aip_path = os.path.join(os.getcwd(), 'organize_xml', 'test_coll2_001')
        if os.path.exists(aip_path):
            shutil.rmtree(aip_path)

        aips_staging = os.path.join(os.getcwd(), 'staging')
        xml_paths = [os.path.join(aips_staging, 'fits-xmls', 'test_coll2_001_combined-fits.xml'),
                     os.path.join(aips_staging, 'preservation-xmls', 'test_coll2_001_preservation.xml')]
        for xml_path in xml_paths:
            if os.path.exists(xml_path):
                os.remove(xml_path)

    def test_organize_xml(self):
        """Test for the function (has no variations)"""
        # Makes the test input and runs the function.
        # A copy of the AIP is made since this test should alter the contents of the AIP metadata folder.
        aips_dir = os.path.join(os.getcwd(), 'organize_xml')
        aips_staging = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'test', None, 'coll-1', 'aip-folder', 'general', 'test_coll2_001', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, 'test_coll2_001_copy'), os.path.join(aips_dir, 'test_coll2_001'))
        organize_xml(aip, aips_staging)

        # Tests the metadata folder contains only the expected files.
        result = []
        for file in os.listdir(os.path.join(os.getcwd(), 'organize_xml', 'test_coll2_001', 'metadata')):
            result.append(file)
        expected = ['file_fits.xml', 'test_coll2_001_preservation.xml']
        self.assertEqual(expected, result, "Problem with organize xml, metadata")

        # Tests the FITS folder has the expected file.
        result = os.path.exists(os.path.join(aips_staging, 'fits-xmls', 'test_coll2_001_combined-fits.xml'))
        self.assertEqual(True, result, "Problem with organize xml, fits-xmls")

        # Tests the preservation xml folder has the expected file.
        result = os.path.exists(os.path.join(aips_staging, 'preservation-xmls', 'test_coll2_001_preservation.xml'))
        self.assertEqual(True, result, "Problem with organize xml, preservation-xmls")


if __name__ == "__main__":
    unittest.main()
