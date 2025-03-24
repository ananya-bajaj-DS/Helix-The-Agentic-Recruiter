from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_gpt4_with_function(message, history):
    try:
        messages = [{"role": "system", "content": "You are a helpful assistant for creating recruiting outreach sequences."}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}