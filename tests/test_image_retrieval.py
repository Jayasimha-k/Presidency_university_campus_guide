import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.image_retrieval import matches, route_images


class ImageRetrievalTests(unittest.TestCase):
    def test_matches_photo_by_filename_without_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            image_dir = Path(directory) / "picture"
            image_dir.mkdir()
            (image_dir / "gym.jpeg").touch()
            metadata_file = Path(directory) / "image_metadata.json"
            metadata_file.write_text('{"images":[]}', encoding="utf-8")

            with patch("src.image_retrieval.IMAGE_DIR", image_dir), \
                    patch("src.image_retrieval.METADATA_FILE", metadata_file):
                result = matches("Where is the gym?")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["filename"], "gym.jpeg")
        self.assertEqual(result[0]["title"], "gym")

    def test_custom_metadata_overrides_filename_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            image_dir = Path(directory) / "picture"
            image_dir.mkdir()
            (image_dir / "gym.jpeg").touch()
            metadata_file = Path(directory) / "image_metadata.json"
            metadata_file.write_text(json.dumps({
                "images": [{
                    "filename": "gym.jpeg",
                    "title": "Campus fitness center",
                    "location": "L Block",
                    "keywords": ["exercise"],
                    "description": "User-provided description",
                }]
            }), encoding="utf-8")

            with patch("src.image_retrieval.IMAGE_DIR", image_dir), \
                    patch("src.image_retrieval.METADATA_FILE", metadata_file):
                result = matches("Where is the gym?")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Campus fitness center")
        self.assertEqual(result[0]["location"], "L Block")

    def test_exact_query_match_ranks_above_unrelated_context_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            image_dir = Path(directory) / "picture"
            image_dir.mkdir()
            (image_dir / "gym.jpeg").touch()
            (image_dir / "main_gate_student_entrance.jpeg").touch()
            metadata_file = Path(directory) / "image_metadata.json"
            metadata_file.write_text('{"images":[]}', encoding="utf-8")

            with patch("src.image_retrieval.IMAGE_DIR", image_dir), \
                    patch("src.image_retrieval.METADATA_FILE", metadata_file):
                result = matches("Where is the gym?", "Main Gate route through the Main Gate")

        self.assertEqual(result[0]["filename"], "gym.jpeg")

    def test_does_not_return_nonexistent_image(self):
        with tempfile.TemporaryDirectory() as directory:
            image_dir = Path(directory) / "picture"
            image_dir.mkdir()
            metadata_file = Path(directory) / "image_metadata.json"
            metadata_file.write_text(json.dumps({
                "images": [{"filename": "gym.jpeg", "keywords": ["gym"]}]
            }), encoding="utf-8")

            with patch("src.image_retrieval.IMAGE_DIR", image_dir), \
                    patch("src.image_retrieval.METADATA_FILE", metadata_file):
                result = matches("gym")

        self.assertEqual(result, [])

    def test_route_images_follow_stops_and_put_destination_last(self):
        with tempfile.TemporaryDirectory() as directory:
            image_dir = Path(directory) / "picture"
            image_dir.mkdir()
            for name in ("main_gate.jpeg", "right_side_footpath.jpeg", "E_block.jpeg", "gym.jpeg"):
                (image_dir / name).touch()
            metadata_file = Path(directory) / "image_metadata.json"
            metadata_file.write_text('{"images":[]}', encoding="utf-8")
            hit = {
                "source": "routes.txt",
                "chunk": 1,
                "text": "ROUTE 40: MAIN GATE TO GYM Starting Point: Main Gate Destination: Gym Route: Main Gate -> Right-side Campus Route -> E Block -> Fifth Floor -> Gym Directions: Enter the gate.",
            }

            with patch("src.image_retrieval.IMAGE_DIR", image_dir), \
                    patch("src.image_retrieval.METADATA_FILE", metadata_file):
                result = route_images([hit], "Main Gate", "Gym")

        self.assertEqual(
            [image["filename"] for image in result],
            ["main_gate.jpeg", "right_side_footpath.jpeg", "E_block.jpeg", "gym.jpeg"],
        )
        self.assertEqual(result[-1]["route_stop"], "Final destination")

    def test_route_stop_prefers_exact_place_photo_over_related_photo(self):
        with tempfile.TemporaryDirectory() as directory:
            image_dir = Path(directory) / "picture"
            image_dir.mkdir()
            (image_dir / "L_block.jpeg").touch()
            (image_dir / "f_block_towards_L_block_first_floor.jpeg").touch()
            (image_dir / "gym.jpeg").touch()
            metadata_file = Path(directory) / "image_metadata.json"
            metadata_file.write_text('{"images":[]}', encoding="utf-8")
            hit = {
                "source": "routes.txt",
                "chunk": 1,
                "text": "ROUTE 13: L BLOCK TO GYM Starting Point: L Block Destination: Gym Route: L Block -> Fifth Floor -> Gym Directions: Use the stairs.",
            }

            with patch("src.image_retrieval.IMAGE_DIR", image_dir), \
                    patch("src.image_retrieval.METADATA_FILE", metadata_file):
                result = route_images([hit], "L Block", "Gym")

        self.assertEqual(result[0]["filename"], "L_block.jpeg")
        self.assertEqual(result[-1]["filename"], "gym.jpeg")

    def test_route_images_extract_stops_from_legacy_arrow_record(self):
        with tempfile.TemporaryDirectory() as directory:
            image_dir = Path(directory) / "picture"
            image_dir.mkdir()
            for name in ("L_block.jpeg", "gym.jpeg"):
                (image_dir / name).touch()
            metadata_file = Path(directory) / "image_metadata.json"
            metadata_file.write_text('{"images":[]}', encoding="utf-8")
            hit = {
                "source": "legacy_routes.txt",
                "chunk": 1,
                "text": "ROUTE 077: L Block -> Gym L Block -> Fifth floor -> Gym and indoor sports area. Direction: use stairs. Destination: Gym.",
            }

            with patch("src.image_retrieval.IMAGE_DIR", image_dir), \
                    patch("src.image_retrieval.METADATA_FILE", metadata_file):
                result = route_images([hit], "L Block", "Gym")

        self.assertEqual([image["filename"] for image in result], ["L_block.jpeg", "gym.jpeg"])
        self.assertEqual(result[-1]["route_stop"], "Final destination")


if __name__ == "__main__":
    unittest.main()
