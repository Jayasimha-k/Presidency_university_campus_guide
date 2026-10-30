import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.knowledge_ingestion import read_sources, sources


class KnowledgeIngestionTests(unittest.TestCase):
    def test_future_txt_route_files_are_discovered_automatically(self):
        with tempfile.TemporaryDirectory() as directory:
            knowledge_dir = Path(directory)
            route_file = knowledge_dir / "future_routes.txt"
            route_file.write_text("ROUTE 999: Main Gate -> Gym", encoding="utf-8")
            (knowledge_dir / "notes.md").write_text("Not a source text file", encoding="utf-8")

            with patch("src.knowledge_ingestion.KNOWLEDGE_DIR", knowledge_dir):
                found = sources()
                loaded = read_sources()

        self.assertEqual([path.name for path in found], ["future_routes.txt"])
        self.assertEqual(loaded, [(route_file, "ROUTE 999: Main Gate -> Gym")])


if __name__ == "__main__":
    unittest.main()
