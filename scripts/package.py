# Purpose: Bags, tars, and zips each aip.

# Dependencies: bagit.py, prepare_bag perl script        

import os
import subprocess
import sys
from aip_variables import move_error, aip_scripts


# The aip id is an argument when this script is run from aips.py.
# It is used to identify the folder the script should work on.
aip = sys.argv[1]


# Bags the aip folder in place.
# Both md5 and sha256 checksums are generated to guard against tampering.
subprocess.run(f'bagit.py --md5 --sha256 --quiet "{aip}"', shell=True)


#Renames the aip folder to add _bag to the end.
os.replace(aip, f'{aip}_bag')
    

# Validates the bag.
# If it is not valid, moves the aip to an error folder and quits this script.
validation = subprocess.run(f'bagit.py --validate "{aip}_bag"', stderr=subprocess.PIPE, shell=True)

if 'is invalid' in str(validation.stderr):
    move_error('bag_invalid', f'{aip}_bag')
    exit()
        

# Tars and zips the aip using a perl script.
# The script also adds the uncompressed file size to the file name.
# The tarred and zipped aip is saved to the aips-to-ingest folder.
subprocess.run(f'"{aip_scripts}/prepare_bag" "{aip}_bag" "../aips-to-ingest"', shell=True)
