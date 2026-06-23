import requests
import os
from typing import Optional

class HuggingFaceGenerator:
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("HUGGINGFACE_TOKEN")
        self.text_model = "mistralai/Mistral-7B-Instruct-v0.1"
        self.image_model = "stabilityai/stable-diffusion-2-1"

    def generate_text(self, prompt: str, max_length: int = 200) -> str:
        url = f"https://api-inference.huggingface.co/models/{self.text_model}"
        headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_length, "temperature": 0.7}}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            result = resp.json()
            if isinstance(result, list):
                return result[0].get("generated_text", "")
            return result.get("generated_text", "")
        except Exception as e:
            return f"[Falló la generación de texto: {e}] Usando texto de respaldo: {prompt}"

    def generate_image(self, prompt: str) -> Optional[str]:
        """Genera una imagen usando la API gratuita de Pollinations.ai."""
        # La URL es simple: https://image.pollinations.ai/prompt/{tu_texto}
        url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            
            os.makedirs("data/images", exist_ok=True)
            filename = f"data/images/gen_{hash(prompt)}.png"
            with open(filename, "wb") as f:
                f.write(resp.content)
            return filename
        except Exception as e:
            print(f"⚠️ No se pudo generar imagen con Pollinations: {e}")
            return None