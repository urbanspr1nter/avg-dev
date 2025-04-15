import requests
import json

base_url = "http://localhost:8888/v1"
model = "llama.cpp"

def send_message(message):
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": message 
            }
        ],
        "stream": True
    }

    with requests.post(f"{base_url}/chat/completions", json=payload, stream=True) as chat_response_iterator:
        for chunk in chat_response_iterator.iter_content(chunk_size=None):
            if chunk:
                raw_string = chunk.decode("utf-8")
                
                if raw_string.startswith("data: "):
                    raw_string = raw_string[6:].strip()

                if raw_string == "[DONE]":
                    break

                try:
                    parsed_json = json.loads(raw_string)

                    if "choices" not in parsed_json:
                        raise KeyError("Couldn't find choices")
                    
                    choices = parsed_json["choices"]
                    assistant_response = choices[0]

                    if "finish_reason" not in assistant_response:
                        raise KeyError("Couldn't find finish_reason")
                    
                    if assistant_response["finish_reason"] == "stop":
                        break

                    if "delta" not in assistant_response:
                        raise KeyError("Couldn't find delta")

                    delta = assistant_response["delta"]

                    if "content" not in delta:
                        raise KeyError("Couldn't find content")
                    
                    content = delta["content"]

                    yield content
                except Exception:
                    print("ALERT: Couldn't parse JSON", raw_string)
                    exit(1)
        print()

for token in send_message("hello there"):
    print(token, end="", flush=True)
