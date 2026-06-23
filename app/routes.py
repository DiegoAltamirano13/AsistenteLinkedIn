import os
import json
import sys
from flask import Blueprint, render_template, request, jsonify, redirect, session, url_for
from src.zernio_poster import ZernioClient
from src.content_fetcher import ContentFetcher
from src.content_generator import HuggingFaceGenerator
from src.calendar_fetcher import CalendarFetcher
from src.scheduler import PostScheduler

bp = Blueprint('main', __name__)

# Configuración
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
config = {}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

# Inicializar clientes globales
zernio = None
fetcher = None
generator = None
calendar = None
scheduler = None

def init_clients():
    global zernio, fetcher, generator, calendar
    api_key = config.get("api_key")
    if api_key:
        zernio = ZernioClient(api_key)
    # Fetcher (RSS + Reddit) - requiere credenciales
    if config.get("reddit_client_id") and config.get("reddit_secret"):
        fetcher = ContentFetcher(
            rss_feeds=config.get("rss_feeds", []),
            reddit_client_id=config["reddit_client_id"],
            reddit_secret=config["reddit_secret"],
            user_agent="AgentSocial/1.0"
        )
    generator = HuggingFaceGenerator()
    try:
        calendar = CalendarFetcher()
    except:
        calendar = None

init_clients()

# ===================== RUTAS DE PÁGINAS =====================

@bp.route('/')
def index():
    return render_template('index.html', config=config)

@bp.route('/config')
def config_page():
    return render_template('config.html', config=config)

@bp.route('/platforms')
def platforms_page():
    return render_template('platforms.html', config=config)

@bp.route('/publish')
def publish_page():
    return render_template('publish.html', config=config)

@bp.route('/schedule')
def schedule_page():
    return render_template('schedule.html', config=config)

# ===================== API =====================

@bp.route('/api/config', methods=['GET', 'POST'])
def api_config():
    global config, zernio
    if request.method == 'POST':
        data = request.json
        config.update(data)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        init_clients()
        return jsonify({"status": "ok", "message": "Configuración guardada"})
    else:
        safe = config.copy()
        safe.pop('reddit_secret', None)
        return jsonify(safe)

@bp.route('/api/profiles')
def api_profiles():
    if not zernio:
        return jsonify({"error": "API Key no configurada"}), 400
    try:
        profiles = zernio.get_profiles()
        return jsonify(profiles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/accounts')
def api_accounts():
    if not zernio:
        return jsonify({"error": "API Key no configurada"}), 400
    try:
        profile_id = config.get("profile_id")
        if not profile_id:
            # Intentar obtener el primer perfil automáticamente
            profiles = zernio.get_profiles()
            if profiles:
                profile_id = profiles[0]["_id"]
                config["profile_id"] = profile_id
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
            else:
                return jsonify({"error": "No se encontró un perfil. Conecta una cuenta primero."}), 400
        accounts = zernio.get_accounts(profile_id=profile_id)
        # Devolver solo el array de cuentas
        return jsonify(accounts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/connect/<platform>', methods=['POST'])
def api_connect(platform):
    if not zernio:
        return jsonify({"error": "API Key no configurada"}), 400
    data = request.json
    profile_id = data.get('profileId') or config.get("profile_id")
    redirect_uri = data.get('redirectUri')
    if not profile_id or not redirect_uri:
        return jsonify({"error": "Faltan profileId o redirectUri"}), 400
    try:
        auth_url = zernio.get_connect_url(platform, profile_id, redirect_uri)
        return jsonify({"authUrl": auth_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/select-page', methods=['POST'])
def api_select_page():
    if not zernio:
        return jsonify({"error": "API Key no configurada"}), 400
    data = request.json
    platform = data.get('platform')
    temp_token = data.get('tempToken')
    connect_token = data.get('connectToken')
    page_id = data.get('pageId')
    if not all([platform, temp_token, connect_token, page_id]):
        return jsonify({"error": "Faltan parámetros"}), 400
    try:
        result = zernio.select_page(platform, temp_token, connect_token, page_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/publish', methods=['POST'])
def api_publish():
    data = request.json
    account_id = data.get('account_id') or config.get('account_id')
    text = data.get('text', '')
    if not account_id:
        return jsonify({"error": "Falta account_id"}), 400
    if not zernio:
        return jsonify({"error": "Zernio no inicializado"}), 400
    try:
        result = zernio.post_content(account_id, text)
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/generate_text', methods=['POST'])
def api_generate_text():
    data = request.json
    prompt = data.get('prompt', '')
    if not generator:
        return jsonify({"error": "Generador no disponible"}), 400
    try:
        text = generator.generate_text(prompt)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/generate_image', methods=['POST'])
def api_generate_image():
    data = request.json
    prompt = data.get('prompt', '')
    if not generator:
        return jsonify({"error": "Generador no disponible"}), 400
    try:
        image_path = generator.generate_image(prompt)
        return jsonify({"image_path": image_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/news')
def api_news():
    if not fetcher:
        return jsonify({"error": "Fetcher no configurado"}), 400
    try:
        news = fetcher.fetch_news(limit=5)
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/meme')
def api_meme():
    if not fetcher:
        return jsonify({"error": "Fetcher no configurado"}), 400
    try:
        meme_path = fetcher.fetch_meme(config.get("subreddits", []))
        if meme_path:
            return jsonify({"meme_path": meme_path})
        else:
            return jsonify({"error": "No se pudo obtener meme"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/events')
def api_events():
    if not calendar:
        return jsonify({"error": "Calendar no configurado"}), 400
    try:
        events = calendar.get_upcoming_events(days=7)
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/schedule', methods=['POST'])
def api_schedule():
    global scheduler
    data = request.json
    action = data.get('action')
    interval = data.get('interval_hours', 1)

    if action == 'start':
        if scheduler and scheduler.running:
            return jsonify({"status": "already_running"})
        def auto_post():
            print("Publicación automática ejecutada")
        scheduler = PostScheduler(auto_post, interval_hours=interval)
        scheduler.start()
        return jsonify({"status": "started", "interval": interval})
    elif action == 'stop':
        if scheduler and scheduler.running:
            scheduler.stop()
            scheduler = None
            return jsonify({"status": "stopped"})
        return jsonify({"status": "not_running"})
    elif action == 'change_interval':
        if scheduler and scheduler.running:
            scheduler.change_interval(interval)
            return jsonify({"status": "interval_changed", "interval": interval})
        return jsonify({"status": "not_running"})
    return jsonify({"error": "Acción no válida"}), 400

# Servir archivos estáticos
@bp.route('/data/<path:filename>')
def serve_data(filename):
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    return send_from_directory(data_dir, filename)