import openai
from openai import Stream

class BasicLlmClient:
    def __init__(self, api_base_url="", api_key="none"):
        if not api_base_url:
            raise ValueError("Must provide an API base URL")
        
        self.api_base_url = api_base_url

        self.client = openai.Client(
            base_url=self.api_base_url,
            api_key=api_key
        )
        self.messages = []
        self.system_prompt = "You are a helpful assistant"

        self.messages.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def send_message(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })

        chat_completion: Stream = self.client.chat.completions.create(
            model="qwen/qwen2.5-coder-14b",
            messages=self.messages,
            stream=True
        )

        assistant_message = ""
        for chunk in chat_completion:
            partial_message = chunk.choices[0].delta.content

            if partial_message is None:
                break

            assistant_message += partial_message

            yield partial_message 

        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })

        yield "\n\n"

if __name__ == "__main__":
    client = BasicLlmClient(
        api_base_url="http://192.168.1.77:8000/v1"
    )
    client.send_message("can you help me with python?")
    print()