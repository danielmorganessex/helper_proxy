import unittest
import subprocess
import os
import shutil
import sys

# Use the same Python interpreter for the subprocess that is running this test script
PYTHON_EXECUTABLE = sys.executable
SCRIPT_TO_TEST = "recursive_copy.py"

class TestRecursiveCopy(unittest.TestCase):

    def setUp(self):
        """Clean up any leftover directories before each test."""
        self.source_dir = os.path.abspath("test_source_dir_rc")
        self.dest_dir = os.path.abspath("test_dest_dir_rc")
        self.cleanup()

    def tearDown(self):
        """Clean up directories after each test."""
        self.cleanup()

    def cleanup(self):
        """Removes source and destination test directories."""
        if os.path.exists(self.source_dir):
            shutil.rmtree(self.source_dir)
        if os.path.exists(self.dest_dir):
            shutil.rmtree(self.dest_dir)

    def create_source_files(self, modifications=None):
        """Creates a standard set of source files and directories."""
        os.makedirs(os.path.join(self.source_dir, "subdir1"), exist_ok=True)

        with open(os.path.join(self.source_dir, "file1.txt"), "w") as f:
            f.write("Content of file1")
        with open(os.path.join(self.source_dir, "file2.txt"), "w") as f:
            f.write("Content of file2")
        with open(os.path.join(self.source_dir, "subdir1", "file3.txt"), "w") as f:
            f.write("Content of file3 in subdir1")

        if modifications:
            if "update_file1" in modifications:
                with open(os.path.join(self.source_dir, "file1.txt"), "w") as f:
                    f.write(modifications["update_file1"])
            if "new_file_path" in modifications and "new_file_content" in modifications:
                 with open(os.path.join(self.source_dir, modifications["new_file_path"]), "w") as f:
                    f.write(modifications["new_file_content"])


    def run_script(self, source, dest):
        """Runs the recursive_copy.py script."""
        return subprocess.run([PYTHON_EXECUTABLE, SCRIPT_TO_TEST, source, dest],
                              capture_output=True, text=True)

    def assert_file_content(self, filepath, expected_content):
        self.assertTrue(os.path.exists(filepath), f"File {filepath} does not exist.")
        with open(filepath, "r") as f:
            actual_content = f.read()
        self.assertEqual(actual_content, expected_content, f"Content mismatch for {filepath}")

    def test_successful_copy(self):
        """Test basic successful copy of directory tree."""
        self.create_source_files()

        result = self.run_script(self.source_dir, self.dest_dir)
        self.assertEqual(result.returncode, 0, f"Script failed with stderr: {result.stderr}")

        # Verify structure and content
        self.assertTrue(os.path.exists(self.dest_dir))
        self.assert_file_content(os.path.join(self.dest_dir, "file1.txt"), "Content of file1")
        self.assert_file_content(os.path.join(self.dest_dir, "file2.txt"), "Content of file2")
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "subdir1")))
        self.assert_file_content(os.path.join(self.dest_dir, "subdir1", "file3.txt"), "Content of file3 in subdir1")

    def test_source_not_exists(self):
        """Test handling of a non-existent source directory."""
        non_existent_source = os.path.join(self.source_dir, "non_existent")
        # Ensure it truly doesn't exist (setUp might create self.source_dir parent)
        if os.path.exists(non_existent_source):
             shutil.rmtree(non_existent_source)

        result = self.run_script(non_existent_source, self.dest_dir)

        # The main script logs an error and exits, but argparse might exit with code 2
        # and the script itself might exit via return in main() which is exit code None (implicitly 0 for subprocess if not set by sys.exit)
        # For now, let's check if stderr contains "does not exist" and dest_dir is not created.
        # A more robust way would be for the main script to use sys.exit(1) on error.
        self.assertIn("does not exist", result.stderr.lower() + result.stdout.lower(), "Error message for non-existent source not found in script output.")
        self.assertFalse(os.path.exists(self.dest_dir), "Destination directory was created even though source did not exist.")
        # If the script used sys.exit(1) for errors, we could assert result.returncode != 0

    def test_overwrite_behavior(self):
        """Test that existing files are overwritten and new files are added."""
        # 1. Initial copy
        self.create_source_files()
        initial_result = self.run_script(self.source_dir, self.dest_dir)
        self.assertEqual(initial_result.returncode, 0, f"Initial copy failed: {initial_result.stderr}")
        self.assert_file_content(os.path.join(self.dest_dir, "file1.txt"), "Content of file1")

        # 2. Modify source
        updated_content_file1 = "Updated content of file1"
        new_file_in_subdir_path = os.path.join("subdir1", "new_file4.txt")
        new_file_in_subdir_content = "Content of new_file4 in subdir1"

        self.create_source_files(modifications={
            "update_file1": updated_content_file1,
            "new_file_path": new_file_in_subdir_path,
            "new_file_content": new_file_in_subdir_content
        })

        # 3. Run copy again
        overwrite_result = self.run_script(self.source_dir, self.dest_dir)
        self.assertEqual(overwrite_result.returncode, 0, f"Overwrite copy failed: {overwrite_result.stderr}")

        # 4. Verify changes
        self.assert_file_content(os.path.join(self.dest_dir, "file1.txt"), updated_content_file1)
        self.assert_file_content(os.path.join(self.dest_dir, "subdir1", "file3.txt"), "Content of file3 in subdir1") # Original file in subdir
        self.assert_file_content(os.path.join(self.dest_dir, new_file_in_subdir_path), new_file_in_subdir_content)


if __name__ == '__main__':
    unittest.main()
