# Purpose: defines variables and a function that are used by other aip scripts.

import os
import sys


# Gives the absolute filepath for programs and files used by the script.

#   fits is the path to the fits.sh file. Script tested with FITS 1.4.1.
#   saxon is the path to the saxon jar file. Script tested with Saxon HE9-9-1-1J.
#   aip scripts is the folder with the python scripts for this workflow.
#   workflowdocs is the folder with stylesheets, xds, and perl script for this workflow.

fits = 'INSERT-PATH'
saxon = 'INSERT-PATH'
aip_scripts = 'INSERT-PATH'
stylesheets = 'INSERT-PATH'

   
# Function to move the aip folder to an error folder.
# The error folder is named with the error type.
# Moving the aip prevents the rest of the workflow steps from being completed on it.

def move_error(error_name, item):
    if not os.path.exists(f'../errors/{error_name}'):
        os.makedirs(f'../errors/{error_name}')
    os.replace(item, f'../errors/{error_name}/{item}')
