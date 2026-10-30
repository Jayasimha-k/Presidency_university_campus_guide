import unittest
from unittest.mock import patch

from src import campus_explorer, navigation
from modules import ai_assistant


class CampusExplorerAnswerTests(unittest.TestCase):
    def test_explorer_generates_answer_from_retrieved_campus_sources(self):
        docs = [{
            "source": "campus.txt",
            "chunk": 3,
            "text": "The gym is on the fifth floor of L Block.",
            "distance": 0.2,
        }]

        with patch.object(campus_explorer, "search", return_value=docs), \
                patch.object(campus_explorer, "matches", return_value=[{"filename": "gym.jpeg"}]) as matches, \
                patch.object(campus_explorer, "answer_with_context", return_value=("The gym is on L Block's fifth floor.", docs)) as generate:
            response, retrieved, images = campus_explorer.explore("Where is the gym?")

        self.assertIn("fifth floor", response)
        self.assertEqual(retrieved, docs)
        self.assertEqual(images, [{"filename": "gym.jpeg"}])
        generate.assert_called_once()
        self.assertEqual(generate.call_args.args[1], docs)
        self.assertIn("summarize", generate.call_args.kwargs["system_instruction"].lower())
        matches.assert_called_once()
        self.assertEqual(matches.call_args.kwargs["limit"], 1)

    def test_ai_assistant_does_not_render_images(self):
        with patch.object(ai_assistant, "answer", return_value=("The gym is on the fifth floor.", [])), \
                patch("modules.ai_assistant.st.image") as show_image, \
                patch("modules.ai_assistant.st.chat_input", return_value="Where is the gym?"):
            ai_assistant.render()

        show_image.assert_not_called()


class NavigationAnswerTests(unittest.TestCase):
    def test_navigation_generates_directions_only_from_endpoint_matching_sources(self):
        route = {
            "source": "routes.txt",
            "chunk": 7,
            "text": "ROUTE 40: MAIN GATE TO GYM\nStarting Point: Main Gate\nDestination: Gym\nRoute: Main Gate -> L Block -> Fifth Floor -> Gym",
            "distance": 0.2,
        }

        with patch.object(navigation, "search", return_value=[route]) as search, \
                patch.object(navigation, "answer_with_context", return_value=("Enter L Block and go to the fifth floor.", [route])) as generate:
            response, hits = navigation.directions_answer("Main Gate", "Gym")

        self.assertIn("fifth floor", response)
        self.assertEqual(hits, [route])
        self.assertEqual(search.call_args.kwargs["top_k"], 6)
        self.assertEqual(generate.call_args.args[1], [route])
        self.assertIn("Do not join separate routes", generate.call_args.kwargs["system_instruction"])

    def test_navigation_does_not_generate_when_no_source_matches_both_endpoints(self):
        route = {
            "source": "routes.txt",
            "chunk": 7,
            "text": "ROUTE 40: MAIN GATE TO LIBRARY\nStarting Point: Main Gate\nDestination: Library",
            "distance": 0.2,
        }

        with patch.object(navigation, "search", return_value=[route]), \
                patch.object(navigation, "answer_with_context", return_value=("No relevant information.", [])) as generate:
            response, hits = navigation.directions_answer("Main Gate", "Gym")

        self.assertEqual(hits, [])
        generate.assert_called_once()
        self.assertEqual(generate.call_args.args[1], [])

    def test_navigation_excludes_routes_that_only_pass_through_destination(self):
        source_chunk = {
            "source": "routes.txt",
            "chunk": 8,
            "text": (
                "ROUTE 077: L Block -> Gym\nL Block -> Fifth floor -> Gym\n\n"
                "ROUTE 078: Main Gate -> Gym\nMain Gate -> L Block -> Fifth floor -> Gym\n\n"
                "ROUTE 079: Registrar's Office -> Gym\nRegistrar's Office -> L Block -> Fifth floor -> Gym"
            ),
            "distance": 0.2,
        }

        with patch.object(navigation, "search", return_value=[source_chunk]):
            hits = navigation.find_directions("L Block", "Gym")

        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0]["text"].startswith("ROUTE 077:"))
        self.assertNotIn("ROUTE 078", hits[0]["text"])
        self.assertNotIn("ROUTE 079", hits[0]["text"])


if __name__ == "__main__":
    unittest.main()
