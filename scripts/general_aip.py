"""Purpose: Creates AIPs from folders of digital objects that are then ready for ingest into the UGA Libraries'
digital preservation system (ARCHive). The AIPs may contain one or multiple files of any format. The script works
with Hargrett and Russell library identifiers and Emory disk identifiers.

All workflow steps are done for one AIP before processing begins on the next. If an anticipated error is encountered
during processing, the AIP is moved to an error folder and the rest of the workflow steps are not executed for that
AIP. A log is generated while the script runs to record which AIPs were processed and any errors encountered.

Prior to running the script:
    1. The digital objects for each AIP should be in a folder named 'aip-id_AIP Title'
    2. All folders to be made into AIPs should be in a single folder (the AIPs directory).

Workflow Steps:
    1. Extracts the aip id, department, and aip title from the aip folder title.
    2. Deletes temporary files.
    3. Organizes folder contents into the UGA Libraries' AIP directory structure.
    4. Extracts technical metadata using FITS.
    5. Converts technical metadata to Dublin Core and PREMIS (preservation.xml file).
    6. Packages the AIP.
    7. When all AIPs are created (steps 1-6), makes a md5 manifest of the packaged AIPs.

Script usage: python '/path/general_aip.py' '/path/aips_directory'
Depending on how Python is installed on the machine, may need to substitute python3 for python.

This script has been tested on Windows 10 and Mac OS X (10.9.5).
"""

import datetime
import os
import re
import sys

import aip_functions as aip

# Assigns the script argument to the aips_directory variable and makes that the current directory.
# Ends the script if it is missing or not a valid directory.
try:
    aips_directory = sys.argv[1]
    os.chdir(aips_directory)
except (IndexError, FileNotFoundError):
    print('Unable to run the script: AIPs directory argument is missing or invalid.')
    print('Script usage: python "/path/general_aip.py" "/path/aips-directory"')
    exit()

# Starts a log for saving information about errors encountered while running the script. The log includes the date
# and time the script starts for calculating how long it takes the script to run.
log_path = f'../script_log_{datetime.date.today()}.txt'
aip.log(log_path, f'Starting AIP script at {datetime.datetime.today()}')

# Makes directories used to store script outputs in the same parent folder as the AIPs directory.
aip.make_output_directories()

# Starts counts for tracking script progress. Some steps are time consuming so this shows the script is not stuck.
current_aip = 0
total_aips = len(os.listdir(aips_directory))

# Uses the aip functions to create AIPs for one folder at a time. Checks if the AIP folder is still present before
# calling the function for the next step in case it was moved due to an error in the previous step.
for aip_folder in os.listdir(aips_directory):

    # Updates the current AIP number and displays the script progress.
    current_aip += 1
    aip.log(log_path, f'\n>>>Processing {aip_folder} ({current_aip} of {total_aips}).')
    print(f'\n>>>Processing {aip_folder} ({current_aip} of {total_aips}).')

    # Parses the AIP id, department, and AIP title from the folder name.
    #   * Prefix of harg or rbrl indicate a UGA department. Otherwise, department assigned after this.
    #   * AIP id is everything before the last underscore, include department if present.
    #   * AIP title is everything after the last underscore.
    regex = re.match('^((harg|rbrl)?[a-z0-9-_]+)_(?!.*_)(.*)', aip_folder)
    try:
        aip_id = regex.group(1)
        department = regex.group(2)
        aip_title = regex.group(3)
    except AttributeError:
        aip.log(log_path, 'Stop processing. Folder name not structured correctly.')
        aip.move_error('folder_name', aip_folder)
        continue

    # If the folder name did not include a UGA department prefix, department is partner.
    if department is None:
        department = "partner"

    # Renames the AIP folder to the AIP id. Only need the AIP title in the folder name to get the title for the
    # preservation.xml file.
    os.replace(aip_folder, aip_id)

    # Deletes temporary files. Remove the log_path parameter to not include a list of deleted files in the log.
    aip.delete_temp(aip_id, log_path)

    # Organizes the AIP folder contents into the UGA Libraries' AIP directory structure.
    if aip_id in os.listdir('.'):
        aip.structure_directory(aip_id, log_path)

    # Extracts technical metadata from the files using FITS.
    if aip_id in os.listdir('.'):
        aip.extract_metadata(aip_id, aips_directory, log_path)

    # Converts the technical metadata into Dublin Core and PREMIS (preservation.xml file) using xslt stylesheets.
    if aip_id in os.listdir('.'):
        aip.make_preservationxml(aip_id, aip_title, department, 'general', log_path)

    # Bags, tars, and zips the aip using bagit.py and a perl script.
    if aip_id in os.listdir('.'):
        aip.package(aip_id, log_path)

# Makes a MD5 manifest of all packaged AIPs in this batch using md5deep.
aip.make_manifest()

# Adds date and time the script was completed to the log.
aip.log(log_path, f'\nScript finished running at {datetime.datetime.today()}.')
