# scheduler.py
import schedule
import time
import random
import logging
from datetime import datetime
import threading
import json
import os
from functools import partial

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self, content_fetcher, meme_generator, linkedin_poster):
        self.content_fetcher = content_fetcher
        self.meme_generator = meme_generator
        self.linkedin_poster = linkedin_poster
        self.post_history = []
        self.is_running = False
        self.load_history()

    def load_history(self):
        """Carga el historial de publicaciones"""
        history_file = 'data/posts/history.json'
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.post_history = json.load(f)
            except:
                self.post_history = []

    def save_history(self):
        """Guarda el historial de publicaciones"""
        os.makedirs('data/posts', exist_ok=True)
        with open('data/posts/history.json', 'w', encoding='utf-8') as f:
            json.dump(self.post_history, f, indent=2, ensure_ascii=False)

    def create_ai_post(self):
        """Crea una publicación sobre IA"""
        try:
            logger.info("Generando publicacion de IA...")
            articles = self.content_fetcher.fetch_news('ia', limit=3)
            if not articles:
                return None
            article = random.choice(articles)
            
            image_path = None
            if article.get('image_url'):
                image_path = f"data/images/ia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                self.content_fetcher.download_image(article['image_url'], image_path)
            
            templates = [
                f"🚀 **Novedades en Inteligencia Artificial**\n\n{article['title']}\n\n{article['summary']}\n\n🔗 {article['link']}\n\n#IA #InteligenciaArtificial #MachineLearning #Tech",
                f"🤖 **La IA no se detiene**\n\n{article['title']}\n\n{article['summary']}\n\n📖 Más info: {article['link']}\n\n#AI #ArtificialIntelligence #Innovación"
            ]
            content = random.choice(templates)
            post_image = self.meme_generator.create_post_image(article['title'], "IA - Últimas Noticias", image_path)
            
            return {'content': content, 'image': post_image}
        except Exception as e:
            logger.error(f"Error en publicacion de IA: {e}")
            return None

    def create_meme_post(self):
        """Crea una publicación con meme"""
        try:
            logger.info("Generando meme...")
            memes = self.content_fetcher.fetch_memes(limit=5)
            if memes:
                meme = random.choice(memes)
                meme_path = f"data/memes/meme_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                if self.content_fetcher.download_image(meme['url'], meme_path):
                    content = f"😂 {meme['title']}\n\n💬 De r/{meme['subreddit']}\n\n#Meme #Programación #Tecnología #Humor"
                    return {'content': content, 'image': meme_path}
            
            # Fallback: meme generado localmente
            jokes = [
                "Cuando el código compila a la primera",
                "El programador después de 8 horas de debugging",
                "Mi reacción cuando veo código sin comentarios",
                "El QA encontrando un bug después del deploy"
            ]
            joke = random.choice(jokes)
            meme_path = self.meme_generator.create_meme(joke)
            if meme_path:
                content = f"😂 {joke}\n\n#Programación #Meme #DevLife #Coding"
                return {'content': content, 'image': meme_path}
            return None
        except Exception as e:
            logger.error(f"Error en publicacion de meme: {e}")
            return None

    def create_videojuegos_post(self):
        """Crea publicación sobre videojuegos"""
        try:
            logger.info("Generando publicacion de videojuegos...")
            articles = self.content_fetcher.fetch_news('videojuegos', limit=3)
            if not articles:
                return None
            article = random.choice(articles)
            
            image_path = None
            if article.get('image_url'):
                image_path = f"data/images/gaming_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                self.content_fetcher.download_image(article['image_url'], image_path)
            
            templates = [
                f"🎮 **Novedades en el mundo gamer**\n\n{article['title']}\n\n{article['summary']}\n\n🔗 {article['link']}\n\n#Videojuegos #Gaming #Gamer #PCGaming",
                f"🕹️ **Últimas noticias de la industria**\n\n{article['title']}\n\n📰 {article['summary']}\n\n#Videojuegos #GamingNews #Juegos"
            ]
            content = random.choice(templates)
            post_image = self.meme_generator.create_post_image(article['title'], "🎮 Gaming News", image_path)
            return {'content': content, 'image': post_image}
        except Exception as e:
            logger.error(f"Error en publicacion de videojuegos: {e}")
            return None

    def create_movies_post(self):
        """Crea publicación sobre películas"""
        try:
            logger.info("Generando publicacion de peliculas...")
            articles = self.content_fetcher.fetch_news('peliculas', limit=3)
            if not articles:
                return None
            article = random.choice(articles)
            
            image_path = None
            if article.get('image_url'):
                image_path = f"data/images/movie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                self.content_fetcher.download_image(article['image_url'], image_path)
            
            templates = [
                f"🎬 **Nuevo en el cine de acción**\n\n{article['title']}\n\n{article['summary']}\n\n🔗 {article['link']}\n\n#Cine #Películas #Acción #Marvel #DC",
                f"🍿 **Estrenos y novedades**\n\n{article['title']}\n\n{article['summary']}\n\n#Cine #Estrenos #Películas"
            ]
            content = random.choice(templates)
            post_image = self.meme_generator.create_post_image(article['title'], "🎬 Cine de Acción", image_path)
            return {'content': content, 'image': post_image}
        except Exception as e:
            logger.error(f"Error en publicacion de peliculas: {e}")
            return None

    def post_random_topic(self):
        """Publica sobre un tema aleatorio"""
        topics = [
            ('ia', self.create_ai_post),
            ('memes', self.create_meme_post),
            ('videojuegos', self.create_videojuegos_post),
            ('peliculas', self.create_movies_post)
        ]
        topic, creator = random.choice(topics)
        logger.info(f"Publicando sobre: {topic}")
        post_data = creator()
        if post_data:
            return self.publish_post(post_data)
        return False

    def publish_post(self, post_data):
        """Publica el contenido en LinkedIn"""
        try:
            if not post_data:
                return False
            content = post_data['content']
            image_path = post_data.get('image')
            success = self.linkedin_poster.create_post(content, image_path)
            if success:
                self.post_history.append({
                    'date': datetime.now().isoformat(),
                    'content': content[:100] + '...',
                    'image': image_path
                })
                self.save_history()
            return success
        except Exception as e:
            logger.error(f"Error publicando: {e}")
            return False

    def start_scheduler(self):
        """Inicia el programador"""
        if self.is_running:
            logger.warning("El scheduler ya esta corriendo")
            return
        
        self.is_running = True
        logger.info("Iniciando scheduler...")
        
        # Programar publicaciones:
        # 1. Cada 4 horas, un tema aleatorio
        schedule.every(4).hours.do(self.post_random_topic)
        
        # 2. Publicaciones fijas a horas específicas (usando partial para pasar argumentos)
        #    Nota: estas funciones se ejecutarán en el momento programado
        schedule.every().day.at("08:00").do(partial(self.publish_post, self.create_ai_post()))
        schedule.every().day.at("12:00").do(partial(self.publish_post, self.create_meme_post()))
        schedule.every().day.at("16:00").do(partial(self.publish_post, self.create_videojuegos_post()))
        schedule.every().day.at("20:00").do(partial(self.publish_post, self.create_movies_post()))
        schedule.every().day.at("22:00").do(partial(self.publish_post, self.create_ai_post()))
        
        logger.info("Scheduler iniciado correctamente")
        
        # Loop principal
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                self.stop_scheduler()
                break
            except Exception as e:
                logger.error(f"Error en scheduler: {e}")
                time.sleep(60)

    def stop_scheduler(self):
        """Detiene el scheduler"""
        self.is_running = False
        self.linkedin_poster.close()
        logger.info("Scheduler detenido")