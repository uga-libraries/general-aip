"""Testing for the function combine_metadata, which takes an AIP class instance as input and
combines the FITS files in the AIP's metadata folder into a single XML file."""

import os
import shutil
import unittest
import xml.etree.ElementTree as ET
from aip_functions import AIP, combine_metadata


def read_xml(path):
    """
    Reads an XML file, either from the function output or the expected file stored in the repo,
    so they can be fully compared with each other
    """
    with open(path, 'r') as result_file:
        tree = ET.parse(result_file)
    read_file = ET.tostring(tree.getroot())
    return read_file


class TestCombineMetadata(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the log, errors folder, and combined fits xml, if present.
        """
        # Deletes files created by the function.
        file_paths = [os.path.join('combine_metadata', 'aip_log.csv'),
                      os.path.join('combine_metadata', 'aip-2', 'metadata', 'aip-2_combined-fits.xml'),
                      os.path.join('combine_metadata', 'aip-1', 'metadata', 'aip-1_combined-fits.xml')]
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

        # Deletes the errors folder and its contents.
        if os.path.exists('aips-with-errors'):
            shutil.rmtree('aips-with-errors')

    def test_one_file(self):
        """
        Test for an AIP with one file (Plain text).
        """
        # Makes the AIP instance and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'combine_metadata')
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder-1', 'general', 'aip-1', 'title', 1, True)
        combine_metadata(aip, os.getcwd())

        # Test for combined-fits.xml produced by the function.
        result = read_xml(os.path.join(aips_dir, 'aip-1', 'metadata', 'aip-1_combined-fits.xml'))
        expected = read_xml(os.path.join(aips_dir, 'expected_xml', 'aip-1_combined-fits.xml'))
        self.assertEqual(result, expected, "Problem with one file, combined-fits.xml")

        # Test for AIP log.
        result_log = aip.log['FITSError']
        expected_log = 'Successfully created combined-fits.xml'
        self.assertEqual(result_log, expected_log, "Problem with one file, log")

    def test_multiple_files(self):
        """
        Test for an AIP with multiple files of different formats (CSV, JSON, Plain text).
        """
        # Makes the AIP instance and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'combine_metadata')
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder-2', 'general', 'aip-2', 'title', 1, True)
        combine_metadata(aip, os.getcwd())

        # Test for combined-fits.xml produced by the function.
        # Tests a sorted list of each fits element because the file order differs between OS.
        tree = ET.parse(os.path.join(aips_dir, 'aip-2', 'metadata', 'aip-2_combined-fits.xml'))
        root = tree.getroot()
        fits_element = root.findall('{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fits')
        result = []
        for fits in fits_element:
            result.append(ET.tostring(fits, encoding='unicode'))
        result.sort()

        expected_0 = ('<fits xmlns="http://hul.harvard.edu/ois/xml/ns/fits/fits_output" '
                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                      'xsi:schemaLocation="http://hul.harvard.edu/ois/xml/ns/fits/fits_output '
                      'http://hul.harvard.edu/ois/xml/xsd/fits/fits_output.xsd" version="1.5.0" timestamp="7/18/25 9:27 AM">\n'
                      '  <identification status="CONFLICT">\n'
                      '    <identity format="JSON Data Interchange Format" mimetype="application/json" toolname="FITS" toolversion="1.5.0">\n'
                      '      <tool toolname="Droid" toolversion="6.4" />\n'
                      '      <externalIdentifier toolname="Droid" toolversion="6.4" type="puid">fmt/817</externalIdentifier>\n'
                      '    </identity>\n'
                      '    <identity format="Plain text" mimetype="text/plain" toolname="FITS" toolversion="1.5.0">\n'
                      '      <tool toolname="Jhove" toolversion="1.20.1" />\n'
                      '      <tool toolname="file utility" toolversion="5.03" />\n'
                      '    </identity>\n'
                      '    <identity format="JSON" mimetype="application/json" toolname="FITS" toolversion="1.5.0">\n'
                      '      <tool toolname="Exiftool" toolversion="11.54" />\n'
                      '    </identity>\n'
                      '  </identification>\n'
                      '  <fileinfo>\n'
                      '    <size toolname="Jhove" toolversion="1.20.1">120</size>\n'
                      '    <filepath toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">CURRENT-DIRECTORY\combine_metadata\\aip-2\objects\Pandas Output\output.json</filepath>\n'
                      '    <filename toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">output.json</filename>\n'
                      '    <md5checksum toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">525216486df22ea55e7ab7c17acc3cf8</md5checksum>\n'
                      '    <fslastmodified toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">1752845261635</fslastmodified>\n'
                      '  </fileinfo>\n'
                      '  <filestatus />\n'
                      '  <metadata />\n'
                      '  <statistics fitsExecutionTime="374">\n'
                      '    <tool toolname="OIS Audio Information" toolversion="0.1" status="did not run" />\n'
                      '    <tool toolname="ADL Tool" toolversion="0.1" status="did not run" />\n'
                      '    <tool toolname="VTT Tool" toolversion="0.1" status="did not run" />\n'
                      '    <tool toolname="Droid" toolversion="6.4" executionTime="4" />\n'
                      '    <tool toolname="Jhove" toolversion="1.20.1" executionTime="146" />\n'
                      '    <tool toolname="file utility" toolversion="5.03" executionTime="195" />\n'
                      '    <tool toolname="Exiftool" toolversion="11.54" executionTime="368" />\n'
                      '    <tool toolname="NLNZ Metadata Extractor" toolversion="3.6GA" status="did not run" />\n'
                      '    <tool toolname="OIS File Information" toolversion="1.0" executionTime="2" />\n'
                      '    <tool toolname="OIS XML Metadata" toolversion="0.2" status="did not run" />\n'
                      '    <tool toolname="ffident" toolversion="0.2" executionTime="9" />\n'
                      '    <tool toolname="Tika" toolversion="1.21" executionTime="7" />\n'
                      '  </statistics>\n'
                      '</fits>')
        self.assertEqual(result[0], expected_0, "Problem with multiple files, combined-fits.xml, 1st fits")
        expected_1 = ('<fits xmlns="http://hul.harvard.edu/ois/xml/ns/fits/fits_output" '
                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                      'xsi:schemaLocation="http://hul.harvard.edu/ois/xml/ns/fits/fits_output '
                      'http://hul.harvard.edu/ois/xml/xsd/fits/fits_output.xsd" version="1.5.0" timestamp="7/18/25 9:27 AM">\n'
                      '  <identification status="SINGLE_RESULT">\n'
                      '    <identity format="Comma-Separated Values (CSV)" mimetype="text/csv" toolname="FITS" toolversion="1.5.0">\n'
                      '      <tool toolname="Droid" toolversion="6.4" />\n'
                      '      <externalIdentifier toolname="Droid" toolversion="6.4" type="puid">x-fmt/18</externalIdentifier>\n'
                      '    </identity>\n'
                      '  </identification>\n'
                      '  <fileinfo>\n'
                      '    <filepath toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">CURRENT-DIRECTORY\combine_metadata\\aip-2\objects\Pandas Output\output.csv</filepath>\n'
                      '    <filename toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">output.csv</filename>\n'
                      '    <size toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">56</size>\n'
                      '    <md5checksum toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">c1ba0d48bdba30ca540b4dcf3249692f</md5checksum>\n'
                      '    <fslastmodified toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">1752845261634</fslastmodified>\n'
                      '  </fileinfo>\n'
                      '  <filestatus />\n'
                      '  <metadata />\n'
                      '  <statistics fitsExecutionTime="439">\n'
                      '    <tool toolname="OIS Audio Information" toolversion="0.1" status="did not run" />\n'
                      '    <tool toolname="ADL Tool" toolversion="0.1" status="did not run" />\n'
                      '    <tool toolname="VTT Tool" toolversion="0.1" status="did not run" />\n'
                      '    <tool toolname="Droid" toolversion="6.4" executionTime="87" />\n'
                      '    <tool toolname="Jhove" toolversion="1.20.1" status="did not run" />\n'
                      '    <tool toolname="file utility" toolversion="5.03" status="did not run" />\n'
                      '    <tool toolname="Exiftool" toolversion="11.54" executionTime="434" />\n'
                      '    <tool toolname="NLNZ Metadata Extractor" toolversion="3.6GA" status="did not run" />\n'
                      '    <tool toolname="OIS File Information" toolversion="1.0" executionTime="85" />\n'
                      '    <tool toolname="OIS XML Metadata" toolversion="0.2" status="did not run" />\n'
                      '    <tool toolname="ffident" toolversion="0.2" executionTime="379" />\n'
                      '    <tool toolname="Tika" toolversion="1.21" executionTime="331" />\n'
                      '  </statistics>\n'
                      '</fits>')
        self.assertEqual(result[1], expected_1, "Problem with multiple files, combined-fits.xml, 2nd fits")
        expected_2 = ('<fits xmlns="http://hul.harvard.edu/ois/xml/ns/fits/fits_output" '
                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                      'xsi:schemaLocation="http://hul.harvard.edu/ois/xml/ns/fits/fits_output '
                      'http://hul.harvard.edu/ois/xml/xsd/fits/fits_output.xsd" version="1.5.0" timestamp="7/18/25 9:27 AM">\n'
                      '  <identification>\n'
                      '    <identity format="Plain text" mimetype="text/plain" toolname="FITS" toolversion="1.5.0">\n'
                      '      <tool toolname="Droid" toolversion="6.4" />\n'
                      '      <tool toolname="Jhove" toolversion="1.20.1" />\n'
                      '      <tool toolname="file utility" toolversion="5.03" />\n'
                      '      <externalIdentifier toolname="Droid" toolversion="6.4" type="puid">x-fmt/111</externalIdentifier>\n'
                      '    </identity>\n'
                      '  </identification>\n'
                      '  <fileinfo>\n'
                      '    <size toolname="Jhove" toolversion="1.20.1">9</size>\n'
                      '    <filepath toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">CURRENT-DIRECTORY\combine_metadata\\aip-2\objects\Text.txt</filepath>\n'
                      '    <filename toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">Text.txt</filename>\n'
                      '    <md5checksum toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">dfee14c3ca5a537621c67ffba86333b7</md5checksum>\n'
                      '    <fslastmodified toolname="OIS File Information" toolversion="1.0" status="SINGLE_RESULT">1752845261626</fslastmodified>\n'
                      '  </fileinfo>\n'
                      '  <filestatus>\n'
                      '    <well-formed toolname="Jhove" toolversion="1.20.1" status="SINGLE_RESULT">true</well-formed>\n'
                      '    <valid toolname="Jhove" toolversion="1.20.1" status="SINGLE_RESULT">true</valid>\n'
                      '  </filestatus>\n'
                      '  <metadata>\n'
                      '    <text>\n'
                      '      <charset toolname="Jhove" toolversion="1.20.1">US-ASCII</charset>\n'
                      '    </text>\n'
                      '  </metadata>\n'
                      '  <statistics fitsExecutionTime="97">\n'
                      '    <tool toolname="OIS Audio Information" toolversion="0.1" status="did not run" />\n'
                      '    <tool toolname="ADL Tool" toolversion="0.1" status="did not run" />\n'
                      '    <tool toolname="VTT Tool" toolversion="0.1" status="did not run" />\n'
                      '    <tool toolname="Droid" toolversion="6.4" executionTime="4" />\n'
                      '    <tool toolname="Jhove" toolversion="1.20.1" executionTime="40" />\n'
                      '    <tool toolname="file utility" toolversion="5.03" executionTime="92" />\n'
                      '    <tool toolname="Exiftool" toolversion="11.54" status="did not run" />\n'
                      '    <tool toolname="NLNZ Metadata Extractor" toolversion="3.6GA" status="did not run" />\n'
                      '    <tool toolname="OIS File Information" toolversion="1.0" executionTime="3" />\n'
                      '    <tool toolname="OIS XML Metadata" toolversion="0.2" status="did not run" />\n'
                      '    <tool toolname="ffident" toolversion="0.2" executionTime="8" />\n'
                      '    <tool toolname="Tika" toolversion="1.21" executionTime="5" />\n'
                      '  </statistics>\n'
                      '</fits>')
        self.assertEqual(result[2], expected_2, "Problem with multiple files, combined-fits.xml, 3rd fits")

        result = read_xml(os.path.join(aips_dir, 'aip-2', 'metadata', 'aip-2_combined-fits.xml'))
        expected = read_xml(os.path.join(aips_dir, 'expected_xml', 'aip-2_combined-fits.xml'))
        self.assertEqual(result, expected, "Problem with multiple files, combined-fits.xml")

        # Test for AIP log.
        result_log = aip.log['FITSError']
        expected_log = 'Successfully created combined-fits.xml'
        self.assertEqual(result_log, expected_log, "Problem with multiple files, log")

    def test_error_et_parse(self):
        """
        Test for an AIP where the FITS XML can't be parsed correctly by ElementTree.
        The metadata folder has a file with the correct name but not the expected contents.
        """
        # Makes the AIP instance, a copy of the aip folder (moved by test) and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'combine_metadata')
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder-error', 'general', 'aip-0', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, 'aip-0_copy'), os.path.join(aips_dir, 'aip-0'))
        combine_metadata(aip, os.getcwd())

        # Test for if the folder is moved, both that it is in the error folder
        # and is not in the original location (AIPs directory).
        result = (os.path.exists(os.path.join('aips-with-errors', 'combining_fits', 'aip-0')),
                  os.path.exists(os.path.join(aips_dir, 'aip-0')))
        expected = (True, False)
        self.assertEqual(result, expected, "Problem with ET parse error, move to error folder")

        # Test for the AIP log, FITSError.
        result_log = aip.log['FITSError']
        expected_log = 'Issue when creating combined-fits.xml: syntax error: line 1, column 0'
        self.assertEqual(result_log, expected_log, "Problem with ET parse error, log: FITSError")

        # Test for the AIP log, Complete.
        result_log2 = aip.log['Complete']
        expected_log2 = 'Error during processing'
        self.assertEqual(result_log2, expected_log2, "Problem with ET parse error, log: Complete")


if __name__ == "__main__":
    unittest.main()
