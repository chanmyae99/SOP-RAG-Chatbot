import json

from evaluation.retrieval_eval import evaluate_retrieval
from evaluation.faithfulness_eval import faithfulness_judge
from backend.services.rag_pipeline import answer_question, build_context

# ----------------------------
# Load evaluation questions
# ----------------------------
with open("evaluation/questions.json", "r") as f:
    eval_data = json.load(f)

print("\n==============================")
print(" RETRIEVAL EVALUATION")
print("==============================")
evaluate_retrieval(eval_data, k=5)

print("\n==============================")
print(" FAITHFULNESS EVALUATION")
print("==============================")

for item in eval_data:
    result = answer_question(item["question"])

    context = build_context(
        result.get("text_results", []),
        result.get("image_results", [])
    )

    verdict = faithfulness_judge(
        item["question"],
        context,
        result["answer"]
    )

    print(f"{item['id']} | Faithfulness: {verdict}")
