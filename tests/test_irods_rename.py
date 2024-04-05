import unittest
from pathlib import Path
import shutil
import logging

from rename import (
    get_list_of_files,
    check_which_files_need_rename,
    check_validity_of_rename_decision,
    check_possible_filename_switch,
    check_uniqueness_filenames,
    rename_files,
    create_output_directory,
)

logging.basicConfig(level=logging.INFO)


def convert_to_Path(d: dict):
    return {Path(k): Path(v) for k, v in d.items()}


class TestRename(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake_dirs = ["testdir/dir1", "testdir/dir2", "testdir/dir3", "test_sheets"]
        fake_files = [
            "testdir/dir1/file1.txt",
            "testdir/dir1/file2.txt",
            "testdir/dir2/file3.txt",
            "testdir/dir3/file4.txt",
        ]

        for d in fake_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)

        for f in fake_files:
            Path(f).touch()

        with open("test_sheets/rename_all.csv", "w") as f:
            f.write("dir1/file1.txt,dir1/file1_new.txt\n")
            f.write("dir1/file2.txt,dir1/file2_new.txt\n")
            f.write("dir2/file3.txt,dir2/file3_new.txt\n")
            f.write("dir3/file4.txt,dir3/file4_new.txt\n")

        with open("test_sheets/rename_single_file.csv", "w") as f:
            f.write("dir1/file1.txt,dir1/file1_new.txt\n")

        with open("test_sheets/rename_sheet_duplicate_new_filenames.csv", "w") as f:
            f.write("dir1/file1.txt,dir1/file1_new.txt\n")
            f.write("dir1/file2.txt,dir1/file1_new.txt\n")
            f.write("dir1/file3.txt,dir1/file3_new.txt\n")

        with open(
            "test_sheets/rename_sheet_duplicate_original_filenames.csv", "w"
        ) as f:
            f.write("dir1/file1.txt,dir1/file1_new.txt\n")
            f.write("dir1/file1.txt,dir1/file2_new.txt\n")
            f.write("dir1/file2.txt,dir1/file3_new.txt\n")

        with open("test_sheets/rename_sheet_missing_new_filenames.csv", "w") as f:
            f.write("dir1/file1.txt,dir1/file1_new.txt\n")
            f.write("dir1/file2.txt\n")

        with open("test_sheets/rename_sheet_missing_original_filenames.csv", "w") as f:
            f.write("dir1/file1.txt\n")
            f.write(",dir1/file1_new.txt\n")

        with open("test_sheets/rename_sheet_missing_comma.csv", "w") as f:
            f.write("dir1/file1.txt dir1/file1_new.txt\n")

        with open("test_sheets/filename_switch.csv", "w") as f:
            f.write("dir1/file1.txt,dir1/file2.txt\n")
            f.write("dir1/file2.txt,dir1/file1.txt\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("testdir")
        shutil.rmtree("test_sheets")

    def test_010_get_list_of_files(self):
        directory = Path("testdir")
        files = get_list_of_files(directory)
        self.assertEqual(len(files), 4)

    def test_020_check_which_files_need_rename(self):
        list_of_files = [
            "dir1/file1.txt",
            "dir1/file2.txt",
            "dir2/file3.txt",
            "dir3/file4.txt",
        ]
        rename_sheet = Path("test_sheets/rename_all.csv")
        rename_dict = check_which_files_need_rename(list_of_files, rename_sheet)
        correct_output = convert_to_Path(
            {
                "dir1/file1.txt": "dir1/file1_new.txt",
                "dir1/file2.txt": "dir1/file2_new.txt",
                "dir2/file3.txt": "dir2/file3_new.txt",
                "dir3/file4.txt": "dir3/file4_new.txt",
            }
        )
        self.assertEqual(rename_dict, correct_output)

    def test_030_check_which_files_need_rename_single_file(self):
        list_of_files = ["dir1/file1.txt"]
        rename_sheet = Path("test_sheets/rename_single_file.csv")
        rename_dict = check_which_files_need_rename(list_of_files, rename_sheet)
        correct_output = convert_to_Path({"dir1/file1.txt": "dir1/file1_new.txt"})
        self.assertEqual(rename_dict, correct_output)

    def test_040_check_which_files_need_rename_duplicate_new_filenames(self):
        list_of_files = ["dir1/file1.txt", "dir1/file2.txt"]
        rename_sheet = Path("test_sheets/rename_sheet_duplicate_new_filenames.csv")
        rename_dict = check_which_files_need_rename(list_of_files, rename_sheet)
        with self.assertRaises(ValueError):
            check_validity_of_rename_decision(rename_dict)

    def test_050_check_which_files_need_rename_duplicate_original_filenames(self):
        list_of_files = ["dir1/file1.txt", "dir1/file2.txt"]
        rename_sheet = Path("test_sheets/rename_sheet_duplicate_original_filenames.csv")
        with self.assertRaises(ValueError):
            rename_dict = check_which_files_need_rename(list_of_files, rename_sheet)

    def test_060_check_which_files_need_rename_missing_new_filenames(self):
        list_of_files = ["dir1/file1.txt", "dir1/file2.txt"]
        rename_sheet = Path("test_sheets/rename_sheet_missing_new_filenames.csv")
        with self.assertRaises(ValueError):
            rename_dict = check_which_files_need_rename(list_of_files, rename_sheet)

    def test_070_check_which_files_need_rename_missing_original_filenames(self):
        list_of_files = ["dir1/file1.txt", "dir1/file2.txt"]
        rename_sheet = Path("test_sheets/rename_sheet_missing_original_filenames.csv")
        with self.assertRaises(ValueError):
            rename_dict = check_which_files_need_rename(list_of_files, rename_sheet)

    def test_080_check_which_files_need_rename_missing_comma(self):
        from rename import check_which_files_need_rename

        list_of_files = ["dir1/file1.txt", "dir1/file2.txt"]
        rename_sheet = Path("test_sheets/rename_sheet_missing_comma.csv")
        with self.assertRaises(ValueError):
            rename_dict = check_which_files_need_rename(list_of_files, rename_sheet)

    def test_090_check_which_files_need_rename_filename_switch_rename_sheet(self):
        list_of_files = ["dir1/file1.txt", "dir1/file2.txt"]
        rename_sheet = Path("test_sheets/filename_switch.csv")
        rename_dict = check_which_files_need_rename(list_of_files, rename_sheet)
        with self.assertRaises(ValueError):
            check_validity_of_rename_decision(rename_dict)

    def test_100_check_uniqueness_filenames(self):
        unique_values = {
            "dir1/file1_new.txt",
            "dir1/file2_new.txt",
            "dir2/file3_new.txt",
            "dir3/file4_new.txt",
        }
        rename_decision_per_file = {
            "dir1/file1.txt": "dir1/file1_new.txt",
            "dir1/file2.txt": "dir1/file2_new.txt",
            "dir2/file3.txt": "dir2/file3_new.txt",
            "dir3/file4.txt": "dir3/file4_new.txt",
        }
        check_uniqueness_filenames(
            "new filenames", unique_values, rename_decision_per_file
        )

    def test_110_check_uniqueness_filenames_duplicate_new_filenames(self):
        unique_values = {
            "dir1/file1_new.txt",
            "dir1/file1_new.txt",
            "dir2/file3_new.txt",
            "dir3/file4_new.txt",
        }
        rename_decision_per_file = {
            "dir1/file1.txt": "dir1/file1_new.txt",
            "dir1/file2.txt": "dir1/file1_new.txt",
            "dir2/file3.txt": "dir2/file3_new.txt",
            "dir3/file4.txt": "dir3/file4_new.txt",
        }
        with self.assertRaises(ValueError):
            check_uniqueness_filenames(
                "new filenames", unique_values, rename_decision_per_file
            )

    def test_120_check_possible_filename_switch(self):
        rename_decision_per_file = {
            "dir1/file1.txt": "dir1/file2.txt",
            "dir1/file2.txt": "dir1/file1.txt",
        }
        with self.assertRaises(ValueError):
            check_possible_filename_switch(rename_decision_per_file)

    def test_130_check_possible_filename_switch_no_filename_switch(self):
        rename_decision_per_file = {
            "dir1/file1.txt": "dir1/file1_new.txt",
            "dir1/file2.txt": "dir1/file2_new.txt",
            "dir2/file3.txt": "dir2/file3_new.txt",
            "dir3/file4.txt": "dir3/file4_new.txt",
        }
        check_possible_filename_switch(rename_decision_per_file)

    def test_140_rename_files(self):
        rename_dict = {
            "dir1/file1.txt": "dir1/file1_new.txt",
            "dir1/file2.txt": "dir1/file2_new.txt",
            "dir2/file3.txt": "dir2/file3_new.txt",
            "dir3/file4.txt": "dir3/file4_new.txt",
        }
        input_dir = Path("testdir")
        output_dir = Path("testdir_renamed")
        files = [output_dir / f for f in rename_dict.values()]
        create_output_directory(input_dir, output_dir)
        rename_files(output_dir, rename_dict)
        for f in files:
            self.assertTrue(Path(f).exists())


if __name__ == "__main__":
    unittest.main()
