# backend/services/blob_storage.py
import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER")

def get_container_client():
    blob_service = BlobServiceClient.from_connection_string(
        BLOB_CONNECTION_STRING
    )
    return blob_service.get_container_client(CONTAINER_NAME)


def list_blobs(container_client):
    return list(container_client.list_blobs())


def download_blob(container_client, blob_name: str) -> bytes:
    blob_client = container_client.get_blob_client(blob_name)
    return blob_client.download_blob().readall()

def upload_image(container_client, blob_path: str, image_bytes: bytes):
    blob = container_client.get_blob_client(blob_path)
    blob.upload_blob(image_bytes, overwrite=True)
