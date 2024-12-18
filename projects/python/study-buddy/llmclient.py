import requests
import json

class LlmClient:

    def __init__(self, prompt):
        self._headers = {
            "Content-Type": "application/json"
        }

        self._prompt = prompt

    def validate_answer(self, question, answer, attempt):
        user_message = f"Question: {question}\nAnswer: {answer}\nAttempt: {attempt}"

        payload = {
            "model": "llama3.2:3b-instruct-q8_0",
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": self._prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }

        res = requests.post(
            'http://localhost:11434/api/chat',
            data=json.dumps(payload),
            headers=self._headers
        )

        res_as_json_dict = res.json()
        llm_response_content = res_as_json_dict['message']['content']

        result = json.loads(llm_response_content)

        return result["result"]
