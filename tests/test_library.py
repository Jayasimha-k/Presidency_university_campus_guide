import unittest
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

from modules import library
from src import vector_store


class LibraryAssistantTests(unittest.TestCase):
    def test_library_sources_include_campus_routes_and_named_library_uploads(self):
        paths = [
            Path("C:/knowledge_base/campus_directions1.txt"),
            Path("C:/knowledge_base/uploads/upload_123_library_rules.txt"),
            Path("C:/knowledge_base/transport_information.txt"),
        ]
        with patch.object(library, "sources", return_value=paths), \
                patch.object(library, "source_name", side_effect=lambda path: path.name):
            result = library.library_sources()

        self.assertEqual(result, ["campus_directions1.txt", "upload_123_library_rules.txt"])

    def test_library_answers_search_only_library_sources_and_pass_history(self):
        docs = [{
            "source": "campus_directions1.txt",
            "chunk": 3,
            "text": "The Technical Library is on the first floor of M Block.",
            "distance": 0.2,
        }]
        history = [{"role": "user", "content": "Where is the library?"}]
        library_sources = ["campus_directions1.txt", "uploads/library_rules.txt"]

        with patch.object(library, "library_sources", return_value=library_sources), \
                patch.object(library, "search", return_value=docs) as search, \
                patch.object(library, "answer_with_context", return_value=("First floor, M Block.", docs)) as generate:
            response, retrieved = library.answer("What facilities does it have?", history)

        self.assertIn("M Block", response)
        self.assertEqual(retrieved, docs)
        search.assert_called_once_with(
            "What facilities does it have?",
            top_k=6,
            source=library_sources,
        )
        self.assertEqual(generate.call_args.kwargs["history"], history)
        self.assertIn("opening hours", generate.call_args.kwargs["system_instruction"])

    def test_vector_search_supports_multiple_library_sources(self):
        class FakeCollection:
            query_args = None

            def count(self):
                return 3

            def query(self, **kwargs):
                self.query_args = kwargs
                return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        collection = FakeCollection()
        with patch.object(vector_store, "collection", return_value=collection), \
                patch.object(vector_store, "embed_texts", return_value=[[0.0, 1.0]]):
            vector_store.search(
                "Technical Library facilities",
                source=["campus_directions1.txt", "uploads/library_rules.txt"],
            )

        self.assertEqual(collection.query_args["where"], {
            "source": {"$in": ["campus_directions1.txt", "uploads/library_rules.txt"]}
        })

    def test_library_assistant_does_not_render_images(self):
        state = {
            "library_history": [
                {
                    "role": "assistant",
                    "content": "The Technical Library is on the first floor.",
                    "sources": [{"source": "library.txt", "chunk": 1, "text": "Technical Library"}],
                }
            ]
        }
        with patch.object(library.st, "session_state", state), \
                patch.object(library.st, "title"), \
                patch.object(library.st, "write"), \
                patch.object(library.st, "button", return_value=False), \
                patch.object(library.st, "chat_input", return_value=None), \
                patch.object(library.st, "chat_message", return_value=MagicMock()), \
                patch.object(library.st, "expander", return_value=MagicMock()), \
                patch.object(library.st, "markdown"), \
                patch.object(library.st, "caption"), \
                patch.object(library.st, "image", create=True) as image:
            library.render()

        image.assert_not_called()


if __name__ == "__main__":
    unittest.main()
