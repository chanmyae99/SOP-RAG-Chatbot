# backend/services/rag_pipeline.py
import os
from backend.services.azure_search import vector_search_text, vector_search_images
from openai import OpenAI


client = OpenAI()

# ----------------------------
# OpenAI client
# ----------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ----------------------------
# System prompt (STRICT)
# ----------------------------
SYSTEM_PROMPT = """
You are an SOP Q&A assistant.

Answer the question using ONLY the provided document excerpts.
Prioritise operational procedures, role responsibilities,
and safety requirements over training, administrative,
or curriculum-related information.

If the question is semantically related to the content,
answer using the most directly relevant procedures.
Do NOT include loosely related or generic safety practices.

DO NOT MIXED the lifting dust and combustible dust procedure.

When you use evidence, explicitly cite its source ID
(e.g., [T1], [T2], [I1]).

Do not cite sources you did not use.

The evidence may include:
- TEXT EVIDENCE (procedures, responsibilities, requirements)
- IMAGE EVIDENCE (diagrams, schematics, figures)

IMPORTANT RULES:
- If IMAGE EVIDENCE is used, explicitly state phrases such as
  "Based on the diagram [I1]..." or
  "According to the schematic [I1]..."

- If only TEXT EVIDENCE is used, do NOT mention diagrams or images.

Do NOT require exact wording matches.
Do NOT hallucinate new procedures.

For factual statements:
- Cite sources only when they directly support the statement.
- Do NOT add extra statements solely to increase citations.

If the documents partially cover the topic,
clearly explain what is covered and what is not.

"""




# You are an SOP Q&A assistant.

# Answer the question using ONLY the provided document excerpts.
# The documents may use formal or regulatory language.

# If the question is semantically related to the content,
# answer using the closest relevant procedures.

# When you use evidence, explicitly cite its source ID
# (e.g., [T1], [T2], [I1]).

# If you use an image, say phrases like:
# "Based on the diagram [I1]..."

# Do not cite sources you did not use.

# The evidence may include:
# - TEXT EVIDENCE (procedures, requirements)
# - IMAGE EVIDENCE (diagrams, schematics, figures)

# IMPORTANT RULES:
# - If IMAGE EVIDENCE is used in your reasoning, you MUST explicitly say
#   phrases such as:
#   "Based on the diagram..."
#   "According to the schematic..."
#   "The figure illustrates that..."

# - If only TEXT EVIDENCE is used, do NOT mention diagrams or images.

# Do NOT require exact wording matches.
# Do NOT hallucinate new procedures.

# For every factual statement in your answer:
# - Cite the source number(s) in square brackets, e.g. [Source 1].
# - Only cite sources that directly support the statement.
# - Do NOT cite sources that are not used.
# - Site the page name 

# If the documents partially cover the topic,
# explain what is covered and what is not.

import re

def extract_used_source_ids(answer: str):
    return set(re.findall(r"\[(T\d+|I\d+)\]", answer))




# ----------------------------
# Build context with citations
# ----------------------------
# def build_context(pages):
#     blocks = []

#     for p in pages:
#         if p.get("page_number") is not None:
#             citation = f"{p['source_file']}, page {p['page_number']}"
#         elif p.get("section") and p.get("paragraph_number"):
#             citation = (
#                 f"{p['source_file']}, "
#                 f"Section: {p['section']}, "
#                 f"Paragraph {p['paragraph_number']}"
#             )
#         elif p.get("section"):
#             citation = f"{p['source_file']}, Section: {p['section']}"
#         else:
#             citation = p["source_file"]

#         block = f"""
# Source: ({citation})
# Content:
# {p['content']}
# """
#         blocks.append(block.strip())

#     return "\n\n---\n\n".join(blocks)


# def build_context(text_results, image_results):
#     blocks = []

#     # ----------------------------
#     # TEXT EVIDENCE
#     # ----------------------------
#     if text_results:
#         blocks.append("TEXT EVIDENCE:")

#         for p in text_results:
#             if p.get("page_number") is not None:
#                 citation = f"{p['source_file']}, page {p['page_number']}"
#             elif p.get("section") and p.get("paragraph_number"):
#                 citation = (
#                     f"{p['source_file']}, "
#                     f"Section: {p['section']}, "
#                     f"Paragraph {p['paragraph_number']}"
#                 )
#             elif p.get("section"):
#                 citation = f"{p['source_file']}, Section: {p['section']}"
#             else:
#                 citation = p["source_file"]

#             block = f"""
# Source: ({citation})
# Content:
# {p['content']}
# """
#             blocks.append(block.strip())

#     # ----------------------------
#     # IMAGE EVIDENCE
#     # ----------------------------
#     if image_results:
#         blocks.append("\nIMAGE EVIDENCE:")

#         # for img in image_results:
#         #     citation = (
#         #         f"{img['source_file']}, "
#         #         f"page {img['page_number']}"
#         #         if img.get("page_number") is not None
#         #         else img["source_file"]
#         #     )

#         #     block = f"""
#         #         Source: ({citation})
#         #         Diagram description:
#         #         {img['image_caption']}
#         #     """
#         #     blocks.append(block.strip())

#         for img in image_results:
#             citation = img["source_file"]
#             if img.get("page_number") is not None:
#                 citation += f", page {img['page_number']}"

#             blocks.append(f"""
#                 Source: ({citation})
#                 Diagram:
#                 {img.get("caption")}
#             """.strip())

#     return "\n\n---\n\n".join(blocks)

# def build_context(text_results, image_results):
#     blocks = []

#     if text_results:
#         blocks.append("TEXT EVIDENCE:")
#         for p in text_results:
#             citation = f"[{p['_source_id']}] {p['source_file']}"
#             blocks.append(f"{citation}\n{p['content']}")

#     if image_results:
#         blocks.append("\nIMAGE EVIDENCE:")
            
#         for img in image_results:
#             citation = f"[{img['_source_id']}] {img['source_file']}"
#             if img.get("page_number") is not None:
#                 citation += f", page {img['page_number']}"

#             blocks.append(f"""
#                 Source: ({citation})
#                 Diagram:
#                 {img.get("caption")}
#             """.strip())

#     return "\n\n".join(blocks)

def build_context(text_results, image_results):
    blocks = []

    # ----------------------------
    # TEXT / TABLE EVIDENCE
    # ----------------------------
    if text_results:
        blocks.append("TEXT EVIDENCE:")

        for p in text_results:
            citation = f"[{p['_source_id']}] {p['source_file']}"

            # PDF
            if p.get("page_number") is not None:
                citation += f", page {p['page_number']}"

            # DOCX
            elif p.get("section"):
                citation += f", section \"{p['section']}\""
                if p.get("paragraph_number"):
                    citation += f", paragraph {p['paragraph_number']}"

            # XLSX
            elif p.get("sheet_name"):
                citation += f", sheet \"{p['sheet_name']}\""
                if p.get("row_number"):
                    citation += f", row {p['row_number']}"

            blocks.append(
                f"{citation}\n{p['content']}"
            )

    # ----------------------------
    # IMAGE EVIDENCE
    # ----------------------------
    if image_results:
        blocks.append("\nIMAGE EVIDENCE:")

        for img in image_results:
            citation = f"[{img['_source_id']}] {img['source_file']}"

            if img.get("page_number") is not None:
                citation += f", page {img['page_number']}"

            blocks.append(
                f"{citation}\nDiagram description:\n{img.get('caption')}"
            )

    return "\n\n".join(blocks)


# ----------------------------
# Build user prompt
# ----------------------------
def build_prompt(question: str, context: str):
    return f"""
Question:
{question}

Sources:
{context}

Instructions:
- Use TEXT EVIDENCE for procedural steps.
- Use IMAGE EVIDENCE to explain spatial layout, safety zones, or visual concepts.
- If you refer to IMAGE EVIDENCE, explicitly mention it in your answer.

Answer clearly and concisely.
"""

# ----------------------------
# Main RAG function (USED BY API)
# ----------------------------
# def answer_question(question: str, top_k: int = 5):
#     """
#     Full RAG pipeline:
#     1. Retrieve pages from Azure AI Search
#     2. Build grounded prompt
#     3. Call OpenAI
#     4. Return answer + sources
#     """

#     pages = retrieve_context(question)


#     if not pages:
#         return {
#             "question": question,
#             "answer": "The information is not available in the provided documents.",
#             "sources": []
#         }

#     context = build_context(pages)
#     prompt = build_prompt(question, context)

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.1
#     )
#     answer = response.choices[0].message.content
#     used = extract_used_sources(answer)

#     final_sources = [
#         pages[i - 1] for i in used
#         if 0 < i <= len(pages)
#     ]
#     return {
#         "question": question,
#         "answer": response.choices[0].message.content,
#         "sources": [
#     {
#         "source_file": p["source_file"],
#         **({"page_number": p["page_number"]} if p.get("page_number") is not None else {}),
#         **({"section": p["section"]} if p.get("section") else {}),
#         **({"paragraph_number": p["paragraph_number"]} if p.get("paragraph_number") else {})
#     }
#     for p in final_sources
# ]


#     }

# def answer_question(question: str, top_k: int = 5):
#     """
#     Hybrid RAG pipeline (TEXT + IMAGE):
#     1. Retrieve text + image context
#     2. Build grounded prompt
#     3. Call OpenAI
#     4. Return answer + cited sources
#     """

#     text_results, image_results = retrieve_context(question)

#     if not text_results and not image_results:
#         return {
#             "question": question,
#             "answer": "The information is not available in the provided documents.",
#             "sources": []
#         }

#     context = build_context(
#         text_results=text_results,
#         image_results=image_results
#     )

#     prompt = build_prompt(question, context)

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.1
#     )

#     answer = response.choices[0].message.content

#     # ----------------------------
#     # Build sources explicitly
#     # ----------------------------
#     sources = []

#     for p in text_results:
#         src = {
#             "type": "text",
#             "source_file": p["source_file"]
#         }

#         if p.get("page_number") is not None:
#             src["page_number"] = p["page_number"]

#         if p.get("section") is not None:
#             src["section"] = p["section"]

#         if p.get("paragraph_number") is not None:
#             src["paragraph_number"] = p["paragraph_number"]

#         sources.append(src)

#     for i in image_results:
#         src = {
#             "type": "image",
#             "source_file": i["source_file"],
#             "page_number": i.get("page_number"),
#             "image_path": i.get("image_path"),
#             "caption": i.get("caption")
#         }
#         sources.append(src)

#     return {
#         "question": question,
#         "answer": answer,
#         "sources": sources
#     }

def answer_question(question: str, top_k: int = 5):
    text_results, image_results = retrieve_context(question)
    
    if not text_results and not image_results:
        return {
            "question": question,
            "answer": "The information is not available in the provided documents.",
            "sources": []
        }

    assign_source_ids(text_results, image_results)

    context = build_context(text_results, image_results)
    prompt = build_prompt(question, context)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    answer = response.choices[0].message.content
    used_ids = extract_used_source_ids(answer)



    final_sources = [
        build_source_metadata(p)
        for p in (text_results + image_results)
        if p["_source_id"] in used_ids
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": final_sources
    }




def embed_query(query: str) -> list:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    return response.data[0].embedding


def retrieve_context(user_question: str):
    query_vector = embed_query(user_question)
    text_results = vector_search_text(query_vector)
    image_results = vector_search_images(query_vector)


    return text_results, image_results

def assign_source_ids(text_results, image_results):
    sources = []

    for i, p in enumerate(text_results, start=1):
        p["_source_id"] = f"T{i}"
        sources.append(p)

    for j, img in enumerate(image_results, start=1):
        img["_source_id"] = f"I{j}"
        sources.append(img)

    return sources


def build_source_metadata(p: dict) -> dict:
    source = {
        "source_id": p["_source_id"],
        "source_file": p["source_file"],
        **({"page_number": p["page_number"]} if p.get("page_number") is not None else {}),
        **({"section": p["section"]} if p.get("section") else {}),
        **({"paragraph_number": p["paragraph_number"]} if p.get("paragraph_number") else {}),
        **({"caption": p["caption"]} if p.get("caption") else {}),
        **({"image_path": p["image_path"]} if p.get("image_path") else {})
    }

    return source


