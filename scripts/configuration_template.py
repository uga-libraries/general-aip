# Local paths to programs used in the aip functions.
# The first three are dependencies and the stylesheets folder is part of this GitHub repo.

"""
To use, make a copy of this file named configuration.py and update the paths to match your local machine.
    C: may need to be replaced with a different drive letter.
    INSERT\\PATH\\ is replaced with the path on your local machine.
    # is replaced by the number for your version of the programs.

In a Mac or Linux environment:
    Use the path to fits.sh instead of fits.bat
    Change \\ to /
"""

FITS = 'C:\\INSERT\\PATH\\fits.bat'
SAXON = 'C:\\INSERT\\PATH\\saxon-he-#.#.jar'
MD5DEEP = 'C:\\INSERT\\PATH\\md5deep64.exe'
STYLESHEETS = 'C:\\INSERT\\PATH\\stylesheets'

# Namespace for the AIP identifiers.
# For UGA, this is the URI for the ARCHive.
NAMESPACE = 'INSERT_NAMESPACE'

# Department for AIP identifiers.
# For UGA, this is the group codes for ARCHive
GROUPS = ('INSERT_GROUP1', 'INSERT_GROUP2')
