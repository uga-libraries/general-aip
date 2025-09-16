# Local paths to programs used in the aip functions.

"""
To use, make a copy of this file named configuration.py and update the paths to match your local machine.
    C: may need to be replaced with a different drive letter.
    INSERT\\PATH\\ is replaced with the path on your local machine.
    # is replaced by the number for your version of the programs.

In a Mac or Linux environment:
    Use the path to fits.sh instead of fits.bat
    Change \\ to /
"""

# Consistent locations for saving script outputs.
# AIP_STAGING is for copies of metadata and INGEST_SERVER is where to save the zipped AIPs.
AIP_STAGING = 'C:\\INSERT\\PATH'
INGEST_SERVER = 'C:\\INSERT\\PATH'

# Dependencies. Stylesheets is a folder in the GitHub repo.
FITS = 'C:\\INSERT\\PATH\\fits.bat'
SAXON = 'C:\\INSERT\\PATH\\saxon-he-#.#.jar'
MD5DEEP = 'C:\\INSERT\\PATH\\md5deep64.exe'
STYLESHEETS = 'C:\\INSERT\\PATH\\general-aip\\stylesheets'

# Namespace for the AIP identifiers.
# For UGA, this is the URI for the ARCHive. It starts with http, not https
NAMESPACE = 'INSERT_NAMESPACE'

# Department for AIP identifiers.
# For UGA, this is the group codes for ARCHive
GROUPS = ('INSERT_GROUP1', 'INSERT_GROUP2')
