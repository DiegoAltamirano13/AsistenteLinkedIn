import os
import json
import sys
from flask import Blueprint, render_template, request, jsonify, session, url_for, send_from_directory
from src.zernio_poster import ZernioClient
from src.content_fetcher import ContentFetcher
from src.content_generator import HuggingFaceGenerator
from src.calendar_fetcher import CalendarFetcher
from src.scheduler import PostScheduler

bp = Blueprint('main', __name__)

# ============================================================
# CONFIGURACIÓN DE IDIOMAS, TEMAS Y FUENTES
# ============================================================

THEMES_BY_LANG = {
    'es': {
        'tecnologia': {
            'label': 'Tecnología',
            'rss': [
                "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/tecnologia",
                "https://www.bbc.com/mundo/ciencia_y_tecnologia/index.xml",
                "https://www.elmundo.es/rss/tecnologia.xml"
            ],
            'subreddits': ['tecnologia', 'programacion', 'linux', 'android', 'apple', 'gadgets']
        },
        'ciencia': {
            'label': 'Ciencia',
            'rss': [
                "https://www.abc.es/rss/feeds/abc_Ciencia.xml",
                "https://www.nationalgeographic.com.es/rss/ciencia",
                "https://www.muyinteresante.es/rss/feed.xml"
            ],
            'subreddits': ['ciencia', 'fisica', 'biologia', 'space', 'astronomia']
        },
        'deportes': {
            'label': 'Deportes',
            'rss': [
                "https://www.marca.com/rss/futbol.xml",
                "https://as.com/rss/tag/futbol.xml",
                "https://www.mundodeportivo.com/rss/futbol.xml"
            ],
            'subreddits': ['futbol', 'deportes', 'basket', 'tenis', 'formula1']
        },
        'entretenimiento': {
            'label': 'Entretenimiento',
            'rss': [
                "https://www.lavanguardia.com/mvc/feed/rss/cine",
                "https://www.elmundo.es/rss/cultura.xml",
                "https://www.20minutos.es/rss/feed.xml"
            ],
            'subreddits': ['peliculas', 'series', 'videojuegos', 'musica', 'cine']
        },
        'moda': {
            'label': 'Moda',
            'rss': [
                "https://www.vogue.es/rss/feed",
                "https://www.elle.com/es/rss/feed.xml",
                "https://www.harpersbazaar.com/es/rss/feed.xml"
            ],
            'subreddits': ['moda', 'fashion', 'estilo', 'tendencias']
        },
        'arquitectura': {
            'label': 'Arquitectura',
            'rss': [
                "https://www.archdaily.mx/rss",
                "https://www.plataformaarquitectura.cl/rss",
                "https://www.metalocus.es/rss.xml"
            ],
            'subreddits': ['arquitectura', 'architecture', 'diseno', 'urbanismo']
        },
        'videojuegos': {
            'label': 'Videojuegos',
            'rss': [
                "https://www.eurogamer.es/rss",
                "https://www.vidaextra.com/rss",
                "https://www.3djuegos.com/rss/feed.xml"
            ],
            'subreddits': ['videojuegos', 'gaming', 'pcgaming', 'consolas', 'nintendo']
        },
        'gastronomia': {
            'label': 'Gastronomía',
            'rss': [
                "https://www.directoalpaladar.com/rss",
                "https://www.elmundo.es/rss/gastronomia.xml",
                "https://www.abc.es/rss/feeds/abc_Comer.xml"
            ],
            'subreddits': ['cocina', 'gastronomia', 'recetas', 'comida']
        },
        'viajes': {
            'label': 'Viajes',
            'rss': [
                "https://www.lavanguardia.com/mvc/feed/rss/viajes",
                "https://www.elmundo.es/rss/viajes.xml",
                "https://www.abc.es/rss/feeds/abc_Viajes.xml"
            ],
            'subreddits': ['viajes', 'travel', 'turismo', 'aventura']
        },
        'economia': {
            'label': 'Economía',
            'rss': [
                "https://www.expansion.com/rss/portada.xml",
                "https://www.elmundo.es/rss/economia.xml",
                "https://www.abc.es/rss/feeds/abc_Economia.xml"
            ],
            'subreddits': ['economia', 'finanzas', 'negocios', 'inversion']
        }
    },
    'en': {
        'technology': {
            'label': 'Technology',
            'rss': [
                "https://feeds.feedburner.com/TechCrunch",
                "https://feeds.feedburner.com/wired/",
                "https://feeds.arstechnica.com/arstechnica/index",
                "https://www.theverge.com/rss/index.xml"
            ],
            'subreddits': ['technology', 'programming', 'linux', 'android', 'apple', 'gadgets']
        },
        'science': {
            'label': 'Science',
            'rss': [
                "https://www.sciencedaily.com/rss/all.xml",
                "https://www.nature.com/nature.rss",
                "https://www.sciencemag.org/rss/news_current.xml"
            ],
            'subreddits': ['science', 'physics', 'biology', 'space', 'astronomy']
        },
        'sports': {
            'label': 'Sports',
            'rss': [
                "https://www.espn.com/espn/rss/news",
                "https://www.si.com/rss/si_topstories.rss",
                "https://www.bbc.com/sport/rss.xml"
            ],
            'subreddits': ['sports', 'football', 'basketball', 'tennis', 'formula1']
        },
        'entertainment': {
            'label': 'Entertainment',
            'rss': [
                "https://www.eonline.com/rss/news",
                "https://www.rollingstone.com/music/music-news/feed/",
                "https://www.hollywoodreporter.com/rss"
            ],
            'subreddits': ['movies', 'television', 'music', 'gaming', 'entertainment']
        },
        'fashion': {
            'label': 'Fashion',
            'rss': [
                "https://www.vogue.com/rss/feed",
                "https://www.elle.com/rss/feed.xml",
                "https://www.harpersbazaar.com/rss/feed.xml"
            ],
            'subreddits': ['fashion', 'style', 'trends', 'streetwear']
        },
        'architecture': {
            'label': 'Architecture',
            'rss': [
                "https://www.archdaily.com/rss",
                "https://www.dezeen.com/feed",
                "https://www.architecturaldigest.com/rss.xml"
            ],
            'subreddits': ['architecture', 'design', 'urbanplanning']
        },
        'gaming': {
            'label': 'Gaming',
            'rss': [
                "https://www.ign.com/rss",
                "https://www.gamespot.com/rss",
                "https://www.polygon.com/rss/index.xml"
            ],
            'subreddits': ['gaming', 'pcgaming', 'consoles', 'nintendo', 'playstation', 'xbox']
        },
        'food': {
            'label': 'Food',
            'rss': [
                "https://www.foodnetwork.com/rss",
                "https://www.bonappetit.com/rss",
                "https://www.seriouseats.com/rss"
            ],
            'subreddits': ['food', 'cooking', 'recipes', 'gastronomy']
        },
        'travel': {
            'label': 'Travel',
            'rss': [
                "https://www.lonelyplanet.com/rss",
                "https://www.cntraveler.com/rss",
                "https://www.nationalgeographic.com/travel/rss"
            ],
            'subreddits': ['travel', 'tourism', 'adventure', 'backpacking']
        },
        'business': {
            'label': 'Business',
            'rss': [
                "https://feeds.feedburner.com/forbes",
                "https://www.bloomberg.com/feed",
                "https://www.economist.com/rss.xml"
            ],
            'subreddits': ['business', 'finance', 'investing', 'entrepreneur']
        }
    },
    'pt': {
        'tecnologia': {
            'label': 'Tecnologia',
            'rss': [
                "https://tecnoblog.net/feed",
                "https://www.tecmundo.com.br/feed",
                "https://canaltech.com.br/feed/"
            ],
            'subreddits': ['tecnologia', 'programacao', 'linux', 'android']
        },
        'ciencia': {
            'label': 'Ciência',
            'rss': [
                "https://revistagalileu.globo.com/rss/ciencia/",
                "https://www.nationalgeographic.pt/rss"
            ],
            'subreddits': ['ciencia', 'biologia', 'fisica', 'space']
        },
        'esportes': {
            'label': 'Esportes',
            'rss': [
                "https://globoesporte.globo.com/rss/esportes/",
                "https://www.record.pt/rss"
            ],
            'subreddits': ['futebol', 'esportes', 'basketball']
        },
        'entretenimento': {
            'label': 'Entretenimento',
            'rss': [
                "https://www.cinemablend.com/rss",
                "https://www.omelete.com.br/feed"
            ],
            'subreddits': ['filmes', 'series', 'jogos', 'musica']
        },
        'moda': {
            'label': 'Moda',
            'rss': [
                "https://ffw.com.br/feed",
                "https://www.vogue.globo.com/rss"
            ],
            'subreddits': ['moda', 'estilo', 'fashion']
        }
    },
    'fr': {
        'technologie': {
            'label': 'Technologie',
            'rss': [
                "https://www.lemonde.fr/technologies/rss_full.xml",
                "https://www.01net.com/feed/rss",
                "https://www.futura-sciences.com/rss/actualites.xml"
            ],
            'subreddits': ['technologie', 'programmation', 'informatique']
        },
        'science': {
            'label': 'Science',
            'rss': [
                "https://www.lemonde.fr/sciences/rss_full.xml",
                "https://www.sciencesetavenir.fr/rss.xml"
            ],
            'subreddits': ['science', 'astronomie', 'biologie']
        },
        'sport': {
            'label': 'Sport',
            'rss': [
                "https://www.lequipe.fr/rss/actu.xml",
                "https://www.sport.fr/feed"
            ],
            'subreddits': ['sport', 'football', 'tennis', 'cyclisme']
        },
        'divertissement': {
            'label': 'Divertissement',
            'rss': [
                "https://www.lefigaro.fr/culture/rss.xml",
                "https://www.telerama.fr/rss"
            ],
            'subreddits': ['cinema', 'series', 'jeuxvideos', 'musique']
        },
        'mode': {
            'label': 'Mode',
            'rss': [
                "https://www.lemonde.fr/mode/rss_full.xml",
                "https://www.vogue.fr/rss/feed"
            ],
            'subreddits': ['mode', 'style', 'luxe']
        }
    },
    'de': {
        'technologie': {
            'label': 'Technologie',
            'rss': [
                "https://www.heise.de/rss/news.rss",
                "https://www.golem.de/rss.xml",
                "https://www.computerbase.de/feed"
            ],
            'subreddits': ['technologie', 'programmierung', 'linux', 'android']
        },
        'wissenschaft': {
            'label': 'Wissenschaft',
            'rss': [
                "https://www.spektrum.de/rss/all",
                "https://www.nationalgeographic.de/rss"
            ],
            'subreddits': ['wissenschaft', 'physik', 'biologie', 'space']
        },
        'sport': {
            'label': 'Sport',
            'rss': [
                "https://www.kicker.de/rss",
                "https://www.sport1.de/rss/feed"
            ],
            'subreddits': ['sport', 'fussball', 'tennis', 'formel1']
        },
        'unterhaltung': {
            'label': 'Unterhaltung',
            'rss': [
                "https://www.spiegel.de/kultur/rss.xml",
                "https://www.faz.net/rss/aktuell/feuilleton"
            ],
            'subreddits': ['filme', 'serien', 'spiele', 'musik']
        },
        'mode': {
            'label': 'Mode',
            'rss': [
                "https://www.vogue.de/rss/feed",
                "https://www.harpersbazaar.de/rss/feed"
            ],
            'subreddits': ['mode', 'stil', 'fashion']
        }
    },
    'it': {
        'tecnologia': {
            'label': 'Tecnologia',
            'rss': [
                "https://www.hwupgrade.it/rss/news.xml",
                "https://www.tomshw.it/feed",
                "https://www.techprincess.it/feed"
            ],
            'subreddits': ['tecnologia', 'programmazione', 'linux', 'android']
        },
        'scienza': {
            'label': 'Scienza',
            'rss': [
                "https://www.lescienze.it/rss",
                "https://www.nationalgeographic.it/rss"
            ],
            'subreddits': ['scienza', 'fisica', 'biologia', 'spazio']
        },
        'sport': {
            'label': 'Sport',
            'rss': [
                "https://www.gazzetta.it/rss",
                "https://www.corrieredellosport.it/rss"
            ],
            'subreddits': ['sport', 'calcio', 'tennis', 'formula1']
        },
        'intrattenimento': {
            'label': 'Intrattenimento',
            'rss': [
                "https://www.repubblica.it/rss/cultura",
                "https://www.corriere.it/rss/cultura"
            ],
            'subreddits': ['cinema', 'serie', 'videogiochi', 'musica']
        },
        'moda': {
            'label': 'Moda',
            'rss': [
                "https://www.vogue.it/rss/feed",
                "https://www.elle.it/rss/feed"
            ],
            'subreddits': ['moda', 'stile', 'tendenze']
        }
    }
}

# ============================================================
# FUNCIÓN PARA OBTENER FEEDS POR DEFECTO SEGÚN IDIOMA
# ============================================================
def get_default_feeds(lang):
    """Devuelve feeds y subreddits por defecto para un idioma."""
    default_feeds = {
        'es': {
            'rss': [
                "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
                "https://www.bbc.com/mundo/index.xml",
                "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
                "https://actualidad.rt.com/rss"
            ],
            'subreddits': ["memexico", "spanishmemes", "Mujico"]
        },
        'en': {
            'rss': [
                "https://feeds.feedburner.com/TechCrunch",
                "https://feeds.feedburner.com/wired/",
                "https://feeds.arstechnica.com/arstechnica/index"
            ],
            'subreddits': ["ProgrammerHumor", "dankmemes", "techmemes"]
        },
        'pt': {
            'rss': [
                "https://tecnoblog.net/feed",
                "https://www.tecmundo.com.br/feed"
            ],
            'subreddits': ["brasil", "portugal"]
        },
        'fr': {
            'rss': [
                "https://www.lemonde.fr/technologies/rss_full.xml",
                "https://www.01net.com/feed/rss"
            ],
            'subreddits': ["france", "memes"]
        },
        'de': {
            'rss': [
                "https://www.heise.de/rss/news.rss",
                "https://www.golem.de/rss.xml"
            ],
            'subreddits': ["de", "ich_iel"]
        },
        'it': {
            'rss': [
                "https://www.hwupgrade.it/rss/news.xml",
                "https://www.tomshw.it/feed"
            ],
            'subreddits': ["italy", "memesITA"]
        }
    }
    return default_feeds.get(lang, default_feeds['es'])
# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
config = {}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    config = {
        "api_key": "",
        "profile_id": "",
        "platform_id": "",
        "account_id": "",
        "account_name": "",
        "language": "es",
        "active_themes": [],          # Lista de temas activos (para referencia)
        "active_rss_feeds": [],       # Lista de URLs RSS activas
        "active_subreddits": [],      # Lista de nombres de subreddits activos
        "custom_rss_feeds": [],       # Fuentes personalizadas (se añaden a las activas)
        "custom_subreddits": [],      # Subreddits personalizados
        "interval_hours": 1
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# Clientes globales
zernio = None
fetcher = None
generator = None
calendar = None
scheduler = None

def init_clients():
    global zernio, fetcher, generator, calendar
    
    print("🔄 Inicializando clientes...")
    
    if config.get("api_key"):
        try:
            zernio = ZernioClient(config["api_key"])
            print("✅ Zernio inicializado")
        except Exception as e:
            print(f"❌ Error en Zernio: {e}")
            zernio = None
    else:
        print("⚠️ No hay API Key")
    
    # Obtener listas activas o usar por defecto
    lang = config.get('language', 'es')
    
    rss_feeds = config.get('active_rss_feeds', [])
    subreddits = config.get('active_subreddits', [])
    
    # Si no hay fuentes activas, usar defaults
    if not rss_feeds or not subreddits:
        defaults = get_default_feeds(lang)
        if not rss_feeds:
            rss_feeds = defaults['rss']
        if not subreddits:
            subreddits = defaults['subreddits']
        # Guardar en config para futuras sesiones
        config['active_rss_feeds'] = rss_feeds
        config['active_subreddits'] = subreddits
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    # Añadir personalizados
    rss_feeds.extend(config.get('custom_rss_feeds', []))
    subreddits.extend(config.get('custom_subreddits', []))
    
    # Eliminar duplicados
    rss_feeds = list(dict.fromkeys(rss_feeds))
    subreddits = list(dict.fromkeys(subreddits))
    
    # Crear fetcher siempre
    try:
        fetcher = ContentFetcher(
            rss_feeds=rss_feeds,
            subreddits=subreddits,  # <--- ¡Asegurar que se pasa!
            user_agent="AgenteSocial/1.0"
        )
        print(f"✅ Fetcher creado con {len(fetcher.rss_feeds)} feeds y {len(fetcher.subreddits)} subreddits")
    except Exception as e:
        print(f"❌ Error creando Fetcher: {e}")
        fetcher = None
    
    # Si por alguna razón fetcher.subreddits sigue vacío, forzar
    if fetcher and not fetcher.subreddits:
        print("⚠️ fetcher.subreddits vacío, forzando defaults...")
        defaults = get_default_feeds(lang)
        fetcher.subreddits = defaults['subreddits']
        print(f"✅ Forzado: {fetcher.subreddits}")
    
    generator = HuggingFaceGenerator()
    try:
        calendar = CalendarFetcher()
        print("✅ Calendar inicializado")
    except:
        calendar = None

# Inicializar clientes
init_clients()

# ============================================================
# RUTAS DE PÁGINAS
# ============================================================
@bp.route('/')
def index():
    return render_template('index.html', config=config)

@bp.route('/config')
def config_page():
    return render_template('config.html', config=config)

@bp.route('/publish')
def publish_page():
    return render_template('publish.html', config=config)

@bp.route('/schedule')
def schedule_page():
    return render_template('schedule.html', config=config)

# ============================================================
# RUTAS API
# ============================================================

@bp.route('/api/config', methods=['GET', 'POST'])
def api_config():
    global config, zernio, fetcher
    if request.method == 'POST':
        data = request.json
        config.update(data)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        init_clients()
        return jsonify({"status": "ok", "message": "Configuración guardada"})
    else:
        safe = config.copy()
        return jsonify(safe)

@bp.route('/api/themes/<lang>')
def api_themes(lang):
    """Devuelve la lista de temas disponibles para un idioma."""
    if lang not in THEMES_BY_LANG:
        return jsonify({"error": "Idioma no soportado"}), 400
    themes = THEMES_BY_LANG[lang]
    result = [{"key": key, "label": data["label"], "rss": data.get("rss", []), "subreddits": data.get("subreddits", [])} for key, data in themes.items()]
    return jsonify(result)

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
        print("❌ zernio no inicializado")
        return jsonify({"error": "API Key no configurada"}), 400
    try:
        profile_id = config.get("profile_id")
        if not profile_id:
            print("ℹ️ No hay profile_id en config, intentando obtener perfiles...")
            profiles = zernio.get_profiles()
            print(f"📋 Perfiles obtenidos: {len(profiles) if profiles else 0}")
            if profiles:
                profile_id = profiles[0]["_id"]
                config["profile_id"] = profile_id
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"✅ Profile_id guardado: {profile_id}")
            else:
                print("❌ No se encontraron perfiles")
                return jsonify({"error": "No se encontró un perfil. Verifica que tu API Key sea válida."}), 400
        accounts = zernio.get_accounts(profile_id=profile_id)
        print(f"✅ Cuentas obtenidas: {len(accounts) if accounts else 0}")
        return jsonify(accounts)
    except Exception as e:
        print(f"❌ Error en api_accounts: {e}")
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
    platform = data.get('platform') or config.get('platform_id', 'facebook')
    if not account_id or not text:
        return jsonify({"error": "Faltan account_id o texto"}), 400
    if not zernio:
        return jsonify({"error": "Zernio no inicializado"}), 400
    try:
        platforms = [{"platform": platform, "accountId": account_id}]
        result = zernio.create_post(text, platforms, publish_now=True)
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/generate_text', methods=['POST'])
def api_generate_text():
    if not generator:
        return jsonify({"error": "Generador no disponible"}), 400
    data = request.json
    prompt = data.get('prompt', '')
    try:
        text = generator.generate_text(prompt)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/generate_image', methods=['POST'])
def api_generate_image():
    if not generator:
        return jsonify({"error": "Generador no disponible"}), 400
    data = request.json
    prompt = data.get('prompt', '')
    try:
        image_path = generator.generate_image(prompt)
        return jsonify({"image_path": image_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/news')
def api_news():
    if not fetcher:
        return jsonify({"error": "Fetcher no configurado. Revisa la configuración."}), 400
    try:
        news = fetcher.fetch_news(limit=5)
        if not news:
            return jsonify({"error": "No se encontraron noticias"}), 404
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/meme')
def api_meme():
    if not fetcher:
        return jsonify({"error": "Fetcher no configurado"}), 400
    
    # Obtener subreddits (del fetcher o de config)
    subreddits = getattr(fetcher, 'subreddits', None)
    if not subreddits:
        # Fallback: usar los de config
        subreddits = config.get('active_subreddits', [])
        if not subreddits:
            # Fallback final: defaults por idioma
            lang = config.get('language', 'es')
            defaults = get_default_feeds(lang)
            subreddits = defaults['subreddits']
            # Guardar para futuras ocasiones
            config['active_subreddits'] = subreddits
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
    
    if not subreddits:
        return jsonify({"error": "No hay subreddits disponibles"}), 400
    
    try:
        print(f"🔍 Intentando obtener meme de: {subreddits}")
        meme_path = fetcher.fetch_meme(subreddits)
        if meme_path:
            return jsonify({"meme_path": meme_path})
        else:
            # Si no se encontró, devolver más información
            return jsonify({"error": "No se encontró meme en los subreddits: " + ", ".join(subreddits)}), 404
    except Exception as e:
        print(f"❌ Excepción en /api/meme: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.route('/api/events')
def api_events():
    if not calendar:
        # Si no hay calendario configurado, devolvemos una lista vacía con código 200
        return jsonify([])
    try:
        events = calendar.get_upcoming_events(days=7)
        return jsonify(events)
    except Exception as e:
        # Si hay error al obtener eventos, devolvemos lista vacía
        print(f"⚠️ Error al obtener eventos: {e}")
        return jsonify([])

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

# ============================================================
# CALLBACK OAuth
# ============================================================
@bp.route('/callback')
def oauth_callback():
    temp_token = request.args.get('tempToken')
    connect_token = request.args.get('connectToken')
    platform = request.args.get('platform', 'facebook')
    error = request.args.get('error')
    if error:
        return render_template('callback.html', error=error, success=False)
    if not temp_token or not connect_token:
        return render_template('callback.html', error="Faltan parámetros", success=False)
    session['temp_token'] = temp_token
    session['connect_token'] = connect_token
    session['platform'] = platform
    try:
        profile_id = config.get("profile_id")
        if not profile_id:
            profiles = zernio.get_profiles() if zernio else []
            if profiles:
                profile_id = profiles[0]["_id"]
                config["profile_id"] = profile_id
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
        if not profile_id:
            return render_template('callback.html', error="No se encontró profileId", success=False)
        accounts = zernio.get_accounts(profile_id) if zernio else []
        page_id = None
        for acc in accounts:
            if acc.get("platform") == platform:
                metadata = acc.get("metadata", {})
                page_id = metadata.get("selectedPageId")
                if page_id:
                    break
        if not page_id:
            return render_template('select_page.html',
                                   platform=platform,
                                   temp_token=temp_token,
                                   connect_token=connect_token,
                                   error="No se encontró página. Introduce el ID.")
        result = zernio.select_page(platform, temp_token, connect_token, page_id)
        return render_template('callback.html', success=True, message=f"Cuenta de {platform} conectada correctamente.")
    except Exception as e:
        return render_template('callback.html', error=str(e), success=False)

@bp.route('/select-page', methods=['POST'])
def select_page_post():
    platform = request.form.get('platform')
    temp_token = request.form.get('tempToken')
    connect_token = request.form.get('connectToken')
    page_id = request.form.get('pageId')
    if not all([platform, temp_token, connect_token, page_id]):
        return "Faltan parámetros", 400
    try:
        result = zernio.select_page(platform, temp_token, connect_token, page_id)
        return render_template('callback.html', success=True, message=f"Cuenta de {platform} conectada correctamente.")
    except Exception as e:
        return render_template('callback.html', error=str(e), success=False)

# ============================================================
# SERVIR ARCHIVOS ESTÁTICOS (imágenes, memes)
# ============================================================
@bp.route('/data/<path:filename>')
def serve_data(filename):
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    return send_from_directory(data_dir, filename)

