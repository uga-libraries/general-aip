"""Purpose: Creates AIPs from folders of digital objects that are then ready for ingest into the
UGA Libraries' digital preservation system (ARCHive). The AIPs may contain one or multiple files
of any format. The script works with Hargrett and Russell library IDs and Emory disk image IDs.

All workflow steps are done for one AIP before processing begins on the next.
If an anticipated error is encountered during processing, the AIP is moved to an error folder
and the rest of the workflow steps are not executed for that AIP. A log is generated while
the script runs to record which AIPs were processed and any errors encountered.

Prior to running the script:
    1. Make one folder per AIP with the digital objects for those AIPs.
    2. All folders to be made into AIPs should be in a single folder (the AIPs directory).
    3. Make a file named metadata.csv in the AIPs directory. See README for what to include.

Workflow Steps:
    1. Extracts the information about each AIP from metadata.csv.
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

import aip_functions as a
import configuration as c

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

# Verifies all the paths from the configuration file are valid. If not, ends the script.
valid_errors = a.check_paths()
if not valid_errors == "no errors":
    print('The following path(s) in the configuration file are not correct:')
    for error in valid_errors:
        print(error)
    print('Correct the configuration file and run the script again.')
    sys.exit()

# Reads the CSV with the AIP metadata.
open_metadata = open(aip_metadata_csv)
read_metadata = csv.reader(open_metadata)

# Verifies the metadata header row has the expected values and matches the folders in the AIPs directory.
# If there is an error, ends the script.
metadata_errors = a.check_metadata_csv(read_metadata)
if not metadata_errors == "no_errors":
    for error in metadata_errors:
        print(error)
    sys.exit()

# Starts a log for saving information about events and errors from running the script and adds a header row.
a.log(['Time Started', 'AIP ID', 'Department Correct', 'Deleted Temp Files', 'Error: Objects folder exists',
       'Error: metadata folder exists', 'FITS Tool Errors', 'Preservation.xml Made', 'Preservation Valid', 'Bag Valid',
       'Tar Made', 'Processing Complete'])

# Makes directories used to store script outputs in the same parent folder as the AIPs directory.
a.make_output_directories()

# Starts counts for tracking script progress.
# Some steps are time consuming so this shows the script is not stuck.
# Subtracts one from the count for the metadata file.
# If the AIPs directory already contains the output folders and log, the total will be too high.
CURRENT_AIP = 0
TOTAL_AIPS = len(os.listdir(AIPS_DIRECTORY)) - 1

# Returns to the beginning of the CSV and skips the header
open_metadata.seek(0)
next(read_metadata)

# Uses the AIP functions to create an AIP for each one in the metadata CSV.
# Checks if the AIP folder is still present before calling the function for the next step
# in case it was moved due to an error in the previous step.
for aip_row in read_metadata:

    # Makes an instance of the AIP class using metadata from the CSV.
    department, collection_id, aip_folder, aip_id, title, version = aip_row
    aip = a.AIP(department, collection_id, aip_folder, aip_id, title, version, ZIP)

    # Updates the current AIP number and displays the script progress.
    CURRENT_AIP += 1
    print(f'\n>>>Processing {aip.id} ({CURRENT_AIP} of {TOTAL_AIPS}).')

    # Verifies the department matches one of the required group codes. If not, starts the next AIP.
    if aip.department not in c.GROUPS:
        aip.log = [datetime.datetime.now(), aip.id, 'No', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'No: error']
        a.log(aip.log)
        a.move_error('department_not_group', aip.folder_name)
        continue
    else:
        aip.log.append("Yes")

    # Renames the folder to the AIP ID.
    # Already know from check_metadata_csv() that every AIP in the CSV is in the AIPs directory.
    if aip.folder_name in os.listdir('.'):
        os.replace(aip.folder_name, aip.id)

    # Deletes temporary files and makes a log of deleted files which is saved in the metadata folder.
    a.delete_temp(aip)

    # Organizes the AIP folder contents into the UGA Libraries' AIP directory structure.
    if aip.id in os.listdir('.'):
        a.structure_directory(aip)

    # Extracts technical metadata from the files using FITS.
    if aip.id in os.listdir('.'):
        a.extract_metadata(aip, AIPS_DIRECTORY)

    # Converts the technical metadata into Dublin Core and PREMIS using xslt stylesheets.
    if aip.id in os.listdir('.'):
        a.make_preservationxml(aip, 'general')

    # Bags the AIP using bagit.
    if aip.id in os.listdir('.'):
        a.bag(aip)

    # Tars the AIP and also zips (bz2) the AIP if ZIP is True.
    # Adds the packaged AIP to the MD5 manifest in the aips-to-ingest folder.
    if f'{aip.id}_bag' in os.listdir('.'):
        a.package(aip, AIPS_DIRECTORY)

    if f'{aip.id}_bag' in os.listdir('.'):
        a.manifest(aip)

    # Logs that the AIP is complete. No anticipated errors were encountered.
    if f'{aip.id}_bag' in os.listdir('.'):
        aip.log.append("Yes: No detected errors")
        a.log(aip.log)

# Closes the metadata CSV.
open_metadata.close()

print("\nScript is finished running.")
