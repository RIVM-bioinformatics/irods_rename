# iRODS rename

This is a small tool that renames files based on sheet of old and new file names ("`.rename` sheet").

This was specifically designed and tested for the iRODS data management system used at the RIVM. The `.rename` sheet should be saved in the sample sheet directory, similar to the `.exclude` files for the Juno pipelines.

Any file in the old input collection which is not listed in the first column of the `.rename` sheet is copied as-is to the new collection. This script does this by copying the directory over the the new directory, and moving files within the new directory as instructed in the `.rename` file.