from dotenv import load_dotenv
import os
from openai import OpenAI

# load environment variables
load_dotenv()

key = os.getenv("OPENAI_API_KEY")
print("OPENAI KEY FOUND:", bool(key))

client = OpenAI(api_key=key)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Say hello in one sentence."}
    ]
)

print("RESPONSE:")
print(response.choices[0].message.content)
