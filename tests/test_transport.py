import unittest
from unittest.mock import MagicMock, call, patch

from modules import transport
from src import vector_store
from config import KNOWLEDGE_DIR


class TransportAnswerTests(unittest.TestCase):
    def test_transport_answers_use_only_transport_source_documents(self):
        docs = [{
            "source": "transport_information.txt",
            "chunk": 3,
            "text": "R-1 serves BTM Layout with a 6:50 AM pickup.",
            "distance": 0.2,
        }]

        with patch.object(transport, "search", return_value=docs) as search, \
                patch.object(transport, "answer_with_context", return_value=("R-1 picks up at 6:50 AM.", docs)) as generate:
            response, retrieved = transport.answer("When does R-1 pick up at BTM Layout?")

        self.assertIn("6:50 AM", response)
        self.assertEqual(retrieved, docs)
        search.assert_called_once_with(
            "When does R-1 pick up at BTM Layout?",
            top_k=6,
            source=transport.transport_sources(),
        )
        self.assertIn("snapshot", generate.call_args.kwargs["system_instruction"].lower())

    def test_transport_sources_include_category_tagged_uploads(self):
        paths = [
            KNOWLEDGE_DIR / transport.TRANSPORT_SOURCE,
            KNOWLEDGE_DIR / "data/uploads/upload_123_transport_update.txt",
            KNOWLEDGE_DIR / "data/uploads/upload_456_library_rules.txt",
        ]
        with patch.object(transport, "sources", return_value=paths), \
                patch.object(transport, "source_name", side_effect=lambda path: path.name):
            result = transport.transport_sources()

        self.assertEqual(result, [transport.TRANSPORT_SOURCE, "upload_123_transport_update.txt"])

    def test_transport_answer_passes_prior_turns_to_chatbot(self):
        history = [
            {"role": "user", "content": "Where is my stop?"},
            {"role": "assistant", "content": "Please tell me the boarding point."},
        ]
        docs = [{"source": "transport_information.txt", "chunk": 1, "text": "BTM Layout"}]

        with patch.object(transport, "search", return_value=docs), \
                patch.object(transport, "answer_with_context", return_value=("R-1.", docs)) as generate:
            transport.answer("Which route serves it?", history)

        self.assertEqual(generate.call_args.kwargs["history"], history)

    def test_render_keeps_transport_history_and_uses_it_for_follow_up(self):
        state = {}
        docs = [{"source": "transport_information.txt", "chunk": 1, "text": "BTM Layout"}]

        with patch.object(transport.st, "session_state", state), \
                patch.object(transport.st, "title"), \
                patch.object(transport.st, "write"), \
                patch.object(transport.st, "warning"), \
                patch.object(transport.st, "button", return_value=False), \
                patch.object(transport.st, "chat_input", side_effect=["Where is my stop?", "Which route serves it?"]), \
                patch.object(transport.st, "chat_message", return_value=MagicMock()), \
                patch.object(transport.st, "spinner", return_value=MagicMock()), \
                patch.object(transport.st, "expander", return_value=MagicMock()), \
                patch.object(transport.st, "markdown"), \
                patch.object(transport.st, "caption"), \
                patch.object(transport, "answer", side_effect=[("Tell me your stop.", docs), ("R-1.", docs)]) as answer:
            transport.render()
            transport.render()

        self.assertEqual(
            answer.call_args_list[1],
            call("Which route serves it?", [
                {"role": "user", "content": "Where is my stop?"},
                {"role": "assistant", "content": "Tell me your stop.", "sources": docs},
            ]),
        )
        self.assertEqual(
            [item["role"] for item in state["transport_history"]],
            ["user", "assistant", "user", "assistant"],
        )

    def test_vector_search_can_filter_by_source(self):
        class FakeCollection:
            def __init__(self):
                self.query_args = None

            def count(self):
                return 8

            def query(self, **kwargs):
                self.query_args = kwargs
                return {
                    "documents": [["A transport record."]],
                    "metadatas": [[{"source": "transport_information.txt", "chunk": 1}]],
                    "distances": [[0.1]],
                }

        collection = FakeCollection()
        with patch.object(vector_store, "collection", return_value=collection), \
                patch.object(vector_store, "embed_texts", return_value=[[0.0, 1.0]]):
            results = vector_store.search("bus route", top_k=6, source="transport_information.txt")

        self.assertEqual(len(results), 1)
        self.assertEqual(collection.query_args["where"], {"source": "transport_information.txt"})

    def test_vector_search_without_source_preserves_unfiltered_behavior(self):
        class FakeCollection:
            def __init__(self):
                self.query_args = None

            def count(self):
                return 8

            def query(self, **kwargs):
                self.query_args = kwargs
                return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        collection = FakeCollection()
        with patch.object(vector_store, "collection", return_value=collection), \
                patch.object(vector_store, "embed_texts", return_value=[[0.0, 1.0]]):
            self.assertEqual(vector_store.search("campus"), [])

        self.assertNotIn("where", collection.query_args)

    def test_transport_source_excludes_personal_contact_records(self):
        text = (KNOWLEDGE_DIR / transport.TRANSPORT_SOURCE).read_text(encoding="utf-8")

        self.assertIn("seat snapshot as of 29 October 2026", text)
        self.assertNotRegex(text, r"\b\d{9,}\b")
        self.assertNotRegex(text, r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


if __name__ == "__main__":
    unittest.main()
