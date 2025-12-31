from dotenv import load_dotenv
load_dotenv()



from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from dotenv import load_dotenv
from pathlib import Path
import os


endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

print("DEBUG endpoint:", endpoint)
print("DEBUG key:", key)
print("DEBUG index:", index_name)

search_client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(key)
)



# def search_documents(query: str, top_k: int = 5):
#     results = search_client.search(
#         search_text=query,
#         top=top_k
#     )

#     docs = []
#     for r in results:
#         docs.append({
#             "content": r.get("content", ""),
#             "source": r.get("metadata_storage_path", ""),
#             "score": r["@search.score"]
#         })

#     return docs

# def search_pages(query: str, top_k: int = 5):
#     results = search_client.search(search_text=query, top=top_k)

#     docs = []
#     for r in results:
#         docs.append({
#             "content": r.get("content", ""),
#             "source_file": r.get("metadata_storage_name", ""),
#             "source_path": r.get("metadata_storage_path", ""),
#             "page_number": extract_page(r.get("metadata_storage_path", "")),
#             "score": r["@search.score"]
#         })
#     return docs

import re

def extract_page(path: str):
    match = re.search(r"page=(\d+)", path)
    return int(match.group(1)) if match else None

def upload_documents(documents, batch_size=100):
    total = len(documents)
    print(f"🔼 Uploading {total} documents in batches of {batch_size}")

    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]

        result = search_client.upload_documents(batch)

        failed = [r for r in result if not r.succeeded]
        if failed:
            print("❌ Failed documents:")
            for f in failed:
                print(f)
            raise Exception("Azure Search batch upload failed")

        print(f"✅ Uploaded batch {i // batch_size + 1}")

# ==============================
# VECTOR SEARCH
# ==============================
# def vector_search(
#     query_vector: list,
#     top_k: int = 5
# ):
#     """
#     Perform vector similarity search on content_vector
#     """

#     results = search_client.search(
#         search_text="*",   # IMPORTANT: disable keyword search
#         vector_queries=[
#             {
#                 "kind": "vector",
#                 "vector": query_vector,
#                 "fields": "content_vector",
#                 "k": top_k
#             }
#         ],
#         select=[
#             "content",
#             "metadata_storage_name",
#             "metadata_storage_path",
#             "page_number",
#             "section",
#             "paragraph_number"
#         ]
#     )

    # docs = []
    # for r in results:
    #     docs.append({
    #         "content": r["content"],
    #         "source_file": r.get("metadata_storage_name"),
    #         "page_number": r.get("page_number"),
    #         "section": r.get("section"),
    #         "paragraph_number": r.get("paragraph_number"),
    #         "score": r["@search.score"]
    #     })

    # return docs

def vector_search_text(query_vector: list, top_k: int = 5):
    results = search_client.search(
        search_text=None,
        vector_queries=[{
            "kind": "vector",
            "vector": query_vector,
            "fields": "content_vector",
            "k": top_k
        }],
        filter="asset_type eq 'text' or asset_type eq 'table'",
        select=[
            "asset_type",
            "content",
            "metadata_storage_name",
            "page_number",
            "section",
            "paragraph_number",
            "sheet_name",
            "row_number"
        ]
    )

    return [{
        "type": "text",
        "content": r["content"],
        "source_file": r.get("metadata_storage_name"),
        "page_number": r.get("page_number"),
        "section": r.get("section"),
        "paragraph_number": r.get("paragraph_number"),
        "sheet_name": r.get("sheet_name"),
        "row_number": r.get("row_number"),
        "score": r["@search.score"]
    } for r in results]


def vector_search_images(query_vector: list, top_k: int = 3):
    results = search_client.search(
        search_text=None,
        vector_queries=[{
            "kind": "vector",
            "vector": query_vector,
            "fields": "image_vector",
            "k": top_k
        }],
        filter="asset_type eq 'image'",
        select=[
            "asset_type",
            "image_caption",
            "image_blob_path",
            "metadata_storage_name",
            "page_number"
        ]
    )

    return [{
        "type": "image",
        "caption": r["image_caption"],
        "image_path": r["image_blob_path"],
        "source_file": r.get("metadata_storage_name"),
        "page_number": r.get("page_number"),
        "score": r["@search.score"]
    } for r in results]
