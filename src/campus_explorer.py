from src.vector_store import search
from src.image_retrieval import matches
from src.chatbot import answer_with_context

def explore(query):
    results=search(query)
    context=" ".join(x["text"] for x in results)
    response, results=answer_with_context(
        query,
        results,
        system_instruction="Answer as a helpful campus information assistant. Summarize the relevant locations or facilities directly, and do not repeat raw source text unless a short exact detail is needed.",
    )
    return response, results, matches(query, context, limit=1)
