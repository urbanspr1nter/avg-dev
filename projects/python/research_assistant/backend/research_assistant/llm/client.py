import openai
from openai import Stream

"""
A basic LLM client that interfaces with an OpenAI compatible endpoint.

Initialization Arguments:
    base_url - the base API url ending with /v1
    api_key - the api key, defaults to 'none'
    model - the model to chat with

Methods:
    send_message(str, opts={})
"""

class BasicChatClient:
    def __init__(self, base_url: str, model: str, api_key="none"):
        self.base_url = base_url
        self.model = model

        self.client = openai.Client(
            base_url=self.base_url,
            api_key=api_key
        )

        self.messages = []
        self.system_prompt = "You are a helpful research assistant."

        self.messages.append({
            "role": "system",
            "content": self.system_prompt
        })

    def send_message(self, message: str, opts={}):
        self.messages.append({
            "role": "user",
            "content": message
        })

        stream: Stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True,
            temperature=opts.get("temperature", 1.0)
        )
  
        assistant_message = ""
        for chunk in stream:
            delta_content = chunk.choices[0].delta.content
            if delta_content is None:
                break

            assistant_message += delta_content

            yield delta_content

        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })


