import requests
import feedparser
import os
import random
from typing import List, Dict, Optional

class ContentFetcher:
    def __init__(self, rss_feeds: List[str], subreddits: List[str], user_agent: str = "AgenteSocial/1.0"):
        """
        Inicializa el fetcher con listas de feeds RSS y subreddits.
        """
        self.rss_feeds = rss_feeds
        self.subreddits = subreddits
        self.user_agent = user_agent

    def fetch_news(self, limit: int = 5) -> List[Dict]:
        """Obtiene noticias usando los feeds RSS configurados."""
        articles = []
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:limit]:
                    articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": entry.summary[:200] + "..." if entry.summary else "",
                        "source": feed.feed.title
                    })
            except Exception as e:
                print(f"Error al leer RSS {feed_url}: {e}")
        return articles

    def fetch_meme(self, subreddits: Optional[List[str]] = None) -> Optional[str]:
        """
        Obtiene un meme de los subreddits usando exclusivamente feeds RSS.
        """
        if subreddits is None:
            subreddits = self.subreddits

        if not subreddits:
            print("❌ No hay subreddits disponibles")
            return None

        # Barajar para probar en orden aleatorio
        shuffled = subreddits.copy()
        random.shuffle(shuffled)
        print(f"🔍 Subreddits barajados: {shuffled[:3]}...")

        for subreddit in shuffled:
            print(f"🔍 Probando subreddit (RSS): {subreddit}")
            meme = self._fetch_meme_rss(subreddit)
            if meme:
                print(f"✅ Meme encontrado en {subreddit} (RSS)")
                return meme

        print("❌ No se encontró ningún meme en todos los subreddits")
        return None

    def _fetch_meme_rss(self, subreddit: str) -> Optional[str]:
        """
        Obtiene un meme del feed RSS de Reddit (funciona sin autenticación).
        """
        url = f"https://www.reddit.com/r/{subreddit}/hot.rss"
        print(f"   🌐 Solicitando RSS: {url}")
        try:
            feed = feedparser.parse(url)
            # Verificar si el feed tiene entradas
            if not feed.entries:
                print(f"   ⚠️ No hay entradas en {subreddit}")
                return None

            for entry in feed.entries[:10]:
                enlace = entry.link
                # Buscar enlaces a imágenes
                if enlace and enlace.endswith(('.jpg', '.png', '.jpeg', '.gif')):
                    return self._download_image(enlace, entry.id)
            return None
        except Exception as e:
            print(f"   ❌ Error en RSS para r/{subreddit}: {e}")
            return None

    def _download_image(self, url: str, nombre_base: str) -> Optional[str]:
        """
        Descarga una imagen y la guarda en data/memes/.
        """
        try:
            resp = requests.get(url, stream=True, timeout=15)
            if resp.status_code == 200:
                os.makedirs("data/memes", exist_ok=True)
                extension = url.split('.')[-1].split('?')[0]
                nombre_base = ''.join(c for c in nombre_base if c.isalnum() or c in '.-_')
                filename = f"data/memes/{nombre_base}.{extension}"
                with open(filename, 'wb') as f:
                    for chunk in resp.iter_content(1024):
                        f.write(chunk)
                return filename
            else:
                print(f"   ⚠️ Error al descargar imagen: {resp.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ Error descargando imagen {url}: {e}")
            return None