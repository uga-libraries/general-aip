"""Purpose: Creates AIPs from folders of digital objects that are then ready for ingest into the
UGA Libraries' digital preservation system (ARCHive). The AIPs may contain one or multiple files
of any format. The script works with Hargrett and Russell library IDs and Emory disk IDs.

All workflow steps are done for one AIP before processing begins on the next.
If an anticipated error is encountered during processing, the AIP is moved to an error folder
and the rest of the workflow steps are not executed for that AIP. A log is generated while
the script runs to record which AIPs were processed and any errors encountered.

Prior to running the script:
    1. The digital objects for each AIP should be in a folder named 'aip-id_AIP Title'
    2. All folders to be made into AIPs should be in a single folder (the AIPs directory).

Workflow Steps:
    1. Extracts the aip id, department, and aip title from the aip folder title.
    2. Deletes temporary files.
    3. Organizes folder contents into the UGA Libraries' AIP directory structure.
    4. Extracts technical metadata using FITS.
    5. Converts technical metadata to Dublin Core and PREMIS (preservation.xml file).
    6. Packages the AIP (bag, tar, zip).
    7. When all AIPs are created (steps 1-6), makes a md5 manifest of the packaged AIPs.

Script usage: python '/path/general_aip.py' '/path/aips_directory' [no-zip]
Depending on how Python is installed on the machine, may need to substitute python3 for python.
Use the optional argument no-zip for batches of AIPs that should only be tarred.

This script has been tested on Windows 10 and Mac OS X (10.9.5).
"""

import datetime
import os
import re
import sys

import aip_functions as aip

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

# Starts a in log for saving information about errors encountered while running the script.
# The log includes the script start time for calculating how long it takes the script to run.
LOG_PATH = f'../script_log_{datetime.date.today()}.txt'
aip.log(LOG_PATH, f'Starting AIP script at {datetime.datetime.today()}')

# Makes directories used to store script outputs in the same parent folder as the AIPs directory.
aip.make_output_directories()

# Starts counts for tracking script progress.
# Some steps are time consuming so this shows the script is not stuck.
# If the AIPs directory already contains the output folders and log, the total will be too high.
CURRENT_AIP = 0
TOTAL_AIPS = len(os.listdir(AIPS_DIRECTORY))

# Uses the aip functions to create AIPs for one folder at a time.
# Checks if the AIP folder is still present before # calling the function for the next step
# in case it was moved due to an error in the previous step.
for aip_folder in os.listdir(AIPS_DIRECTORY):

    # Skip output folders and log, if present from running the script previously.
    if aip_folder in ["aips-to-ingest", "fits-xml", "preservation-xml"] or aip_folder.startswith("script_log"):
        continue

    # Updates the current AIP number and displays the script progress.
    CURRENT_AIP += 1
    aip.log(LOG_PATH, f'\n>>>Processing {aip_folder} ({CURRENT_AIP} of {TOTAL_AIPS}).')
    print(f'\n>>>Processing {aip_folder} ({CURRENT_AIP} of {TOTAL_AIPS}).')

    # Parses the department, AIP id, and AIP title from the folder name.
    #   * Prefix indicates the UGA department or partner institution.
    #   * AIP id is everything before the last underscore, include department if present.
    #   * AIP title is everything after the last underscore.
    regex = re.match('^((harg|rbrl|emory)[_|-][a-z0-9-_]+)_(?!.*_)(.*)', aip_folder)
    try:
        aip_id = regex.group(1)
        department = regex.group(2)
        aip_title = regex.group(3)
    except AttributeError:
        aip.log(LOG_PATH, 'Stop processing. Folder name not structured correctly.')
        aip.move_error('folder_name', aip_folder)
        continue

    # Renames the AIP folder to the AIP ID.
    # Only need the AIP title in the folder name to get the title for the preservation.xml file.
    os.replace(aip_folder, aip_id)

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
        aip.make_preservationxml(aip_id, aip_title, department, 'general', LOG_PATH)

    # Bags the AIP using bagit.
    if aip_id in os.listdir('.'):
        aip.bag(aip_id, LOG_PATH)

    # Tars the AIP and zips (bz2) the AIP if ZIP is True.
    if f'{aip_id}_bag' in os.listdir('.'):
        aip.package(aip_id, AIPS_DIRECTORY, ZIP)

# Makes a MD5 manifest of all packaged AIPs in this batch using md5deep.
aip.make_manifest()

# Adds date and time the script was completed to the log.
aip.log(LOG_PATH, f'\nScript finished running at {datetime.datetime.today()}.')
print("Script is finished running.")
