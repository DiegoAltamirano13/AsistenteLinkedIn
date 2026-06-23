#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import yaml
from dotenv import load_dotenv
from datetime import datetime
import argparse
import io

# ===== CONFIGURACIÓN DE CODIFICACIÓN PARA WINDOWS =====
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    try:
        import subprocess
        subprocess.run('chcp 65001', shell=True, capture_output=True)
    except:
        pass

load_dotenv()

# Configurar logging SIN emojis (para evitar errores)
class NoEmojiFilter(logging.Filter):
    def filter(self, record):
        replacements = {
            '✅': '[OK]', '❌': '[ERROR]', '🔐': '[LOCK]', '🔒': '[LOCKED]',
            '📝': '[WRITE]', '🧪': '[TEST]', '🤖': '[BOT]', '📡': '[FETCH]',
            '📷': '[PHOTO]', '⚠️': '[WARN]', '🚀': '[START]', '📱': '[MOBILE]',
            '⏰': '[TIME]', '🔍': '[DEBUG]', '💡': '[TIP]', '📋': '[LIST]',
            '📌': '[PIN]', '🎯': '[TARGET]', '🔄': '[REFRESH]', '▶️': '[PLAY]',
            '🔥': '[HOT]', '⚡': '[FAST]', '🎮': '[GAME]', '🍿': '[MOVIE]',
            '💻': '[PC]', '🤝': '[HANDSHAKE]', '📊': '[STATS]', '🔗': '[LINK]'
        }
        for emoji, text in replacements.items():
            if emoji in record.msg:
                record.msg = record.msg.replace(emoji, text)
        return True

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_agent.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
for handler in logging.root.handlers:
    handler.addFilter(NoEmojiFilter())

logger = logging.getLogger(__name__)

from src.content_fetcher import ContentFetcher
from src.meme_generator import MemeGenerator
from src.linkedin_poster import LinkedInPoster
from src.scheduler import PostScheduler

def ensure_directories():
    """Crea las carpetas necesarias si no existen"""
    for folder in ['data', 'data/images', 'data/memes', 'data/posts']:
        os.makedirs(folder, exist_ok=True)

def load_config():
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info("Configuracion cargada")
        return config
    except Exception as e:
        logger.error(f"Error cargando configuracion: {e}")
        sys.exit(1)

def test_publication(config, headless=True):
    logger.info("Ejecutando prueba de publicacion...")
    try:
        content_fetcher = ContentFetcher(config)
        meme_generator = MemeGenerator(config)
        poster = LinkedInPoster(config, headless=headless)
        username = os.getenv('LINKEDIN_USER')
        password = os.getenv('LINKEDIN_PASS')
        if not poster.login(username, password):
            logger.error("Error al iniciar sesion")
            poster.close()
            return False
        articles = content_fetcher.fetch_news('ia', limit=1)
        if articles:
            article = articles[0]
            content = f"Prueba de publicacion\n\n{article['title']}\n\n{article['summary'][:200]}...\n\n{article['link']}\n\n#Test #LinkedIn"
            image_path = None
            if article.get('image_url'):
                image_path = f"data/images/test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                content_fetcher.download_image(article['image_url'], image_path)
            success = poster.create_post(content, image_path)
            poster.close()
            if success:
                logger.info("Publicacion de prueba exitosa")
            else:
                logger.error("Fallo la publicacion de prueba")
            return success
        poster.close()
        return False
    except Exception as e:
        logger.error(f"Error en prueba: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='LinkedIn Agent - Publica contenido automaticamente')
    parser.add_argument('--test', action='store_true', help='Ejecutar prueba de publicacion')
    parser.add_argument('--once', help='Publicar una vez sobre el tema especificado (ia|memes|videojuegos|peliculas)')
    parser.add_argument('--start', action='store_true', help='Iniciar el scheduler')
    parser.add_argument('--visible', action='store_true', help='Mostrar el navegador (no headless)')
    args = parser.parse_args()
    
    logger.info("Iniciando LinkedIn Agent...")
    ensure_directories()
    
    config = load_config()
    
    if not os.getenv('LINKEDIN_USER') or not os.getenv('LINKEDIN_PASS'):
        logger.error("Faltan credenciales de LinkedIn en el archivo .env")
        sys.exit(1)
    
    headless = not args.visible  # Por defecto headless=True, si se pasa --visible se desactiva
    
    if args.test:
        success = test_publication(config, headless=headless)
        sys.exit(0 if success else 1)
    
    if args.once:
        logger.info(f"Publicando una vez sobre: {args.once}")
        content_fetcher = ContentFetcher(config)
        meme_generator = MemeGenerator(config)
        poster = LinkedInPoster(config, headless=headless)
        if not poster.login(os.getenv('LINKEDIN_USER'), os.getenv('LINKEDIN_PASS')):
            sys.exit(1)
        scheduler = PostScheduler(content_fetcher, meme_generator, poster)
        creators = {
            'ia': scheduler.create_ai_post,
            'memes': scheduler.create_meme_post,
            'videojuegos': scheduler.create_videojuegos_post,
            'peliculas': scheduler.create_movies_post
        }
        if args.once in creators:
            post_data = creators[args.once]()
            if post_data:
                success = scheduler.publish_post(post_data)
                poster.close()
                sys.exit(0 if success else 1)
        poster.close()
        sys.exit(1)
    
    if args.start:
        content_fetcher = ContentFetcher(config)
        meme_generator = MemeGenerator(config)
        poster = LinkedInPoster(config, headless=headless)
        if not poster.login(os.getenv('LINKEDIN_USER'), os.getenv('LINKEDIN_PASS')):
            sys.exit(1)
        scheduler = PostScheduler(content_fetcher, meme_generator, poster)
        scheduler.start_scheduler()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()