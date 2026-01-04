from backend.services.rag_pipeline import retrieve_context

def precision_at_k(retrieved, expected_sources, k=5):
    """
    retrieved: list of retrieved chunks (text + image)
    expected_sources: list of expected filenames
    """
    retrieved_files = [
        r["source_file"]
        for r in retrieved[:k]
        if r.get("source_file")
    ]

    hits = sum(
    1 for f in retrieved_files
    if any(exp in f for exp in expected_sources))

    return hits / k


def evaluate_retrieval(eval_data, k=5):
    scores = []

    for item in eval_data:
        text_results, image_results = retrieve_context(item["question"])
        retrieved = text_results + image_results

        score = precision_at_k(
            retrieved,
            item["expected_sources"],
            k=k
        )

        scores.append(score)
        print(f"{item['id']} | Precision@{k} = {score:.2f}")

    avg = sum(scores) / len(scores)
    print(f"\nAverage Precision@{k}: {avg:.2f}")
    return avg
