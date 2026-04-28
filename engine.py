from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Union, List

class TestModel(BaseModel):
    explain: str
    key_words: List[str]

class AIEngine:
    def __init__(self, api_key: str, system_instructions: Union[str, None] = None, model: str = "gemini-2.5-flash-lite") -> None:
        self.engine = genai.Client(api_key=api_key)
        self.model = model
        self.system_instructions = system_instructions

    def generate_content(self, prompt: str, output_model: BaseModel) -> BaseModel:
        response = self.engine.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=output_model,
                system_instruction=self.system_instructions
            )
        )

        return output_model.model_validate_json(response.text)
    