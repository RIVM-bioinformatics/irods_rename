#!/usr/bin/env python3

from pathlib import Path
import shutil
import logging


def get_list_of_files(directory):
    """
    Get a list of files in a directory.

    Params
    ------
    directory : Path
        The directory to list files from.

    Returns
    -------
    list
        A list of files in the directory.

    """
    logging.info(f"Getting list of files in {directory}")
    # recursively search for files and list relative paths
    list_of_files_and_dirs = list(directory.rglob("*"))
    trimmed_list_of_files = [
        f.relative_to(directory) for f in list_of_files_and_dirs if f.is_file()
    ]
    return trimmed_list_of_files


def check_which_files_need_rename(list_of_files, rename_sheet):
    """
    Check which files need to be renamed.

    Params
    ------
    list_of_files : list
        A list of files in the directory.
    rename_sheet : Path
        The path to the rename sheet.

    Returns
    -------
    dict
        A dictionary with the original filename as the key and the new filename as the value.

    Notes
    -----
    The rename sheet is a CSV file without a header that contains two columns: the original filename and the new filename.

    """
    logging.info(f"Reading rename sheet from {rename_sheet}")
    with open(rename_sheet, "r") as f:
        lines = f.readlines()
    logging.info(f"Checking which files need to be renamed")
    rename_dict = {}
    logging.info(f"Converting list_of_files to Path objects")
    list_of_files = [Path(f) for f in list_of_files]
    for line in lines:
        original_filename, new_filename = line.strip().split(",")
        logging.info(f"{original_filename} -> {new_filename}")
        if original_filename in list_of_files:
            logging.info(f"File {original_filename} also found in directory")
            rename_dict[original_filename] = new_filename
        else:
            logging.warning(
                f"File {original_filename} found in rename sheet {rename_sheet} but not in directory"
            )
    logging.info(f"Finished checking which files need to be renamed")
    return rename_dict


def main(args):
    list_of_input_files = get_list_of_files(args.input)
    rename_decision_per_file = check_which_files_need_rename(
        list_of_input_files, args.rename_sheet
    )
    logging.info(f"Copying files to {args.output}")
    for file in list_of_input_files:
        logging.info(f"Copying {file.name}")
        new_filename = rename_decision_per_file.get(file.name, None)
        logging.info(f"New filename: {new_filename}")
        if new_filename != None:
            logging.info(f"Copying {file.name} to {new_filename}")
            output_filepath = Path(args.output) / new_filename
            shutil.copy(file, output_filepath)
        else:
            logging.info(f"Copying {file.name} to {file.name}")
            output_filepath = Path(args.output) / file.name
            shutil.copy(file, output_filepath)
    logging.info(f"Finished copying files to {args.output}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Rename files in a directory")

    parser.add_argument("input", help="Input directory", type=Path)
    parser.add_argument("output", help="Output directory", type=Path)
    parser.add_argument("rename_sheet", help="Rename sheet", type=Path)

    args = parser.parse_args()

    main(args)
