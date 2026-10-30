"""Evaluation helpers; answer review metrics require human judgments."""
def precision_at_k(retrieved, relevant, k):
    chosen=retrieved[:k]
    return sum(1 for x in chosen if x in relevant)/k if k else 0.0

def recall_at_k(retrieved, relevant, k):
    return sum(1 for x in retrieved[:k] if x in relevant)/len(relevant) if relevant else 0.0
