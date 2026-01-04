from openai import OpenAI

client = OpenAI()

def faithfulness_judge(question, context, answer):
    """
    LLM-as-judge to detect hallucination
    """
    prompt = f"""
You are evaluating a safety SOP chatbot.

Question:
{question}

Retrieved Context:
{context}

Answer:
{answer}

Is every claim in the answer supported by the retrieved context?

Respond with one of:
- YES (fully supported)
- PARTIAL (some unsupported claims)
- NO (hallucinated)

Explain briefly.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    return response.choices[0].message.content.strip()

