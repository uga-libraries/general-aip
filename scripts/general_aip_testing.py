"""Purpose: Creates AIPs from folders of digital objects but purposefully generates errors.
Used for testing error handling in the script general_aip.py script.

Prior to running the script:
    1. Make one folder per AIP with the digital objects for those AIPs.
    2. All folders to be made into AIPs should be in a single folder (the AIPs directory).
    3. Make a file named metadata.csv in the AIPs directory. See README for what to include.
"""

# Script usage: python '/path/general_aip.py' '/path/aips_directory'

import csv
import os
import sys
import aip_functions as a

# ---------------------------------------------------------------------------------------
# THIS PART OF THE SCRIPT IS FOR TESTING SCRIPT INPUTS AND IS IDENTICAL TO general_aip.py
# IT MAKES SURE THERE ARE NO SETUP ERRORS BEFORE BEGINNING TO TEST THE DESIRED ERRORS
# ---------------------------------------------------------------------------------------

# Verifies the script arguments are correct and calculates the associated variables.
# If there are errors, ends the script.
AIPS_DIRECTORY, ZIP, aip_metadata_csv, argument_errors = a.check_arguments(sys.argv)
if len(argument_errors) > 0:
    print('The script cannot be run because of the following error(s):')
    for error in argument_errors:
        print("* " + error)
    print('\nScript usage: python "/path/general_aip.py" "/path/aips-directory" [no-zip]')
    sys.exit()

# Makes the current directory the AIPs directory
os.chdir(AIPS_DIRECTORY)

# Verifies all the variables from the configuration file are present and all the paths are valid.
# If not, ends the script.
configuration_errors = a.check_configuration()
if len(configuration_errors) > 0:
    print('\nProblems detected with configuration.py:')
    for error in configuration_errors:
        print(error)
    print('\nCorrect the configuration file and run the script again. Use configuration_template.py as a model.')
    sys.exit()

# Reads the CSV with the AIP metadata.
open_metadata = open(aip_metadata_csv)
read_metadata = csv.reader(open_metadata)

# Verifies the metadata header row has the expected values and matches the folders in the AIPs directory.
# If there is an error, ends the script.
metadata_errors = a.check_metadata_csv(read_metadata)
if len(metadata_errors) > 0:
    print('\nProblems detected with metadata.csv')
    for error in metadata_errors:
        print(error)
    print('\nCorrect the metadata.csv and run the script again.')
    sys.exit()

# If there isn't already a log from running this script on a previous batch,
# starts a log for saving information about events and errors from running the script and adds a header row.
if not os.path.exists('../general_aip_script_log.csv'):
    a.log("header")

# Makes directories used to store script outputs in the same parent folder as the AIPs directory.
a.make_output_directories()

# Starts counts for tracking script progress.
# Some steps are time consuming so this shows the script is not stuck.
# Subtracts one from the count for the metadata file.
CURRENT_AIP = 0
TOTAL_AIPS = len(os.listdir(AIPS_DIRECTORY)) - 1

# Returns to the beginning of the CSV (the script is at the end because of checking it for errors) and skips the header.
open_metadata.seek(0)
next(read_metadata)


# ---------------------------------------------------------------------------------------
# THE REST OF THE SCRIPT CREATES EACH KNOWN ERROR TO TEST IT IS CAUGHT AND LOGGED CORRECTLY.
# ---------------------------------------------------------------------------------------

# Uses the AIP functions to create an AIP for each folder in the metadata CSV.
# Supplies alternative to AIP function when needed to generate an error.
# Even though don't expect the rest of the steps to run after an error, include the code for it just in case.
for aip_row in read_metadata:

    # Makes an instance of the AIP class using metadata from the CSV and global variables.
    department, collection_id, aip_folder, aip_id, title, version = aip_row
    aip = a.AIP(AIPS_DIRECTORY, department, collection_id, aip_folder, aip_id, title, version, ZIP)

    # Updates the current AIP number and displays the script progress in the terminal.
    CURRENT_AIP += 1
    print(f'\n>>>Processing {aip.id} ({CURRENT_AIP} of {TOTAL_AIPS}).')

    # Renames the folder to the AIP ID.
    os.replace(aip.folder_name, aip.id)

    # Deletes any temporary files and makes a log of each deleted file.
    a.delete_temp(aip)

    # Use the first AIP to catch if an objects folder already exists.
    if CURRENT_AIP == 1:

        # Produce error: add a folder named objects to the aip folder.
        os.mkdir(f"{aip.id}/objects")

        # Organizes the AIP folder contents into the UGA Libraries' AIP directory structure (objects and metadata).
        # Should give an error.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)

        # Remaining workflow steps. Should not run.
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # Use the second AIP to catch if a metadata folder already exists.
    if CURRENT_AIP == 2:

        # Produce error: add a folder named objects to the aip folder.
        os.mkdir(f"{aip.id}/metadata")

        # Organizes the AIP folder contents into the UGA Libraries' AIP directory structure (objects and metadata).
        # Should give an error.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)

        # Remaining workflow steps. Should not run.
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)
