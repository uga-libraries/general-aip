"""Testing for the function combine_metadata, which takes an AIP class instance as input and
combines the FITS files in the AIP's metadata folder into a single XML file."""

import os
import pandas as pd
import shutil
import unittest
import xml.etree.ElementTree as ET
from scripts.aip_functions import AIP, structure_directory, extract_metadata, combine_metadata


def update_fits(path):
    """
    Reads the FITS XML and edits the data to remove data that varies each time the test is run
    so that it can be compared to expected results.
    Saves the updated XML so it can later be read and compared to another file with the expected results.
    """

    # Reads data from XML produced by the function.
    tree = ET.parse(path)
    root = tree.getroot()

    # Changes the timestamp attribute of every fits element.
    for fits in root.iter('{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fits'):
        fits.set('timestamp', 'VARIES')

    # Changes the beginning of the filepath of every filepath element.
    for filepath in root.iter('{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}filepath'):
        new_path = filepath.text.replace(os.getcwd(), 'CURRENT-DIRECTORY')
        filepath.text = new_path

    # Changes the value of every fslastmodified element.
    for date in root.iter('{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fslastmodified'):
        date.text = '0000000000000'

    # Changes the fitsExecutionTime attribute of every statistics element.
    for stats in root.iter('{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}statistics'):
        stats.set('fitsExecutionTime', '000')

    # Changes the executionTime attribute of every tool element with that attribute.
    for tool in root.iter('{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}tool'):
        if 'executionTime' in tool.attrib:
            tool.set('executionTime', '000')

    tree.write(path, xml_declaration=True, encoding='UTF-8')


class TestExtractMetadata(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the log, errors folder, and AIP test folders, if present.
        """
        if os.path.exists(os.path.join('..', 'aip_log.csv')):
            os.remove(os.path.join('..', 'aip_log.csv'))
        
        directory_paths = (os.path.join('..', 'errors'), 'one_file', 'multi_file', 'tool_error', 'et_error')
        for directory_path in directory_paths:
            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)

    def test_one_file(self):
        """
        Test for an AIP with one file.
        Result for testing is the contents of the combined-fits.xml file, with data that varies for each test
        (time FITS was made, etc.) changed to consistent values to allow an exact comparison, plus the AIP log.
        """
        # Makes the test AIP, including making the initial AIP instance, folder and file and
        # running the first two functions for the AIP workflow.
        one_file_aip = AIP(os.getcwd(), 'test', 'coll-1', 'one_file', 'one_file', 'title', 1, True)
        os.mkdir('one_file')
        with open(os.path.join('one_file', 'Text.txt'), 'w') as file:
            file.write('Test File')
        structure_directory(one_file_aip)
        extract_metadata(one_file_aip)
        combine_metadata(one_file_aip)

        # Edits the combined-fits.xml produced by the function and then reads it to use for the comparison.
        update_fits(os.path.join('one_file', 'metadata', 'one_file_combined-fits.xml'))
        with open(os.path.join('one_file', 'metadata', 'one_file_combined-fits.xml'), 'r') as result_file:
            result = (result_file.read(), one_file_aip.log['FITSError'])

        # Reads an XML file with the expected result after editing.
        with open(os.path.join('expected_xml', 'one_file_combined-fits.xml')) as expected_file:
            expected = (expected_file.read(), 'Successfully created combined-fits.xml')

        self.assertEqual(result, expected, 'Problem with one file')

    def test_multiple_files(self):
        """
        Test for an AIP with multiple files of different formats (CSV, JSON, Plain text).
        Result for testing is the contents of the combined-fits.xml file, with data that varies for each test
        (time FITS was made, etc.) changed to consistent values to allow an exact comparison, plus the AIP log.
        """
        # Makes the test AIP, including making the initial AIP instance, folders and files and
        # running the first two functions for the AIP workflow.
        multi_file_aip = AIP(os.getcwd(), 'test', 'coll-1', 'multi_file', 'multi_file', 'title', 1, True)
        os.mkdir('multi_file')
        with open(os.path.join('multi_file', 'Text.txt'), 'w') as file:
            file.write('Test File')
        os.mkdir(os.path.join('multi_file', 'Pandas Output'))
        df = pd.DataFrame({'First': ['a', 'b', 'c', 'd'], 'Second': [1, 2, 3, 4], 'Third': [0.1, 0.2, 0.3, 0.4]})
        df.to_csv(os.path.join('multi_file', 'Pandas Output', 'output.csv'), index=False)
        df.to_json(os.path.join('multi_file', 'Pandas Output', 'output.json'))
        structure_directory(multi_file_aip)
        extract_metadata(multi_file_aip)
        combine_metadata(multi_file_aip)

        # Edits the combined-fits.xml produced by the function and then reads it to use for the comparison.
        update_fits(os.path.join('multi_file', 'metadata', 'multi_file_combined-fits.xml'))
        with open(os.path.join('multi_file', 'metadata', 'multi_file_combined-fits.xml'), 'r') as result_file:
            result = (result_file.read(), multi_file_aip.log['FITSError'])

        # Reads an XML file with the expected result after editing.
        with open(os.path.join('expected_xml', 'multi_file_combined-fits.xml')) as expected_file:
            expected = (expected_file.read(), 'Successfully created combined-fits.xml')

        self.assertEqual(result, expected, 'Problem with multiple formats')

    def test_error_et_parse(self):
        """
        Test for an AIP where the FITS XML can't be parsed correctly by ElementTree.
        Generates error by making a fake FITS file that is not real XML.
        Result for testing is the AIP log and if the AIP is in the expected error folder.
        """
        # Makes the test AIP, including making the initial AIP instance, folder and file and
        # running the first function for the AIP workflow.
        et_aip = AIP(os.getcwd(), 'test', 'coll-1', 'et_error', 'et_error', 'title', 1, True)
        os.mkdir('et_error')
        with open(os.path.join('et_error', 'Text.txt'), 'w') as file:
            file.write('Test File')
        structure_directory(et_aip)

        # To generate the error, adds a text file instead of the correct fits.xml file
        # that would be generated by the extract_metadata_only function.
        with open(os.path.join('et_error', 'metadata', 'et_error_fits.xml'), 'w') as file:
            file.write('This is not FITS XML')

        # Runs the function with the error handling being tested.
        combine_metadata(et_aip)

        # Result is a tuple with the value in the AIP log and if the AIP folder is in the expected error folder.
        result = (et_aip.log['FITSError'], os.path.exists(os.path.join('..', 'errors', 'combining_fits', 'et_error')))
        expected = ('Issue when creating combined-fits.xml: syntax error: line 1, column 0', True)
        self.assertEqual(result, expected, 'Problem with ET parse error')


if __name__ == '__main__':
    unittest.main()
