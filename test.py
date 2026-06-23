import random
import sys
import os
import time
sys.path.append(os.path.dirname(__file__))

from src.zernio_poster import ZernioClient
from src.content_fetcher import ContentFetcher
from src.content_generator import HuggingFaceGenerator
from src.calendar_fetcher import CalendarFetcher

# ============================================================
# CONFIGURACIÓN
# ============================================================
API_KEY = "sk_d413d7c8ecbb0bc2a64df1c5be6ccaba5213d76f19c25588685d29b62808b4f3"
PROFILE_ID = "6a3aab11ef4517c2bbde032a"
ACCOUNT_ID = "6a3aabbe5f7d1751ab626bfd"
PLATFORM = "facebook"

# ============================================================
# INICIALIZAR CLIENTES (con manejo de errores)
# ============================================================
zernio = ZernioClient(API_KEY)

# Fetcher (RSS + Reddit) - si no hay credenciales, se salta
try:
    fetcher = ContentFetcher(
        rss_feeds=["https://feeds.feedburner.com/TechCrunch"],
        reddit_client_id="",  # Pon tu client_id si quieres memes
        reddit_secret="",
        user_agent="AgenteSocial/1.0"
    )
except:
    fetcher = None

# Generador IA
generator = HuggingFaceGenerator()

# Calendar (opcional)
try:
    calendar = CalendarFetcher()
except:
    calendar = None

# ============================================================
# GENERAR CONTENIDO (con respaldos)
# ============================================================
def generate_random_content():
    """Retorna (texto, imagen_path) usando fuentes variadas."""
    content_type = random.choice(["news", "meme", "event", "ai_text", "ai_image", "ai_combined", "plain"])
    text = ""
    image_path = None

    try:
        if content_type == "news" and fetcher:
            news = fetcher.fetch_news(limit=1)
            if news:
                item = news[0]
                text = f"{item['title']}\n{item['summary']}\nFuente: {item['source']}\n{item['link']}"
            else:
                text = generator.generate_text("Dame una noticia de tecnología")
        elif content_type == "meme" and fetcher:
            image_path = fetcher.fetch_meme(["ProgrammerHumor", "dankmemes"])
            text = "😂 Meme del día" if image_path else "No se pudo obtener meme, usando texto alternativo."
        elif content_type == "event" and calendar:
            events = calendar.get_upcoming_events(days=3)
            if events:
                ev = random.choice(events)
                text = f"📅 {ev['summary']}\n📆 {ev['start']}\n🔗 {ev['link']}"
            else:
                text = generator.generate_text("Genera un recordatorio de productividad")
        elif content_type == "ai_text":
            prompt = random.choice([
                "Escribe un tweet sobre inteligencia artificial",
                "Dame un consejo de marketing digital",
                "Genera una frase motivadora para emprendedores"
            ])
            text = generator.generate_text(prompt)
        elif content_type == "ai_image":
            prompt = random.choice(["Un robot escribiendo código", "Paisaje futurista", "Ciudad inteligente"])
            image_path = generator.generate_image(prompt)
            text = f"🎨 {prompt}" if image_path else f"Intento de imagen fallido. Texto: {prompt}"
        elif content_type == "ai_combined":
            prompt = random.choice(["El futuro de la tecnología", "Consejos para emprendedores"])
            text = generator.generate_text(prompt)
            image_path = generator.generate_image(prompt)
            if not image_path:
                text += "\n(No se pudo generar imagen)"
        else:
            # Contenido de respaldo
            text = random.choice([
                "🚀 Publicación de prueba desde Agente Social.",
                "🤖 Probando la integración con Zernio.",
                "📢 Este es un post automático generado por IA."
            ])
    except Exception as e:
        text = f"⚠️ Error generando contenido: {e}. Usando texto de respaldo."
        print(text)

    # Asegurar que siempre haya texto
    if not text:
        text = "Contenido de prueba generado automáticamente."
    return text, image_path

# ============================================================
# PUBLICAR
# ============================================================
def publish_random_post():
    print("🚀 Generando contenido aleatorio...")
    text, image_path = generate_random_content()
    print(f"📝 Texto: {text[:150]}...")
    if image_path:
        print(f"🖼️ Imagen: {image_path}")

    platforms = [{"platform": PLATFORM, "accountId": ACCOUNT_ID}]
    try:
        result = zernio.create_post(text, platforms, publish_now=True)
        post = result.get("post", {})
        status = post.get("status")
        post_id = post.get("_id")
        print(f"✅ Post creado con ID: {post_id}, estado: {status}")
        if status == "published":
            print("🎉 ¡Publicado exitosamente en Facebook!")
        elif status == "draft":
            print("⚠️ El post quedó como borrador. Si quieres publicarlo manualmente, ve al panel de Zernio.")
            # Opcional: intentar publicar automáticamente con zernio.publish_post(post_id)
            try:
                print("Intentando publicar el borrador automáticamente...")
                publish_result = zernio.publish_post(post_id)
                new_status = publish_result.get("post", {}).get("status")
                print(f"Resultado: {new_status}")
            except Exception as e2:
                print(f"No se pudo publicar automáticamente: {e2}")
        else:
            print(f"ℹ️ Estado del post: {status}")
    except Exception as e:
        print(f"❌ Error al publicar: {e}")

if __name__ == "__main__":
    publish_random_post()