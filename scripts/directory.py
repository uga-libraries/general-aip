# Purpose: Makes the aip directory (objects and metadata folder within the aip folder) and moves the digital objects into the objects folder.
# If the digital objects are organized into folders, that directory structure is maintained within the objects folder.

import os
import sys
from aip_variables import move_error


# The aip id is an argument when this script is run from aips.py.
# It is used to identify the folder the script should work on.
aip = sys.argv[1]


# Deletes temporary files from anywhere within the aip folder because they cause errors in the workflow.
# "if item in delete" matches the filename to any name in the delete list.
# "item.endswith('.tmp')" matches any file that has a .tmp file extension.
# "item.startswith('.')" matches any file that starts with ., which is generated when copying from a Mac to Windows.
delete = ['.DS_Store', '._.DS_Store', 'Thumbs.db']

for root, directories, files in os.walk('.'):
    for item in files:
        if item in delete or item.endswith('.tmp') or item.startswith('.'):
            os.remove(f'{root}/{item}')


# Makes the objects folder within the aip folder, if it doesn't exist.
# If there is already a folder named objects in the first level within the aip folder, moves the aip to an error folder and quits this script.
# Do not want to alter the original directory structure by adding to an original folder named objects.
try:
    os.mkdir(f'{aip}/objects')
except FileExistsError:
    move_error('objects_exists', aip)
    exit()


# Moves the contents of the aip folder into the objects folder.
# Skips the objects folder with continue. Do not want to try to move objects into itself.
for item in os.listdir(aip):
    if item == 'objects':
        continue
    os.replace(f'{aip}/{item}', f'{aip}/objects/{item}')

    
# Makes the metadata folder within the aip folder, if it doesn't exist.
# If there is already a folder named metadata in the first level within the aip folder, moves the aip to an error folder.
# If this happens, there was an error in the previous step when everything should have been moved to the objects folder.
try:
    os.mkdir(f'{aip}/metadata')
except FileExistsError:
    move_error('metadata_exists', aip)
