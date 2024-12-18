class PromptReader:

    def read_prompt(self):
        prompt = "You are a helpful assitant"

        with open("prompt.txt") as f:
            prompt = f.read()

        return prompt
