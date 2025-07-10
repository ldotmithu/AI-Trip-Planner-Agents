import requests
from langchain.llms.base import LLM
from langchain.schema import LLMResult, Generation
from utils.configs import *

def euri_chat(messages, temperature=0.7, max_tokens=500):
    url = "https://api.euron.one/api/v1/euri/alpha/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJhNTM3YzM3Zi0xNmFkLTRjZTUtYjRhMC0wNTNjYTIyNzE1YTgiLCJlbWFpbCI6InN1ZGhhbnNodUBldXJvbi5vbmUiLCJpYXQiOjE3NDMyMzkyNTYsImV4cCI6MTc3NDc3NTI1Nn0.HRHeCucOK0hPVZQwyvNoD0GaHarvHNivjJ2l6-xU1HA"
    }
    payload = {
        "model": "gpt-4.1-nano",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']



class EuriLLM(LLM):
    def _call(self, prompt, stop=None, **kwargs) -> str:
        """Single prompt usage (e.g., LLMChain)"""
        return euri_chat([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

    def _generate(self, prompts, stop=None, **kwargs) -> LLMResult:
        """Batch prompt usage (e.g., Agents)"""
        generations = []
        for prompt in prompts:
            output = self._call(prompt)
            generations.append([Generation(text=output)])
        return LLMResult(generations=generations)

    @property
    def _identifying_params(self):
        return {}

    @property
    def _llm_type(self):
        return "euri-llm"