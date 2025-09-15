"""
Testing for the entire script, with input that represents the different workflows that use the script.
It does not currently include tests for error handling.

BEFORE RUNNING THIS TEST: in configuration.py, make aip_staging the path to staging in the GitHub repo
"""

import datetime
import os
import pandas as pd
import re
import shutil
import subprocess
import unittest


def make_aip_log_list(log_path):
    """Reads the aip log and returns a list of lists, where each list is a row in the log,
    with normalization for inconsistent data."""
    df = pd.read_csv(log_path, dtype=str)

    # Remove time stamps, which are the last 16 characters, and leaves just the day to allow comparison,
    # as long as the column is from a correct validation (may also be blank or a validation error).
    df['Time Started'] = df['Time Started'].str[:-16]
    df.loc[df['Preservation.xml Valid'].str.startswith('Preservation.xml valid on', na=False), 'Preservation.xml Valid'] = df['Preservation.xml Valid'].str[:-16]
    df.loc[df['Bag Valid'].str.startswith('Bag valid on', na=False), 'Bag Valid'] = df['Bag Valid'].str[:-16]

    # Make FITS tool error value consistent, since the same files don't always generate an error.
    df.loc[df['FITS Tool Errors'] == 'FITS tools generated errors (saved to metadata folder)', 'FITS Tool Errors'] = 'No FITS tools errors'

    # Normalize direction of slash from xmllint to match other text.
    df['Preservation.xml Made'] = df['Preservation.xml Made'].str.replace('/', '\\')

    # Convert the dataframe to a list of rows.
    df = df.fillna('BLANK')
    log_list = [df.columns.to_list()] + df.values.tolist()
    return log_list


def make_directory_list(dir_path):
    """Make a list of the paths of every file and folder in a directory,
    with sorting and normalization for inconsistent data."""
    directory_list = []
    for root, dirs, files in os.walk(dir_path):
        for directory in dirs:
            directory_list.append(os.path.join(root, directory))
        for file in files:
            # The size in the zipped AIP filenames varies each time.
            if root.endswith("aips-ready-to-ingest") and file.endswith(".tar.bz2"):
                file = re.sub(r"_bag.\d+.", "_bag.1000.", file)
            # Skips the FITS tool error log because it is not consistently made and the placeholder files for GitHub.
            if file.endswith("_fits-tool-errors_fitserr.txt") or file == 'Explanation.txt' or file == 'placeholder.txt':
                continue
            directory_list.append(os.path.join(root, file))
    directory_list.sort(key=str.lower)
    return directory_list


class TestFullScript(unittest.TestCase):

    def tearDown(self):
        """Deletes the copy of files used for testing and the script outputs for the test"""
        # Test files
        modes = ['av', 'general', 'web']
        for mode in modes:
            mode_path = os.path.join(os.getcwd(), 'script', mode)
            if os.path.exists(mode_path):
                shutil.rmtree(mode_path)

        # Deletes everything but placeholder.txt from the output folders in staging.
        output_dirs = ['aips-ready-to-ingest', 'fits-xmls', 'preservation-xmls']
        for output_dir in output_dirs:
            output_path = os.path.join(os.getcwd(), 'staging', output_dir)
            for file in os.listdir(output_path):
                if not file == 'placeholder.txt':
                    os.remove(os.path.join(output_path, file))

    def test_general(self):
        """Test for the general mode (born-digital archives)"""
        # Makes a copy of the test files stored in the script repo, since the test will alter the files.
        shutil.copytree(os.path.join(os.getcwd(), 'script', 'general_mode'), 
                        os.path.join(os.getcwd(), 'script', 'general'))

        # Runs the script.
        script_path = os.path.join('..', 'general_aip.py')
        aip_dir = os.path.join(os.getcwd(), 'script', 'general', 'aip_directory')
        printed = subprocess.run(f'python "{script_path}" "{aip_dir}" general zip',
                                 shell=True, capture_output=True, text=True)

        # Test for the script print statements.
        result = printed.stdout
        expected = ('\n>>>Processing test-001-er-000001 (1 of 3).\n'
                    '\n>>>Processing test-001-er-000002 (2 of 3).\n'
                    '\n>>>Processing test-001-er-000003 (3 of 3).\n'
                    '\nScript is finished running.\n')
        self.assertEqual(expected, result, "Problem with test for general, print statements")

        # Test for the contents of the AIP directory.
        result = make_directory_list(aip_dir)
        bag_one = os.path.join(aip_dir, 'test-001-er-000001_bag')
        bag_two = os.path.join(aip_dir, 'test-001-er-000002_bag')
        bag_three = os.path.join(aip_dir, 'test-001-er-000003_bag')
        expected = [os.path.join(aip_dir, 'aip_log.csv'),
                    os.path.join(aip_dir, 'metadata.csv'),
                    bag_one,
                    os.path.join(bag_one, 'bag-info.txt'),
                    os.path.join(bag_one, 'bagit.txt'),
                    os.path.join(bag_one, 'data'),
                    os.path.join(bag_one, 'data', 'metadata'),
                    os.path.join(bag_one, 'data', 'metadata', 'Flower2.JPG_fits.xml'),
                    os.path.join(bag_one, 'data', 'metadata', 'test-001-er-000001_preservation.xml'),
                    os.path.join(bag_one, 'data', 'objects'),
                    os.path.join(bag_one, 'data', 'objects', 'Flower2.JPG'),
                    os.path.join(bag_one, 'manifest-md5.txt'),
                    os.path.join(bag_one, 'manifest-sha256.txt'),
                    os.path.join(bag_one, 'tagmanifest-md5.txt'),
                    os.path.join(bag_one, 'tagmanifest-sha256.txt'),
                    bag_two,
                    os.path.join(bag_two, 'bag-info.txt'),
                    os.path.join(bag_two, 'bagit.txt'),
                    os.path.join(bag_two, 'data'),
                    os.path.join(bag_two, 'data', 'metadata'),
                    os.path.join(bag_two, 'data', 'metadata', 'New Text Document.txt_fits.xml'),
                    os.path.join(bag_two, 'data', 'metadata', 'overview-tree.html_fits.xml'),
                    os.path.join(bag_two, 'data', 'metadata', 'test-001-er-000002_preservation.xml'),
                    os.path.join(bag_two, 'data', 'objects'),
                    os.path.join(bag_two, 'data', 'objects', 'New Text Document.txt'),
                    os.path.join(bag_two, 'data', 'objects', 'overview-tree.html'),
                    os.path.join(bag_two, 'manifest-md5.txt'),
                    os.path.join(bag_two, 'manifest-sha256.txt'),
                    os.path.join(bag_two, 'tagmanifest-md5.txt'),
                    os.path.join(bag_two, 'tagmanifest-sha256.txt'),
                    bag_three,
                    os.path.join(bag_three, 'bag-info.txt'),
                    os.path.join(bag_three, 'bagit.txt'),
                    os.path.join(bag_three, 'data'),
                    os.path.join(bag_three, 'data', 'metadata'),
                    os.path.join(bag_three, 'data', 'metadata', 'Test PDF.pdf_fits.xml'),
                    os.path.join(bag_three, 'data', 'metadata', 'test-001-er-000003_preservation.xml'),
                    os.path.join(bag_three, 'data', 'metadata', 'Worksheet.csv_fits.xml'),
                    os.path.join(bag_three, 'data', 'objects'),
                    os.path.join(bag_three, 'data', 'objects', 'Spreadsheet'),
                    os.path.join(bag_three, 'data', 'objects', 'Spreadsheet', 'Worksheet.csv'),
                    os.path.join(bag_three, 'data', 'objects', 'Test PDF.pdf'),
                    os.path.join(bag_three, 'manifest-md5.txt'),
                    os.path.join(bag_three, 'manifest-sha256.txt'),
                    os.path.join(bag_three, 'tagmanifest-md5.txt'),
                    os.path.join(bag_three, 'tagmanifest-sha256.txt')]
        self.assertEqual(expected, result, "Problem with test for general, aip directory")

        # Test for the contents of the staging directory.
        staging_dir = os.path.join(os.getcwd(), 'staging')
        today = datetime.date.today().strftime('%Y-%m-%d')
        result = make_directory_list(staging_dir)
        expected = [os.path.join(staging_dir, 'aips-already-on-ingest-server'),
                    os.path.join(staging_dir, 'aips-ready-to-ingest'),
                    os.path.join(staging_dir, 'aips-ready-to-ingest', f'manifest_aip_directory_test_{today}.txt'),
                    os.path.join(staging_dir, 'aips-ready-to-ingest', 'test-001-er-000001_bag.1000.tar.bz2'),
                    os.path.join(staging_dir, 'aips-ready-to-ingest', 'test-001-er-000002_bag.1000.tar.bz2'),
                    os.path.join(staging_dir, 'aips-ready-to-ingest', 'test-001-er-000003_bag.1000.tar.bz2'),
                    os.path.join(staging_dir, 'fits-xmls'),
                    os.path.join(staging_dir, 'fits-xmls', 'test-001-er-000001_combined-fits.xml'),
                    os.path.join(staging_dir, 'fits-xmls', 'test-001-er-000002_combined-fits.xml'),
                    os.path.join(staging_dir, 'fits-xmls', 'test-001-er-000003_combined-fits.xml'),
                    os.path.join(staging_dir, 'movs-to-bag'),
                    os.path.join(staging_dir, 'preservation-xmls'),
                    os.path.join(staging_dir, 'preservation-xmls', 'test-001-er-000001_preservation.xml'),
                    os.path.join(staging_dir, 'preservation-xmls', 'test-001-er-000002_preservation.xml'),
                    os.path.join(staging_dir, 'preservation-xmls', 'test-001-er-000003_preservation.xml')]
        self.assertEqual(expected, result, 'Problem with test for general, staging directory')

        # Test for the contents of the aip_log.csv file.
        result = make_aip_log_list(os.path.join(aip_dir, 'aip_log.csv'))
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made',
                     'Preservation.xml Valid', 'Bag Valid', 'Package Errors', 'Manifest Errors',
                     'Processing Complete'],
                    [today, 'test-001-er-000001', 'No files deleted', 'Successfully created objects folder',
                     'Successfully created metadata folder', 'No FITS tools errors',
                     'Successfully created combined-fits.xml', 'Successfully created preservation.xml',
                     f'Preservation.xml valid on {today}', f'Bag valid on {today}', 'Successfully made package',
                     'Successfully added AIP to manifest', 'Successfully completed processing'],
                    [today, 'test-001-er-000002', 'No files deleted', 'Successfully created objects folder',
                    'Successfully created metadata folder', 'No FITS tools errors',
                     'Successfully created combined-fits.xml', 'Successfully created preservation.xml',
                     f'Preservation.xml valid on {today}', f'Bag valid on {today}', 'Successfully made package',
                     'Successfully added AIP to manifest', 'Successfully completed processing'],
                    [today, 'test-001-er-000003', 'No files deleted', 'Successfully created objects folder',
                     'Successfully created metadata folder', 'No FITS tools errors',
                     'Successfully created combined-fits.xml', 'Successfully created preservation.xml',
                     f'Preservation.xml valid on {today}', f'Bag valid on {today}', 'Successfully made package',
                     'Successfully added AIP to manifest', 'Successfully completed processing']]
        self.assertEqual(expected, result, "Problem with test for general, aip log")

    def test_web(self):
        """Test for the web mode (content downloaded from Archive-It)"""
        # Makes a copy of the test files stored in the script repo, since the test will alter the files.
        shutil.copytree(os.path.join(os.getcwd(), 'script', 'web_mode'),
                        os.path.join(os.getcwd(), 'script', 'web'))

        # Runs the script.
        script_path = os.path.join('..', 'general_aip.py')
        aip_dir = os.path.join(os.getcwd(), 'script', 'web', 'preservation_download')
        printed = subprocess.run(f'python "{script_path}" "{aip_dir}" web zip',
                                 shell=True, capture_output=True, text=True)

        # Test for the script print statements.
        result = printed.stdout
        expected = ('\n>>>Processing rbrl-498-web-201907-0001 (1 of 2).\n'
                    '\n>>>Processing rbrl-377-web-201907-0001 (2 of 2).\n'
                    '\nScript is finished running.\n')
        self.assertEqual(expected, result, "Problem with test for web, print statements")

        # Test for the contents of the AIP directory.
        result = make_directory_list(aip_dir)
        bag_one = os.path.join(aip_dir, 'rbrl-377-web-201907-0001_bag')
        bag_two = os.path.join(aip_dir, 'rbrl-498-web-201907-0001_bag')
        expected = [os.path.join(aip_dir, 'aip_log.csv'),
                    os.path.join(aip_dir, 'metadata.csv'),
                    bag_one,
                    os.path.join(bag_one, 'bag-info.txt'),
                    os.path.join(bag_one, 'bagit.txt'),
                    os.path.join(bag_one, 'data'),
                    os.path.join(bag_one, 'data', 'metadata'),
                    os.path.join(bag_one, 'data', 'metadata',
                                 'ARCHIVEIT-12264-TEST-JOB943446-SEED2027776-20190710131748634-00000-h3.warc_fits.xml'),
                    os.path.join(bag_one, 'data', 'metadata', 'rbrl-377-web-201907-0001_31104250884_crawldef.csv'),
                    os.path.join(bag_one, 'data', 'metadata', 'rbrl-377-web-201907-0001_943446_crawljob.csv'),
                    os.path.join(bag_one, 'data', 'metadata', 'rbrl-377-web-201907-0001_coll.csv'),
                    os.path.join(bag_one, 'data', 'metadata', 'rbrl-377-web-201907-0001_collscope.csv'),
                    os.path.join(bag_one, 'data', 'metadata', 'rbrl-377-web-201907-0001_preservation.xml'),
                    os.path.join(bag_one, 'data', 'metadata', 'rbrl-377-web-201907-0001_seed.csv'),
                    os.path.join(bag_one, 'data', 'objects'),
                    os.path.join(bag_one, 'data', 'objects',
                                 'ARCHIVEIT-12264-TEST-JOB943446-SEED2027776-20190710131748634-00000-h3.warc'),
                    os.path.join(bag_one, 'manifest-md5.txt'),
                    os.path.join(bag_one, 'manifest-sha256.txt'),
                    os.path.join(bag_one, 'tagmanifest-md5.txt'),
                    os.path.join(bag_one, 'tagmanifest-sha256.txt'),
                    bag_two,
                    os.path.join(bag_two, 'bag-info.txt'),
                    os.path.join(bag_two, 'bagit.txt'),
                    os.path.join(bag_two, 'data'),
                    os.path.join(bag_two, 'data', 'metadata'),
                    os.path.join(bag_two, 'data', 'metadata',
                                 'ARCHIVEIT-12265-TEST-JOB943048-SEED2027707-20190709144234143-00000-h3.warc_fits.xml'),
                    os.path.join(bag_two, 'data', 'metadata', 'rbrl-498-web-201907-0001_31104250630_crawldef.csv'),
                    os.path.join(bag_two, 'data', 'metadata', 'rbrl-498-web-201907-0001_943048_crawljob.csv'),
                    os.path.join(bag_two, 'data', 'metadata', 'rbrl-498-web-201907-0001_coll.csv'),
                    os.path.join(bag_two, 'data', 'metadata', 'rbrl-498-web-201907-0001_collscope.csv'),
                    os.path.join(bag_two, 'data', 'metadata', 'rbrl-498-web-201907-0001_preservation.xml'),
                    os.path.join(bag_two, 'data', 'metadata', 'rbrl-498-web-201907-0001_seed.csv'),
                    os.path.join(bag_two, 'data', 'metadata', 'rbrl-498-web-201907-0001_seedscope.csv'),
                    os.path.join(bag_two, 'data', 'objects'),
                    os.path.join(bag_two, 'data', 'objects',
                                 'ARCHIVEIT-12265-TEST-JOB943048-SEED2027707-20190709144234143-00000-h3.warc'),
                    os.path.join(bag_two, 'manifest-md5.txt'),
                    os.path.join(bag_two, 'manifest-sha256.txt'),
                    os.path.join(bag_two, 'tagmanifest-md5.txt'),
                    os.path.join(bag_two, 'tagmanifest-sha256.txt')]
        self.assertEqual(expected, result, "Problem with test for web, aip directory")

        # Test for the contents of the staging directory.
        staging_dir = os.path.join(os.getcwd(), 'staging')
        today = datetime.date.today().strftime('%Y-%m-%d')
        result = make_directory_list(staging_dir)
        expected = [os.path.join(staging_dir, 'aips-already-on-ingest-server'),
                    os.path.join(staging_dir, 'aips-ready-to-ingest'),
                    os.path.join(staging_dir, 'aips-ready-to-ingest',
                                 f'manifest_preservation_download_russell_{today}.txt'),
                    os.path.join(staging_dir, 'aips-ready-to-ingest', 'rbrl-377-web-201907-0001_bag.1000.tar.bz2'),
                    os.path.join(staging_dir, 'aips-ready-to-ingest', 'rbrl-498-web-201907-0001_bag.1000.tar.bz2'),
                    os.path.join(staging_dir, 'fits-xmls'),
                    os.path.join(staging_dir, 'fits-xmls', 'rbrl-377-web-201907-0001_combined-fits.xml'),
                    os.path.join(staging_dir, 'fits-xmls', 'rbrl-498-web-201907-0001_combined-fits.xml'),
                    os.path.join(staging_dir, 'movs-to-bag'),
                    os.path.join(staging_dir, 'preservation-xmls'),
                    os.path.join(staging_dir, 'preservation-xmls', 'rbrl-377-web-201907-0001_preservation.xml'),
                    os.path.join(staging_dir, 'preservation-xmls', 'rbrl-498-web-201907-0001_preservation.xml')]
        self.assertEqual(expected, result, "Problem with test for web, staging directory")

        # Test for the contents of the aip_log.csv file.
        result = make_aip_log_list(os.path.join(aip_dir, 'aip_log.csv'))
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made',
                     'Preservation.xml Valid', 'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    [today, 'rbrl-498-web-201907-0001', 'No files deleted', 'Successfully created objects folder',
                     'Successfully created metadata folder', 'No FITS tools errors',
                     'Successfully created combined-fits.xml', 'Successfully created preservation.xml',
                     f'Preservation.xml valid on {today}', f'Bag valid on {today}', 'Successfully made package',
                     'Successfully added AIP to manifest', 'Successfully completed processing'],
                    [today, 'rbrl-377-web-201907-0001', 'No files deleted', 'Successfully created objects folder',
                     'Successfully created metadata folder', 'No FITS tools errors',
                     'Successfully created combined-fits.xml', 'Successfully created preservation.xml',
                     f'Preservation.xml valid on {today}', f'Bag valid on {today}', 'Successfully made package',
                     'Successfully added AIP to manifest', 'Successfully completed processing']]
        self.assertEqual(expected, result, "Problem with test for web, aip log")

    def test_error(self):
        """Test for there is an error with the initial checks and the script quits without running"""
        # Runs the script.
        script_path = os.path.join('..', 'general_aip.py')
        aip_dir = os.path.join(os.getcwd(), 'script', 'error')
        printed = subprocess.run(f'python "{script_path}" "{aip_dir}" type_error zip',
                                 shell=True, capture_output=True, text=True)

        # Test for the script print statements.
        result = printed.stdout
        expected = ('\nProblems detected with the provided script arguments:\n'
                    f'   * Provided aips_directory "{aip_dir}" is not a valid directory.\n'
                    '   * Provided aip_type "type_error" is not an expected value (av, general, web).\n'
                    '   * Cannot check for the metadata.csv because the AIPs directory has an error.\n')
        self.assertEqual(expected, result, "Problem with test for error")


if __name__ == "__main__":
    unittest.main()
