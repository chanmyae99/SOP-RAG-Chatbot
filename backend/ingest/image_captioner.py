
# backend/ingest/image_captioner.py
import base64
from openai import OpenAI

client = OpenAI()

def caption_image(image_bytes: bytes) -> str:
    # ✅ convert bytes → base64 string
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # vision-capable
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this image for workplace safety documentation."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.0
    )

    return response.choices[0].message.content

