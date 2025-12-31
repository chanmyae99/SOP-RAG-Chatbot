import fitz  # PyMuPDF
import os
from io import BytesIO
from PIL import Image

def extract_images_from_pdf(blob_bytes, source_name):
    doc = fitz.open(stream=blob_bytes, filetype="pdf")
    extracted = []
    image_index = 0

    for page_index in range(len(doc)):
        page = doc[page_index]
        images = page.get_images(full=True)

        for img in images:
            xref = img[0]
            base = doc.extract_image(xref)
            image_bytes = base["image"]
            ext = base["ext"]

            filename = f"{source_name}_p{page_index+1}_{image_index}.{ext}"

            extracted.append({
                "image_bytes": image_bytes,
                "page_number": page_index + 1,
                "file_name": filename
            })

            image_index += 1

    return extracted

