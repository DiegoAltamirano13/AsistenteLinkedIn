# 🤖 Agente Social Multiplataforma

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?logo=flask)
![Zernio](https://img.shields.io/badge/Zernio-API-purple)
![Status](https://img.shields.io/badge/status-estable-brightgreen)

**Agente Social** es una aplicación **todo en uno** para la gestión y publicación automatizada de contenido en redes sociales. Conecta con **Zernio** para publicar en Facebook, Instagram, Twitter, LinkedIn, Telegram y más. Además, genera contenido automáticamente desde **RSS**, **Reddit** (memes), **Google Calendar** e **IA** (texto e imágenes con Hugging Face).

---

## ✨ Características principales

- 🔑 **Configuración segura** de API Key de Zernio (guardada localmente en `config.json`).
- 📡 **Selección de plataformas y cuentas** vinculadas a tu perfil de Zernio.
- 📰 **Noticias**: Obtén las últimas noticias de tus fuentes RSS favoritas (con soporte multiidioma).
- 🖼️ **Memes**: Descarga memes de Reddit sin necesidad de credenciales (usando feeds RSS).
- 📅 **Eventos**: Importa eventos de Google Calendar.
- 🤖 **IA gratuita**: Genera texto (Mistral) e imágenes (Stable Diffusion) usando Hugging Face Inference API.
- 🚀 **Publicación manual**: Previsualiza y publica contenido en la red seleccionada.
- ⏰ **Programación automática**: Publica contenido rotativo cada X horas.
- 🌍 **Multiidioma**: Elige entre Español, Inglés, Portugués, Francés, Alemán e Italiano.
- 🎯 **Temas personalizables**: Selecciona temas (Tecnología, Ciencia, Moda, etc.) y combina fuentes RSS y subreddits.
- 🧩 **Interfaz web moderna**: Diseño glassmorphism con tonos morados y azules, totalmente responsive.

---

## 📦 Requisitos previos

- Python 3.10 o superior
- Una cuenta en [Zernio](https://app.zernio.com) con API Key generada
- (Opcional) Archivo `credentials.json` para Google Calendar (sigue la [guía oficial](https://developers.google.com/calendar/api/quickstart/python))
- (Opcional) Token de Hugging Face para mayor límite de uso

---

## 🚀 Instalación y puesta en marcha

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/agente-social.git
   cd agente-social
   ```

2. **Crea y activa un entorno virtual**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno** (opcional)
   Crea un archivo `.env` en la raíz con:
   ```env
   ZERNIO_API_KEY=tu_api_key
   HUGGINGFACE_TOKEN=tu_token_opcional
   ```

5. **Ejecuta la aplicación**
   ```bash
   python main_web.py
   ```
   El navegador se abrirá automáticamente en `http://localhost:5000`.

---

## 🖥️ Uso

### 1. Configuración inicial
- Ve a la pestaña **Configuración**.
- Introduce tu **API Key de Zernio** y **Profile ID** (se obtiene automáticamente al guardar).
- Selecciona tu **idioma** preferido y los **temas** que te interesan.
- Las fuentes RSS y subreddits se combinarán automáticamente.
- También puedes añadir **fuentes personalizadas** (RSS o subreddits).

### 2. Conectar cuentas sociales
- En la sección **"Conectar nueva plataforma"**, haz clic en el botón de la red deseada.
- Se abrirá una ventana de autorización de Zernio. Sigue los pasos para vincular tu cuenta.
- Una vez conectada, la cuenta aparecerá en la lista y podrás seleccionarla para publicar.

### 3. Publicar contenido
- Ve a la pestaña **Publicar**.
- Escribe tu mensaje o usa los botones para cargar una noticia, meme o evento.
- También puedes generar texto o imagen con IA.
- Previsualiza el contenido y haz clic en **"Publicar ahora"**.

### 4. Programar publicaciones automáticas
- Ve a la pestaña **Programar**.
- Establece el intervalo en horas y haz clic en **"Iniciar programador"**.
- El sistema generará y publicará contenido rotativo (noticias, memes, eventos, IA) cada X horas.

---

## 🗂️ Estructura del proyecto

```
AgentSocial/
├── app/
│   ├── __init__.py
│   ├── routes.py                # Rutas Flask y lógica de API
│   ├── static/
│   │   ├── css/style.css        # Estilos glassmorphism
│   │   └── js/app.js            # JavaScript auxiliar
│   └── templates/
│       ├── index.html           # Página principal
│       ├── config.html          # Configuración (idiomas, temas, cuentas)
│       ├── publish.html         # Publicación manual
│       ├── schedule.html        # Programación automática
│       ├── callback.html        # Callback OAuth
│       └── select_page.html     # Selección de página (Facebook, etc.)
├── src/
│   ├── zernio_poster.py        # Cliente para API de Zernio
│   ├── content_fetcher.py      # RSS, Reddit (memes)
│   ├── content_generator.py    # IA (Hugging Face)
│   ├── calendar_fetcher.py     # Google Calendar
│   └── scheduler.py            # Programador de publicaciones
├── data/
│   ├── images/                 # Imágenes generadas por IA
│   └── memes/                  # Memes descargados
├── config.json                 # Configuración persistente
├── .env                        # Variables de entorno (opcional)
├── main_web.py                 # Punto de entrada
├── requirements.txt            # Dependencias
└── README.md                   # Este archivo
```

---

## ⚙️ Configuración avanzada

### Modificar temas y fuentes por idioma

Edita el diccionario `THEMES_BY_LANG` en `routes.py`. Cada idioma contiene temas con sus respectivas listas de RSS y subreddits. Puedes añadir o eliminar temas fácilmente.

### Añadir un nuevo idioma

1. Agrega una nueva clave al diccionario `THEMES_BY_LANG` con el código del idioma (ej. `'ja'`).
2. Define los temas y sus fuentes.
3. Añade el idioma al selector en `config.html`.
4. Añade la función `get_default_feeds` para ese idioma.

### Publicación con imagen

- Puedes adjuntar una imagen subiéndola desde el formulario o generándola con IA.
- La imagen se sube a Zernio junto con el texto.

---

## 🛠️ Solución de problemas

### Error 400 en `/api/meme`
- Asegúrate de que hay subreddits configurados (en `config.json` o por defecto).
- Reddit puede bloquear el acceso anónimo a JSON; la aplicación usa RSS como fallback.

### Error 401 en `/api/accounts`
- Verifica que la API Key de Zernio sea correcta y tenga permisos de lectura.
- Comprueba que el `profile_id` esté guardado en `config.json`.

### Google Calendar no disponible
- El endpoint `/api/events` devuelve una lista vacía si no hay `credentials.json`.
- No afecta al resto de funcionalidades.

### Las imágenes generadas no se muestran
- Asegúrate de que la carpeta `data/images/` exista y tenga permisos de escritura.
- La ruta `/data/<path:filename>` sirve archivos estáticos.

---

## 📚 Tecnologías utilizadas

- **Backend**: Flask, requests, feedparser, APScheduler
- **Frontend**: Bootstrap, jQuery, Font Awesome, CSS personalizado
- **APIs externas**: Zernio, Hugging Face, Google Calendar, Reddit (RSS)
- **Empaquetado**: PyInstaller (opcional, para generar `.exe`)

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- [Zernio](https://zernio.com) por su potente API de publicación social.
- [Hugging Face](https://huggingface.co) por los modelos de IA gratuitos.
- [Reddit](https://reddit.com) por los feeds RSS que aún funcionan.
- [Google](https://developers.google.com/calendar) por la API de Calendar.

---

## 📬 Contacto

Si tienes preguntas o sugerencias, abre un issue en el repositorio o contacta al mantenedor.

---

**¡Disfruta de tu Agente Social Multiplataforma!** 🚀
