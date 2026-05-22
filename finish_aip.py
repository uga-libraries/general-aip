"""Finish a single AIP that is already in bag form and has had some manual edits

This is typically used when the preservation.xml needs to be edited to clean up format identifications
or address special characters that cannot be ingested into our preservation system.

To correct, validate the bag and edit as needed. Then run this script, which will have it ready to ingest into ARCHive.
The script will add to a manifest.txt file in the parent folder of the bag, so multiple AIPs can be ingested as a batch.

Parameter:
    bag_path (required): path to the bag to be finished into an AIP

Returns:
    .tar.bz2 version of the AIP ready to ingest into the preservation system
    manifest.txt with the md5 of the AIP needed for ingest
"""
import bagit
import sys


if __name__ == '__main__':

    # Get path to the bag to be made into a finished AIP (script argument) and read as a Bag.
    bag_path = sys.argv[1]
    bag_instance = bagit.Bag(bag_path)

    # Update the bag.
    bag_instance.save(manifests=True)

    # Validate the bag. If the bag is not valid, exit the script.

    # Package (tar and zip) the bag, including add the unzipped size to the filename.

    # Save the MD5 to the manifest.txt in the parent folder of bag_path,
    # adding to an existing manifest.txt if one is already present.