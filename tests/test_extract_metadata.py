"""Testing for the function extract_metadata, which takes an AIP class instance as input and
uses FITS to extract technical metadata, which is combined into a single XML file."""

import csv
import os
import pandas as pd
import shutil
import unittest
import xml.etree.ElementTree as ET
from scripts.aip_functions import AIP, log, structure_directory, extract_metadata


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

    def setUp(self):
        """
        Starts the log, which is typically done in the main body of the script.
        """
        log('header')

    def tearDown(self):
        """
        Deletes the log and error folder, if any, for a clean start to the next test.
        """
        os.remove(os.path.join('..', 'aip_log.csv'))
        if os.path.exists(os.path.join('..', 'errors')):
            shutil.rmtree(os.path.join('..', 'errors'))

    def test_one_file(self):
        """
        Test for an AIP with one file.
        """
        one_file_aip = AIP(os.getcwd(), 'test', 'coll-1', 'one_file', 'one_file', 'title', 1, True)
        os.mkdir('one_file')
        with open(os.path.join('one_file', 'Text.txt'), 'w') as file:
            file.write('Test File')
        structure_directory(one_file_aip)
        extract_metadata(one_file_aip)

        # Edits the produced by the function and then reads it to use for the comparison.
        update_fits(os.path.join('one_file', 'metadata', 'one_file_combined-fits.xml'))
        with open(os.path.join('one_file', 'metadata', 'one_file_combined-fits.xml'), 'r') as result_file:
            result = result_file.read()

        # Deletes the test AIP.
        shutil.rmtree('one_file')

        # Reads data from XML with the expected result after updating.
        with open(os.path.join('combined_fits', 'one_file_combined-fits.xml')) as expected_file:
            expected = expected_file.read()

        self.assertEqual(result, expected, 'Problem with one file')

    def test_multi_id(self):
        """
        Test for an AIP with a format that has multiple possible identifications.
        Format: Excel spreadsheet, identified as ZIP Format, XLSX, and Office Open XML Workbook
        """
        multi_id_aip = AIP(os.getcwd(), 'test', 'coll-1', 'multi_id', 'multi_id', 'title', 1, True)
        os.mkdir('multi_id')
        df = pd.DataFrame({'Column1': ['Text', 'Data', 'More'], 'Column2': ['aaa', 'bbb', 'ccc']})
        df.to_excel(os.path.join('multi_id', 'Spreadsheet.xlsx'), index=False)
        structure_directory(multi_id_aip)
        extract_metadata(multi_id_aip)

        # Edits the produced by the function and then reads it to use for the comparison.
        update_fits(os.path.join('multi_id', 'metadata', 'multi_id_combined-fits.xml'))
        with open(os.path.join('multi_id', 'metadata', 'multi_id_combined-fits.xml'), 'r') as result_file:
            result = result_file.read()

        # Deletes the test AIP.
        shutil.rmtree('multi_id')

        # Reads data from XML with the expected result after updating.
        with open(os.path.join('combined_fits', 'multi_id_combined-fits.xml')) as expected_file:
            expected = expected_file.read()

        self.assertEqual(result, expected, 'Problem with multiple identifications')

    def test_one_format(self):
        """
        Test for an AIP with multiple files that are the same format.
        Format: Comma-Separated Values (CSV)
        """
        one_format_aip = AIP(os.getcwd(), 'test', 'coll-1', 'one_format', 'one_format', 'title', 1, True)
        os.mkdir('one_format')
        with open(os.path.join('one_format', 'spreadsheet.csv'), 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['one', 'two', 'three'])
            writer.writerow(['uno', 'dos', 'tres'])
            writer.writerow(['ein', 'zwei', 'drei'])
        with open(os.path.join('one_format', 'spreadsheet_two.csv'), 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['one fish', 'two fish'])
            writer.writerow(['red fish', 'blue fish'])
        structure_directory(one_format_aip)
        extract_metadata(one_format_aip)
        result = '?????'
        shutil.rmtree('one_format')
        expected = '?????'
        self.assertEqual(result, expected, 'Problem with one format')

    def test_multi_format(self):
        """
        Test for an AIP with multiple files of different formats.
        Formats: Comma-Separated Values (CSV), JSON (also identified as JSON Data Interchange Format and Plain text),
        Plain text
        """
        multi_format_aip = AIP(os.getcwd(), 'test', 'coll-1', 'multi_format', 'multi_format', 'title', 1, True)
        os.mkdir('multi_format')
        with open(os.path.join('multi_format', 'Text.txt'), 'w') as file:
            file.write('Test File')
        os.mkdir(os.path.join('multi_format', 'Pandas Output'))
        df = pd.DataFrame({'First': ['a', 'b', 'c', 'd'], 'Second': [1, 2, 3, 4], 'Third': [0.1, 0.2, 0.3, 0.4]})
        df.to_csv(os.path.join('multi_format', 'Pandas Output', 'output.csv'), index=False)
        df.to_json(os.path.join('multi_format', 'Pandas Output', 'output.json'))
        structure_directory(multi_format_aip)
        extract_metadata(multi_format_aip)
        result = '?????'
        shutil.rmtree('multi_format')
        expected = '?????'
        self.assertEqual(result, expected, 'Problem with multiple formats')

    def test_error_fits_tool(self):
        """
        Test for an AIP with a format that causes FITS to generate an error.
        TODO: how do I cause this error?
        """

    def test_error_et_parse(self):
        """
        Test for an AIP where the FITS XML can't be parsed correctly by ElementTree.
        TODO: how do I cause this error?
        """


if __name__ == '__main__':
    unittest.main()
