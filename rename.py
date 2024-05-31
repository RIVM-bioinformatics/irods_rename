#!/usr/bin/env python3

from pathlib import Path
import shutil
import subprocess
import logging
from version import __version__


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
        try:
            original_filename, new_filename = line.strip().split(",")
        except ValueError:
            if line.strip() == "":
                raise ValueError("Empty line in rename sheet")
            elif "," not in line:
                raise ValueError(
                    f"Line {line} in rename sheet does not contain a comma"
                )
            else:
                raise ValueError(
                    f"Line {line} in rename sheet is not in the correct format"
                )
        original_filename = Path(original_filename)
        new_filename = Path(new_filename)
        logging.info(f"Rename instruction: {original_filename} -> {new_filename}")
        if original_filename in list_of_files:
            logging.info(
                f"File {original_filename} also found in directory, including in rename decision dictionary"
            )
            if original_filename in rename_dict:
                raise ValueError(
                    f"File {original_filename} found in rename sheet {rename_sheet} more than once"
                )
            else:
                rename_dict[original_filename] = new_filename
        else:
            logging.warning(
                f"File {original_filename} found in rename sheet {rename_sheet} but not in directory"
            )
    logging.info(f"Finished checking which files need to be renamed")
    return rename_dict


def check_uniqueness_filenames(label, unique_values, rename_decision_per_file):
    """
    Check whether the new filenames are unique.

    Params
    ------
    label : str
        A label for raising a possible error.
    unique_values : set
        A set of unique values.
    rename_decision_per_file : dict
        A dictionary with the original filename as the key and the new filename as the value.

    Raises
    ------
    ValueError
        If the filenames are not unique.

    """
    logging.info(f"Checking uniqueness of {label}")
    if len(unique_values) != len(rename_decision_per_file):
        logging.error(f"{label} are not unique")
        raise ValueError(f"{label} are not unique")


def check_possible_filename_switch(rename_decision_per_file):
    """
    Check if there are any filename switches in the rename decision.

    Params
    ------
    rename_decision_per_file : dict
        A dictionary with the original filename as the key and the new filename as the value.

    Raises
    ------
    ValueError
        If there are filename switches in the rename decision.

    """
    # filter out entries where the new filename is the same as the original filename
    rename_dict_filtered = {
        original_filename: new_filename
        for original_filename, new_filename in rename_decision_per_file.items()
        if original_filename != new_filename
    }
    # check if any new filename is the same as an original filename of another entry
    new_filenames_filtered = set(rename_dict_filtered.values())
    original_filenames_filtered = set(rename_dict_filtered.keys())
    if len(new_filenames_filtered.intersection(original_filenames_filtered)) > 0:
        logging.error(
            f"Some entries have new filenames that are the same as original filenames for other entries"
        )
        raise ValueError(
            "Some entries have new filenames that are the same as original filenames for other entries"
        )


def check_validity_of_rename_decision(rename_decision_per_file):
    """
    Perform some checks on the validiy of rename decisions.

    Params
    ------
    rename_decision_per_file : dict
        A dictionary with the original filename as the key and the new filename as the value.

    """
    logging.info(f"Checking validity of rename decision")
    check_uniqueness_filenames(
        "new filenames",
        set(rename_decision_per_file.values()),
        rename_decision_per_file,
    )
    check_uniqueness_filenames(
        "old filenames", set(rename_decision_per_file.keys()), rename_decision_per_file
    )
    check_possible_filename_switch(rename_decision_per_file)
    logging.info(f"Rename decision is valid")


def create_output_directory(input_directory, output_directory):
    """
    Create an output directory and copy the contents of the input directory to it.

    Params
    ------
    input_directory : Path
        The input directory.
    output_directory : Path
        The output directory.

    Returns
    -------
    None

    """
    # if output_directory.exists():
    #     logging.info(
    #         f"Output directory {output_directory} already exists, removing before copying"
    #     )
    #     shutil.rmtree(output_directory)
    # shutil.copytree(input_directory, output_directory, dirs_exist_ok=True)
    # use glob of input directory to copy files
    output_directory.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-r", f"{str(input_directory)}/*", str(output_directory)])


def rename_files(output_directory, rename_decision_per_file):
    """
    Rename files in the output directory.

    Params
    ------
    output_directory : Path
        The output directory.
    rename_decision_per_file : dict
        A dictionary with the original filename as the key and the new filename as the value.

    Returns
    -------
    None

    """
    for old_filename, new_filename in rename_decision_per_file.items():
        old_filepath = output_directory / old_filename
        new_filepath = output_directory / new_filename
        new_filepath.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Renaming {old_filepath} to {new_filepath}")
        old_filepath.rename(new_filepath)


def main(args):
    list_of_input_files = get_list_of_files(args.input)
    logging.info(f"Found files {list_of_input_files}")
    rename_decision_per_file = check_which_files_need_rename(
        list_of_input_files, args.rename_sheet
    )
    check_validity_of_rename_decision(rename_decision_per_file)
    create_output_directory(args.input, args.output)
    logging.info(f"Copying files to {args.output}")
    rename_files(args.output, rename_decision_per_file)

    logging.info(f"Finished copying files to {args.output}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Rename files in a directory")

    parser.add_argument("input", help="Input directory", type=Path)
    parser.add_argument("output", help="Output directory", type=Path)
    parser.add_argument("rename_sheet", help="Rename sheet", type=Path)
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    main(args)
