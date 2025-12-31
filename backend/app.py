from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from backend.services.azure_search import vector_search_text, vector_search_images
from backend.services.rag_pipeline import answer_question, embed_query, retrieve_context

app = FastAPI(title="SOP RAG API")

@app.get("/")
def health():
    return {"status": "ok", "message": "SOP RAG backend running"}

# @app.get("/search")
# def search(q: str):
#     try:
#         docs = search_pages(q)
#         return docs
#     except Exception as e:
#         print("❌ SEARCH ERROR:", repr(e))
#         raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
def search(q: str, top_k: int = 5):
    """
    Retrieval-only endpoint (TEXT + IMAGE)
    Useful for debugging RAG context
    """
    try:
        query_vector = embed_query(q)

        text_results = vector_search_text(query_vector, top_k)
        image_results = vector_search_images(query_vector, top_k)
        # text_results, image_results = retrieve_context(q)

        return {
            "query": q,
            "text_results": text_results,
            "image_results": image_results
        }

    except Exception as e:
        print("❌ SEARCH ERROR:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))



# @app.get("/ask")
# def ask(q: str, top_k: int = 5):
#     return answer_question(q, top_k)

from fastapi import HTTPException
import traceback

@app.get("/ask")
def ask(q: str, top_k: int = 5):
    try:
        return answer_question(q, top_k)
    except Exception as e:
        print("❌ INTERNAL ERROR:")
        traceback.print_exc()   # 🔥 THIS prints the traceback
        raise HTTPException(status_code=500, detail=str(e))

