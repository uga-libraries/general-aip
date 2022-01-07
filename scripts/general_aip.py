"""Purpose: Creates AIPs from folders of digital objects that are then ready for ingest into the
UGA Libraries' digital preservation system (ARCHive). The AIPs may contain one or multiple files
of any format. The script works with Hargrett and Russell library IDs and Emory disk image IDs.

All workflow steps are done for one AIP before processing begins on the next.
If an anticipated error is encountered during processing, the AIP is moved to an error folder
and the rest of the workflow steps are not executed for that AIP. A log is generated while
the script runs to record which AIPs were processed and any errors encountered.

Prior to running the script:
    1. The digital objects for each AIP should be in a folder named with the AIP title.'
    2. All folders to be made into AIPs should be in a single folder (the AIPs directory).
    3. Make a file named metadata.csv in the AIPs directory with the department, collection id, AIP id, and title.

Workflow Steps:
    1. Extracts the department, collection id, AIP id, and title from metadata.csv.
    2. Deletes temporary files.
    3. Organizes folder contents into the UGA Libraries' AIP directory structure.
    4. Extracts technical metadata using FITS.
    5. Converts technical metadata to Dublin Core and PREMIS (preservation.xml file).
    6. Packages the AIP (bag, tar, zip).
    7. Adds the md5 for the packaged AIP to the department's md5 manifest.

Script usage: python '/path/general_aip.py' '/path/aips_directory' [no-zip]
Depending on how Python is installed on the machine, may need to substitute python3 for python.
Use the optional argument no-zip for batches of AIPs that should only be tarred.

This script has been tested on Windows 10 and Mac OS X (10.9.5).
"""

import csv
import datetime
import os
import sys

import aip_functions as aip
import configuration as c

# Assigns the required script argument to the aips_directory variable and makes that the current directory.
# Ends the script if it is missing or not a valid directory.
try:
    AIPS_DIRECTORY = sys.argv[1]
    os.chdir(AIPS_DIRECTORY)
except (IndexError, FileNotFoundError):
    print('Unable to run the script: AIPs directory argument is missing or invalid.')
    print('Script usage: python "/path/general_aip.py" "/path/aips-directory" [no-zip]')
    sys.exit()

# If the optional script argument no-zip is present, updates the zip variable to False.
# This is for AIPs that are larger when zipped and should only be tarred to save space and time.
ZIP = True
if len(sys.argv) == 3:
    if sys.argv[2] == "no-zip":
        ZIP = False
    else:
        print('Unexpected value for the second argument. If provided, should be "no-zip".')
        print('Script usage: python "/path/general_aip.py" "/path/aips-directory" [no-zip]')
        sys.exit()

# Verifies all the paths from the configuration file are valid. If not, ends the script.
valid_errors = aip.check_paths()
if not valid_errors == "no errors":
    print('The following path(s) in the configuration file are not correct:')
    for error in valid_errors:
        print(error)
    print('Correct the configuration file and run the script again.')
    sys.exit()

# Verifies the required metadata CSV is present. If not, ends the script.
aip_metadata_csv = os.path.join(AIPS_DIRECTORY, "metadata.csv")
if not os.path.exists(aip_metadata_csv):
    print('Unable to run the script: missing the required metadata file.')
    print('To run the script, include a file named metadata.csv in the AIPs directory.')
    sys.exit()

# Starts a log for saving information about errors encountered while running the script.
# The log includes the script start time for calculating how long it takes the script to run.
LOG_PATH = f'../script_log_{datetime.date.today()}.txt'
aip.log(LOG_PATH, f'Starting AIP script at {datetime.datetime.today()}')

# Makes directories used to store script outputs in the same parent folder as the AIPs directory.
aip.make_output_directories()

# Starts counts for tracking script progress.
# Some steps are time consuming so this shows the script is not stuck.
# Subtracts one from the count for the metadata file.
# If the AIPs directory already contains the output folders and log, the total will be too high.
CURRENT_AIP = 0
TOTAL_AIPS = len(os.listdir(AIPS_DIRECTORY)) - 1

# Reads the CSV with the AIP metadata.
open_metadata = open(aip_metadata_csv)
read_metadata = csv.reader(open_metadata)

# Verifies the metadata header row has the expected values (case insensitive).
# If columns are not in the right order, it ends the script.
header = next(read_metadata)
header_lowercase = [name.lower() for name in header]
if header_lowercase != ['department', 'collection', 'folder', 'aip_id', 'title']:
    print("The columns in the metadata.csv are not in the required order.")
    print("Required order: Department, Collection, Folder, AIP_ID, Title")
    print(f"Current order:  {', '.join(header)}")
    sys.exit()

# Matches the number of rows in the metadata.csv (minus the header) to the number of folders in the AIPs directory.
# If the two do not have the same number, it ends the script.
row_count = sum(1 for row in read_metadata)
folder_count = len([name for name in os.listdir('.') if os.path.isdir(name)])

if row_count != folder_count:
    print(f'There are {row_count} AIPs in the metadata.csv and {folder_count} folders in the AIPs directory.')
    print('The metadata.csv needs to match the folders in the AIPs directory.')
    sys.exit()

# Returns to the beginning of the CSV and skips the header
open_metadata.seek(0)
next(read_metadata)

# Uses the AIP functions to create an AIP for each one in the metadata CSV.
# Checks if the AIP folder is still present before calling the function for the next step
# in case it was moved due to an error in the previous step.
for aip_row in read_metadata:

    # Saves AIP metadata from the CSV to variables.
    department, collection_id, aip_folder, aip_id, title = aip_row

    # Updates the current AIP number and displays the script progress.
    CURRENT_AIP += 1
    aip.log(LOG_PATH, f'\n>>>Processing {aip_id} ({CURRENT_AIP} of {TOTAL_AIPS}).')
    print(f'\n>>>Processing {aip_id} ({CURRENT_AIP} of {TOTAL_AIPS}).')

    # Verifies the department matches one of the required group codes. If not, starts, the next AIP.
    if department not in c.GROUPS:
        aip.log(LOG_PATH, f'Stop processing. Department in metadata.csv ({department}) is not an ARCHive group code.')
        aip.move_error('department_not_group', aip_folder)
        continue

    # Renames the folder to the AIP ID. If the AIP folder is not found, starts the next AIP.
    try:
        os.replace(aip_folder, aip_id)
    except FileNotFoundError:
        aip.log(LOG_PATH, f'Unable to process. AIP folder is in metadata.csv but not the AIPs directory.')
        continue

    # Deletes temporary files.
    # For Emory AIPs, makes a log of deleted files which is saved in the metadata folder.
    if department == "emory":
        aip.delete_temp(aip_id, deletion_log=True)
    else:
        aip.delete_temp(aip_id)

    # Organizes the AIP folder contents into the UGA Libraries' AIP directory structure.
    if aip_id in os.listdir('.'):
        aip.structure_directory(aip_id, LOG_PATH)

    # Extracts technical metadata from the files using FITS.
    if aip_id in os.listdir('.'):
        aip.extract_metadata(aip_id, AIPS_DIRECTORY, LOG_PATH)

    # Converts the technical metadata into Dublin Core and PREMIS using xslt stylesheets.
    if aip_id in os.listdir('.'):
        aip.make_preservationxml(aip_id, collection_id, title, department, 'general', LOG_PATH)

    # Bags the AIP using bagit.
    if aip_id in os.listdir('.'):
        aip.bag(aip_id, LOG_PATH)

    # Tars the AIP and also zips (bz2) the AIP if ZIP is True.
    # Adds the packaged AIP to the MD5 manifest in the aips-to-ingest folder.
    if f'{aip_id}_bag' in os.listdir('.'):
        aip.package_and_manifest(aip_id, AIPS_DIRECTORY, department, ZIP)

# Closes the metadata CSV.
open_metadata.close()

# Adds date and time the script was completed to the log.
aip.log(LOG_PATH, f'\nScript finished running at {datetime.datetime.today()}.')
print("\nScript is finished running.")
