import tempfile
import unittest
from pathlib import Path

from code_agent.cli import main


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_parse_command_writes_json(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "architecture.json"
            exit_code = main(
                [
                    "parse",
                    "--architecture",
                    str(ROOT / "inputs" / "Architecture_Documentation.md"),
                    "--views",
                    str(ROOT / "inputs" / "Architecture_View.md"),
                    "--json-out",
                    str(output),
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertIn('"Space Fractions"', output.read_text(encoding="utf-8"))

    def test_clean_refuses_to_delete_input_containing_directory(self):
        with self.assertRaises(SystemExit):
            main(
                [
                    "generate",
                    "--architecture",
                    str(ROOT / "inputs" / "Architecture_Documentation.md"),
                    "--views",
                    str(ROOT / "inputs" / "Architecture_View.md"),
                    "--output",
                    str(ROOT),
                    "--clean",
                ]
            )


if __name__ == "__main__":
    unittest.main()
