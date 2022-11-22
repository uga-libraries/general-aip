"""Testing for the function extract_metadata_only, which takes an AIP class instance as input and
uses FITS to extract technical metadata."""

import os
import pandas as pd
import shutil
import unittest
from scripts.aip_functions import AIP, structure_directory, extract_metadata_only


class TestExtractMetadata(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the log, error folder, and AIP test folders, if present.
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
        Result for testing is the files in the metadata folder, plus the AIP log.
        """
        one_file_aip = AIP(os.getcwd(), 'test', 'coll-1', 'one_file', 'one_file', 'title', 1, True)
        os.mkdir('one_file')
        with open(os.path.join('one_file', 'Text.txt'), 'w') as file:
            file.write('Test File')
        structure_directory(one_file_aip)
        extract_metadata_only(one_file_aip)

        result = (os.listdir(os.path.join('one_file', 'metadata')), one_file_aip.log['FITSTool'])

        expected = (['Text.txt_fits.xml'], 'No FITS tools errors')

        self.assertEqual(result, expected, 'Problem with one file')

    def test_multiple_files(self):
        """
        Test for an AIP with multiple files of different formats (CSV, JSON, Plain text).
        Result for testing is the files in the metadata folder, plus the AIP log.
        """
        multi_file_aip = AIP(os.getcwd(), 'test', 'coll-1', 'multi_file', 'multi_file', 'title', 1, True)
        os.mkdir('multi_file')
        with open(os.path.join('multi_file', 'Text.txt'), 'w') as file:
            file.write('Test File')
        os.mkdir(os.path.join('multi_file', 'Pandas Output'))
        df = pd.DataFrame({'First': ['a', 'b', 'c', 'd'], 'Second': [1, 2, 3, 4], 'Third': [0.1, 0.2, 0.3, 0.4]})
        df.to_csv(os.path.join('multi_file', 'Pandas Output', 'output.csv'), index=False)
        df.to_json(os.path.join('multi_file', 'Pandas Output', 'output.json'))
        structure_directory(multi_file_aip)
        extract_metadata_only(multi_file_aip)

        result = (os.listdir(os.path.join('multi_file', 'metadata')), multi_file_aip.log['FITSTool'])

        expected = (['output.csv_fits.xml', 'output.json_fits.xml', 'Text.txt_fits.xml'], 'No FITS tools errors')

        self.assertEqual(result, expected, 'Problem with multiple formats')

    def test_error_fits_tool(self):
        """
        Test for an AIP with a format that causes FITS to generate an error.
        Result for testing is the FITS tool errors text file, plus AIP log.
        """
        # Makes the test AIP, including making the initial AIP instance, folder and file and
        # running the first two functions for the AIP workflow.
        # Generates error by making a text file with an XML extension.
        tool_aip = AIP(os.getcwd(), 'test', 'coll-1', 'tool_error', 'tool_error', 'title', 1, True)
        os.mkdir('tool_error')
        with open(os.path.join('tool_error', 'not.xml'), 'w') as file:
            file.write('This is not XML')
        structure_directory(tool_aip)
        extract_metadata_only(tool_aip)

        # Generates result, which is if a few phrases are in the FITs error output.
        # The contents of the entire file cannot be tested, since most are variable (timestamps and file paths).
        with open(os.path.join('tool_error', 'metadata', 'tool_error_fits-tool-errors_fitserr.txt')) as file:
            content = file.read()
            result = ('org.jdom.input.JDOMParseException' in content,
                      'Tool error processing file' in content,
                      'Content is not allowed in prolog.' in content,
                      tool_aip.log['FITSTool'])
            
        expected = (True, True, True, 'FITS tools generated errors (saved to metadata folder)')

        self.assertEqual(result, expected, 'Problem with FITS tool error')


if __name__ == '__main__':
    unittest.main()
