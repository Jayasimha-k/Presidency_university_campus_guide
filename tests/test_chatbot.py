import unittest
from unittest.mock import patch

import requests

import src.chatbot as chatbot


class ChatbotTests(unittest.TestCase):
    def test_greeting_does_not_search_or_call_ai(self):
        with patch.object(chatbot, "search") as search, patch.object(chatbot.requests, "post") as post:
            response, docs = chatbot.answer("Hello!")

        self.assertIn("campus locations and directions", response)
        self.assertEqual(docs, [])
        search.assert_not_called()
        post.assert_not_called()

    def test_campus_question_uses_configured_bearer_key(self):
        docs = [{"source": "routes.txt", "chunk": 1, "text": "Gym is on the fifth floor.", "distance": 0.2}]
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"choices":[{"message":{"content":"The gym is on the fifth floor."}}]}'

        with patch.object(chatbot, "search", return_value=docs), \
                patch.object(chatbot, "GROQ_API_KEY", "test-key"), \
                patch.object(chatbot.requests, "post", return_value=response) as post:
            answer, retrieved = chatbot.answer("Where is the gym?")

        self.assertEqual(answer, "The gym is on the fifth floor.")
        self.assertEqual(retrieved, docs)
        self.assertTrue(post.call_args.kwargs["headers"]["Authorization"].startswith("Bearer "))
        self.assertTrue(post.call_args.kwargs["headers"]["Authorization"].endswith("test-key"))
        self.assertEqual(post.call_args.args[0], "https://api.groq.com/openai/v1/chat/completions")
        request = post.call_args.kwargs["json"]
        self.assertEqual(request["model"], chatbot.GROQ_MODEL)
        self.assertEqual(request["max_completion_tokens"], 700)

    def test_context_answer_passes_instructions_and_sources_to_groq(self):
        docs = [{"source": "routes.txt", "chunk": 1, "text": "Gym is on the fifth floor.", "distance": 0.2}]
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"choices":[{"message":{"content":"The gym is on the fifth floor."}}]}'

        with patch.object(chatbot, "GROQ_API_KEY", "test-key"), \
                patch.object(chatbot.requests, "post", return_value=response) as post:
            answer, retrieved = chatbot.answer_with_context(
                "How do I get to the gym?",
                docs,
                system_instruction="Do not invent missing route steps.",
            )

        self.assertIn("fifth floor", answer)
        self.assertEqual(retrieved, docs)
        messages = post.call_args.kwargs["json"]["messages"]
        self.assertIn("Do not invent missing route steps.", messages[0]["content"])
        self.assertIn("[Source: routes.txt, chunk 1]", messages[-1]["content"])
        self.assertIn("Gym is on the fifth floor.", messages[-1]["content"])

    def test_unauthorized_response_identifies_key_configuration(self):
        response = requests.Response()
        response.status_code = 401

        with patch.object(chatbot, "search", return_value=[{"source": "routes.txt", "chunk": 1, "text": "Gym.", "distance": 0.2}]), \
                patch.object(chatbot, "GROQ_API_KEY", "test-key"), \
                patch.object(chatbot.requests, "post", return_value=response):
            answer, _ = chatbot.answer("Where is the gym?")

        self.assertIn("HTTP 401", answer)
        self.assertIn("valid Groq API key", answer)

    def test_xai_key_is_rejected_without_calling_groq(self):
        docs = [{"source": "routes.txt", "chunk": 1, "text": "Gym.", "distance": 0.2}]

        with patch.object(chatbot, "search", return_value=docs), \
                patch.object(chatbot, "GROQ_API_KEY", "xai-test-key"), \
                patch.object(chatbot.requests, "post") as post:
            answer, retrieved = chatbot.answer("Where is the gym?")

        self.assertIn("xAI key", answer)
        self.assertIn("Groq API key", answer)
        self.assertEqual(retrieved, docs)
        post.assert_not_called()

    def test_bad_request_identifies_model_configuration(self):
        response = requests.Response()
        response.status_code = 400

        with patch.object(chatbot, "search", return_value=[{"source": "routes.txt", "chunk": 1, "text": "Gym.", "distance": 0.2}]), \
                patch.object(chatbot, "GROQ_API_KEY", "gsk_test-key"), \
                patch.object(chatbot.requests, "post", return_value=response):
            answer, _ = chatbot.answer("Where is the gym?")

        self.assertIn("HTTP 400", answer)
        self.assertIn("GROQ_MODEL", answer)


if __name__ == "__main__":
    unittest.main()
