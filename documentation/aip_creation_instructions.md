# AIP Creation Workflow, December 2023

## Overview

Transform a folder or group of folders into AIPs that meet the UGA Libraries AIP Definition, 
in preparation for ingest into our digital preservation system (ARCHive).

Each folder with the AIPs directory (specified via a script argument) will be transformed into a separate AIP.

## Responsibility

The Digital Archivist (Digital Stewardship) creates AIPs with this workflow for Hargrett and Russell born-digital archives.
The Head of Digital Stewardship creates AIPs with this workflow for UGA content in Archive-It. 
Both share responsibility for maintaining the script.

## Workflow

1. Preparation 

   1. Copy FITS to the same letter drive as the files and update configuration.py if needed.
   2. Organize the contents of each AIP into one folder per AIP.
      - An AIP many contain files of any format and additional folders.
      - Limit AIP size and the number of formats for more sustainable ongoing management.
   3. Copy the AIP folders into a single folder (aips_directory). 
      Use a copy in case there is a problem with the script.
   4. Make the metadata.csv file for this batch (see [metadata.csv example](metadata.csv)) and save it to the aips_directory.


2. Run the script. The script will:

   1. Extract the AIP metadata from the metadata.csv.
   2. Delete temporary files from anywhere within the AIP folder because they cause errors with validating bags.
   3. Create the AIP directory structure: folder named with the AIP ID that contains metadata and objects folders.
   4. Extract technical metadata from each file in the objects folder with FITS and save it to the metadata folder. 
   5. Combine each FITS xml file into one file named combined-fits.xml and save it to the fits-xml folder.
   6. Make the preservation.xml file (Dublin Core and PREMIS) from the combined-fits xml and values from metadata.csv and save it to the metadata folder. 
   7. Validate that the preservation.xml file meets UGA standards.
   8. Use bagit to bag each AIP folder in place, with md5 and sha256 manifests.
   9. Validate the bag.
   10. Tar and zip a copy of the bag and save it to the aips-to-ingest folder.
   11. Calculate the MD5 for the tarred and zipped AIP and add it to the department manifest in the aips-to-ingest folder.


3. Quality Control

   1. Review the log and errors folder and address any problems.
   2. Zip the contents of the preservation-xml folder and batch validate with the ARCHive application.
   3. Follow department procedures to review a sample of the AIPs for accuracy.


4. Schedule the AIPs for ingest into ARCHive.


5. Once AIPs are ingested without errors, delete local copies of the AIPs.

## History

This workflow has been in use since 2020 by the Hargrett and Russell libraries. 