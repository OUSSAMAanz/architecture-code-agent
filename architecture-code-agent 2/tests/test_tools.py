import json
import tempfile
import unittest
from pathlib import Path

from code_agent.tools import SafeWorkspace, ToolError


class SafeWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.workspace = SafeWorkspace(Path(self.tempdir.name))

    def tearDown(self):
        self.tempdir.cleanup()

    def test_write_read_and_list(self):
        self.workspace.write_file("src/app.py", "print('hello')\n")
        self.assertEqual(self.workspace.read_file("src/app.py"), "print('hello')\n")
        self.assertIn("src/app.py", json.loads(self.workspace.list_files()))

    def test_rejects_parent_traversal(self):
        with self.assertRaises(ToolError):
            self.workspace.write_file("../escape.txt", "no")

    def test_rejects_absolute_path(self):
        with self.assertRaises(ToolError):
            self.workspace.read_file("/etc/passwd")

    def test_rejects_sensitive_paths(self):
        with self.assertRaises(ToolError):
            self.workspace.write_file(".env", "TOKEN=secret")

    def test_rejects_unknown_tool(self):
        with self.assertRaises(ToolError):
            self.workspace.execute("shell", {"command": "echo unsafe"})


if __name__ == "__main__":
    unittest.main()
