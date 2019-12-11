# Purpose: Extracts technical metadata from the files in the objects folder using FITS (one xml per file) and creates a single xml file that combines the FITS output for every file in the aip. 

# Dependencies: FITS

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from aip_variables import fits, move_error


# The aip id is an argument when this script is run from aips.py.
# It is used to identify the folder the script should work on.
aip = sys.argv[1]


# Runs FITS on every file in the aip's objects folder.
# Saves the output, which is one xml per file, to the aip's metadata folder.
subprocess.run(f'"{fits}" -r -i "{aip}/objects" -o "{aip}/metadata"', shell=True)

       
# Renames the FITS output according to the UGA Libraries' metadata naming convention.
# FITS output is named filename.fits.xml
# The desired name is filename_fits.xml
for item in os.listdir(f'{aip}/metadata'):
    if item.endswith('.fits.xml'):
        new_name = item.replace('.fits', '_fits')
        os.rename(f'{aip}/metadata/{item}', f'{aip}/metadata/{new_name}')


# The rest of this script copies the FITS output into a single xml file.

# Makes a new xml object with the root element named combined-fits.
combo_tree = ET.ElementTree(ET.Element('combined-fits'))
combo_root = combo_tree.getroot()

# Gets each of the FITS documents in the aip's metadata folder.
for doc in os.listdir(f'{aip}/metadata'):
    if doc.endswith('_fits.xml'):
 
        # Makes Python aware of the FITS namespace.        
        ET.register_namespace('', "http://hul.harvard.edu/ois/xml/ns/fits/fits_output")

        # Gets the FITS element (and all its children) and makes it a child of the xml object's root.
        # If there is an error, moves the aip to an error folder.
        try:
            tree = ET.parse(f'{aip}/metadata/{doc}')
            root = tree.getroot()
            combo_root.append(root)
        except:
            move_error('fits_combining', aip)
            exit()

# Saves the xml object, which now contains all the FITS elements, to a file named aip-id_combined-fits.xml in the aip's metadata folder.
combo_tree.write(f'{aip}/metadata/{aip}_combined-fits.xml', xml_declaration = True, encoding = 'UTF-8')
