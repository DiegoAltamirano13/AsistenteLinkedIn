import feedparser
import requests
import json
import praw
from datetime import datetime, timedelta
import random
import os
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentFetcher:
    def __init__(self, config):
        self.config = config
        self.meme_cache = {}
        self.news_cache = {}
        
        # Inicializar Reddit para memes
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT')
            )
            logger.info("✅ Reddit inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error al inicializar Reddit: {e}")
            self.reddit = None

    def fetch_news(self, topic: str, limit: int = 5) -> List[Dict]:
        """Obtiene noticias de feeds RSS"""
        feeds = self.config['topics'][topic]['feeds']
        articles = []
        
        for feed_url in feeds:
            try:
                logger.info(f"📡 Obteniendo noticias de: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:limit]:
                    # Buscar imagen
                    image_url = None
                    if hasattr(entry, 'media_content') and entry.media_content:
                        image_url = entry.media_content[0].get('url')
                    elif hasattr(entry, 'enclosures') and entry.enclosures:
                        image_url = entry.enclosures[0].get('href')
                    
                    articles.append({
                        'title': entry.title,
                        'summary': self.clean_text(entry.summary[:250]) + '...',
                        'link': entry.link,
                        'image_url': image_url,
                        'source': feed_url,
                        'published': entry.get('published', '')
                    })
            except Exception as e:
                logger.error(f"❌ Error en {feed_url}: {e}")
        
        return articles

    def fetch_memes(self, limit: int = 5) -> List[Dict]:
        """Obtiene memes de Reddit"""
        if not self.reddit:
            logger.warning("⚠️ Reddit no disponible")
            return []
        
        memes = []
        subreddits = self.config['memes']['subreddits']
        min_score = self.config['memes']['min_score']
        
        for subreddit_name in random.sample(subreddits, min(3, len(subreddits))):
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.hot(limit=limit * 2)
                
                for post in posts:
                    if post.score >= min_score and post.url.endswith(('.jpg', '.png', '.gif')):
                        memes.append({
                            'title': post.title,
                            'url': post.url,
                            'score': post.score,
                            'subreddit': subreddit_name,
                            'comments': post.num_comments
                        })
                
                if len(memes) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"❌ Error en r/{subreddit_name}: {e}")
        
        return memes[:limit]

    def fetch_trending_github(self) -> List[Dict]:
        """Obtiene repositorios trending de GitHub"""
        try:
            url = "https://github-trending-api.herokuapp.com/repositories"
            response = requests.get(url, timeout=10)
            repos = response.json()
            
            return [{
                'name': repo['name'],
                'description': repo['description'][:200],
                'stars': repo['stars'],
                'language': repo['language'],
                'url': repo['url']
            } for repo in repos[:5]]
        except Exception as e:
            logger.error(f"❌ Error en GitHub Trending: {e}")
            return []

    def clean_text(self, text: str) -> str:
        """Limpia texto HTML"""
        import re
        # Eliminar tags HTML
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        # Eliminar caracteres especiales
        text = re.sub(r'[^\w\s.,!?¡¿]', '', text)
        return text.strip()

    def download_image(self, url: str, save_path: str) -> bool:
        """Descarga una imagen desde una URL"""
        try:
            response = requests.get(url, timeout=30, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                logger.info(f"✅ Imagen descargada: {save_path}")
                return True
        except Exception as e:
            logger.error(f"❌ Error al descargar imagen: {e}")
        return False