import requests
import json
import os
from typing import List, Dict, Optional

class ZernioClient:
    BASE_URL = "https://zernio.com/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None, params: Optional[Dict] = None):
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        if files:
            response = requests.request(method, url, data=data, files=files, headers={"Authorization": f"Bearer {self.api_key}"})
        else:
            response = requests.request(method, url, json=data, headers=self.headers, params=params)
        try:
            response.raise_for_status()
            if response.text:
                return response.json()
            return {}
        except requests.exceptions.HTTPError as e:
            error_detail = response.text if response.text else str(e)
            raise Exception(f"Error en API Zernio: {response.status_code} - {error_detail}")

    # ============================
    # PERFILES Y CUENTAS
    # ============================
    def get_profiles(self) -> List[Dict]:
        data = self._request("GET", "profiles")
        return data.get("profiles", [])

    def get_accounts(self, profile_id: Optional[str] = None) -> List[Dict]:
        params = {}
        if profile_id:
            params["profileId"] = profile_id
        data = self._request("GET", "accounts", params=params)
        return data.get("accounts", [])

    # ============================
    # CONEXIÓN OAuth
    # ============================
    def get_connect_url(self, platform: str, profile_id: str, redirect_uri: str) -> str:
        payload = {"profileId": profile_id, "redirectUri": redirect_uri}
        data = self._request("POST", f"connect/{platform}", data=payload)
        return data.get("authUrl")

    def select_page(self, platform: str, temp_token: str, connect_token: str, page_id: str) -> Dict:
        payload = {"tempToken": temp_token, "connectToken": connect_token, "pageId": page_id}
        return self._request("POST", f"connect/{platform}/select-page", data=payload)

    # ============================
    # PUBLICACIÓN
    # ============================
    def create_post(self, content: str, platforms: List[Dict], publish_now: bool = True) -> Dict:
        """
        Crea una publicación. Si publish_now=True, intenta publicar directamente.
        Devuelve el post creado con su estado.
        """
        payload = {
            "content": content,
            "platforms": platforms,
            "status": "published" if publish_now else "draft"
        }
        data = self._request("POST", "posts", data=payload)
        post = data.get("post", {})
        # Si el post quedó en draft y queríamos publicarlo, intentamos publicarlo
        if publish_now and post.get("status") == "draft":
            post_id = post.get("_id")
            if post_id:
                try:
                    # Intentar publicar el borrador
                    publish_result = self._request("POST", f"posts/{post_id}/publish")
                    # Actualizar el post con el nuevo estado
                    post.update(publish_result.get("post", {}))
                except Exception as e:
                    # Si falla, dejamos el borrador y registramos el error
                    print(f"⚠️ No se pudo publicar el borrador automáticamente: {e}")
        return data

    # Método alternativo: publicar un post existente por ID
    def publish_post(self, post_id: str) -> Dict:
        """Publica un borrador existente."""
        return self._request("POST", f"posts/{post_id}/publish")