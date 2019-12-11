""" 
Purpose: Creates aips from folders of digital objects that are then ready for ingest into the UGA Libraries' digital preservation system (ARCHive). The aips may contain one or multiple files of any format. The scripts work with Hargrett and Russell libraries identifiers.

Script steps:
    1. Verifies arguments are correct.
    2. Makes folders for script outputs (siblings of aips directory).
    3. Organizes folders into the aip directory structure: metadata folder and objects folder with the digital objects.
    4. Extracts technical metadata using FITS.
    5. Converts technical metadata to PREMIS (master.xml) using stylesheets.
    6. Packages the aips: bag, tar, and zip.
    7. Makes a md5 manifest of all packaged aips.

Script usage: python3 '/path/aip.py' '/path/aips-directory' department

Dependencies: bagit.py, FITS, md5deep, saxon, xmllint

Prior to running the script:
    1. The digital objects for each aip should be in a folder named 'aip-id_AIP Title'
    2. All folders to be made into aips should be in a single folder (the aips directory).
"""

import os
import re
import subprocess
import sys
from aip_variables import aip_scripts, move_error


# Script usage message for providing instruction if the arguments are not correct.
usage = "To run the script: python3 '/path/aips.py' '/path/aips-directory' department"


# Gets the aips directory and department from script arguments.
# The aips directory contains all the folders to be made into aips.
# The department is used by stylesheets in master_xml.py to match identifier patterns.
# Ends the script if either argument is missing.
try:
    aips_directory = sys.argv[1]
    department = sys.argv[2]
except IndexError:
    print('Incorrect number of arguments. Should be aips directory and department.')
    print(usage)
    exit()


# Changes the current directory to the aips directory.
# Ends the script if the directory doesn't exist.
try:
    os.chdir(aips_directory)
except FileNotFoundError:
    print(f'The aips directory "{aips_directory}" does not exist.')
    print(usage)
    exit()


# Confirms the department code is "hargrett" or "russell".
# Ends the script if it is not.
if not(department == 'hargrett' or department == 'russell'):
    print(f'"{department}" is not an expected department. Should be "hargrett" or "russell".')
    print(usage)
    exit()


# Makes directories used to store script outputs, if they aren't already there.
# These are made in the same parent folder as the aips directory.

if not os.path.exists('../master-xml'):
    os.mkdir('../master-xml')

if not os.path.exists('../fits-xml'):
    os.mkdir('../fits-xml')

if not os.path.exists('../aips-to-ingest'):
    os.mkdir('../aips-to-ingest')


# Starts counts for tracking script progress.
total_aips = len(os.listdir(aips_directory))
current_aip = 0


# For one aip at a time, runs the scripts for all of the workflow steps.
# If a known error occurs, the aip is moved to a folder with the error name and the rest of the steps are not completed for it.
# Checks if the aip is still present before running each script in case it was moved due to an error in the previous script.
for aip in os.listdir(aips_directory):
     
    #Updates the current aip number and displays the script progress.
    current_aip += 1
    print(f'\n>>>Processing {aip} ({current_aip} of {total_aips}).')
 

    # Parses the aip id and aip title from the folder name.
    # The aip id is everything before the first underscore and can include lowercase letters, numbers and dashes.
    # The aip title is everything after the first underscore and can include any character.
    # Moves the aip to an error folder if the name doesn't match this pattern.
    try:
        regex = re.match('^([a-z\d-]+)_(.*)', aip)
    except AttributeError:
        move_error('folder_title', aip)
        continue

    aip_id = regex.group(1)
    aip_title = regex.group(2)


    # Renames the aip folder to just the aip id.
    # Only include the aip title in the folder to get the title for making the master.xml.
    os.replace(aip, aip_id)  


    # Deletes unwanted files and organizes the rest into the aip directory structure.
    if aip_id in os.listdir('.'):
        subprocess.run(f'python3 "{aip_scripts}/directory.py" "{aip_id}"', shell=True)


    # Extracts technical metadata from the files using FITS.
    if aip_id in os.listdir('.'):
        subprocess.run(f'python3 "{aip_scripts}/fits.py" "{aip_id}"', shell=True)


    # Transforms the FITS metadata into the PREMIS master.xml file using saxon and xslt stylesheets.
    if aip_id in os.listdir('.'):
        subprocess.run(f'python3 "{aip_scripts}/master_xml.py" "{aip_id}" "{aip_title}" "{department}"', shell=True)


    # Bags, tars, and zips the aip using bagit.py and a perl script.
    if aip_id in os.listdir('.'):
        subprocess.run(f'python3 "{aip_scripts}/package.py" "{aip_id}"', shell=True)


# Makes a MD5 manifest of all aips the in this batch using md5deep.
# The manifest is named manifest.txt and saved in the aips-to-ingest folder.
# The manifest has one line per aip, formatted md5<tab>filename
os.chdir('../aips-to-ingest')
subprocess.run(f'md5deep -b * > manifest.txt', shell=True)


print('\nScript is finished running.')
