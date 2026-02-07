from dotenv import load_dotenv
load_dotenv()



from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from dotenv import load_dotenv
from pathlib import Path
import os
import re

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
