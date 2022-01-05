"""Purpose: bag, tar, and zip AIPs which are already have the correct AIP directory structure (metadata and objects
folders) and all metadata correctly generated, including the preservation.xml file. This is used when AIPs are
created using the usual script (general_aip.py) but have an error in the preservation.xml that must be corrected by
hand.

Before running this script (could do as part of the script later):
    * Delete the bag metadata files
    * Move the objects and metadata files out of the data folder
    * Delete the data folder.
    * Delete the size and _bag from the AIP folder title. It will now be the AIP ID.

This script currently works on one AIP at a time but could easily be adapted to work on a batch.

Script usage: python '/path/package_only.py' '/path/aip_to_package' department [no-zip]"""

import datetime
import os
import sys
import aip_functions as aip

# PART ONE: ARGUMENT CHECKING

# Ends the script if the required AIP path argument is missing.
try:
    AIP_PATH = sys.argv[1]
except IndexError:
    print("Unable to run the script: AIP path argument is missing.")
    print("python '/path/package_only.py' '/path/aip_to_package' department [no-zip]")
    sys.exit()

# Ends the script if the AIP path argument is not correct.
if not os.path.exists(AIP_PATH):
    print(f"Unable to run the script: the provided AIP path argument is not valid: {AIP_PATH}")
    print("python '/path/package_only.py' '/path/aip_to_package' department [no-zip]")
    sys.exit()

# Ends the script if the required department argument is not present.
try:
    DEPARTMENT = sys.argv[2]
except IndexError:
    print("Unable to run the script: department argument is missing.")
    print("python '/path/package_only.py' '/path/aip_to_package' department [no-zip]")
    sys.exit()

# If the optional script argument no-zip is present, updates the zip variable to False.
# This is for AIPs that are larger when zipped and should only be tarred to save space and time.
ZIP = True
if len(sys.argv) == 4:
    if sys.argv[3] == "no-zip":
        ZIP = False
    else:
        print(f'Unexpected value for the second argument: "{sys.argv[3]}". If provided, should be "no-zip".')
        print('Script usage: python "/path/general_aip.py" "/path/aips-directory" [no-zip]')
        sys.exit()

# PART TWO: MAKE ADDITIONAL NEEDED VARIABLES

# The AIPs directory is the folder that contains the AIP.
AIPS_DIRECTORY = os.path.dirname(AIP_PATH)
os.chdir(AIPS_DIRECTORY)

# The AIP ID is the last part of the AIP PATH.
AIP_ID = os.path.basename(AIP_PATH)

# The log will be made in the AIPs directory to save script errors.
LOG_PATH = f'{AIPS_DIRECTORY}/log_{AIP_ID}_{datetime.date.today()}.txt'

# Makes a folder in the parent folder of the AIPs directory for the final AIP.
if not os.path.exists('../aips-to-ingest'):
    os.mkdir(f'../aips-to-ingest')

# PART THREE: USE AIP FUNCTIONS TO BAG, TAR, AND ZIP THE AIP.

# Bags the AIP using bagit.
print('Starting to bag')
aip.bag(AIP_ID, LOG_PATH)

# Tars the AIP and also zips (bz2) the AIP if ZIP is True.
# Adds the packaged AIP to the MD5 manifest in the aips-to-ingest folder.
if f'{AIP_ID}_bag' in os.listdir('.'):
    print('Starting to package')
    aip.package(AIP_ID, AIPS_DIRECTORY, DEPARTMENT, ZIP)
