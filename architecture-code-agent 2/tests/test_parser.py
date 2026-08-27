import unittest
from pathlib import Path

from code_agent.parser import ArchitectureParser


ROOT = Path(__file__).resolve().parents[1]


class ArchitectureParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = ArchitectureParser().parse_files(
            ROOT / "inputs" / "Architecture_Documentation.md",
            ROOT / "inputs" / "Architecture_View.md",
        )

    def test_extracts_system_and_requirements(self):
        self.assertEqual(self.result["system"], "Space Fractions")
        self.assertEqual(self.result["requirements"], ["ASR-1", "ASR-2", "FR-1", "NFR-1"])

    def test_extracts_components(self):
        self.assertIn("GameComponent", self.result["components"])
        self.assertIn("QuestionComponent", self.result["components"])

    def test_extracts_all_plantuml_blocks(self):
        diagrams = self.result["views"]["diagrams"]
        self.assertEqual(len(diagrams), 13)
        self.assertEqual(diagrams[0]["name"], "UseCaseDiagram")
        self.assertIn("User->>Game: play()", [d["syntax"] for d in diagrams if d["name"] == "SequenceDiagram1"][0])

    def test_json_output_ends_with_newline(self):
        self.assertTrue(ArchitectureParser.to_json(self.result).endswith("\n"))


if __name__ == "__main__":
    unittest.main()
