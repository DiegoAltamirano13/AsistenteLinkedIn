from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
import textwrap
import os
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MemeGenerator:
    def __init__(self, config):
        self.config = config
        self.font_path = self.get_font_path()
        self.templates = self.load_templates()
        self.output_size = (1080, 1080)

    def get_font_path(self) -> str:
        """Busca la ruta de una fuente disponible"""
        possible_fonts = [
            'C:/Windows/Fonts/ArialBD.TTF',
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/verdanab.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/System/Library/Fonts/Helvetica.ttf'
        ]
        
        for font in possible_fonts:
            if os.path.exists(font):
                return font
        
        # Si no encuentra, usa la fuente por defecto de PIL
        return None

    def load_templates(self) -> List[Dict]:
        """Carga plantillas de memes locales"""
        templates = [
            {
                'name': 'default',
                'local_path': None,
                'positions': {'top_text': (100, 50), 'bottom_text': (100, 200)}
            }
        ]
        return templates

    def download_image(self, url: str, save_path: str):
        """Descarga una imagen"""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"✅ Imagen descargada: {save_path}")
                return True
        except Exception as e:
            logger.error(f"❌ Error descargando imagen: {e}")
            return False

    def create_meme(self, text: str, template_name: str = None, output_path: str = None) -> str:
        """Crea un meme con texto sobre un fondo"""
        try:
            # Crear un fondo simple
            img = Image.new('RGB', self.output_size, self.config['image']['background_color'])
            draw = ImageDraw.Draw(img)
            
            # Cargar fuente (si existe)
            font = None
            if self.font_path and os.path.exists(self.font_path):
                try:
                    font = ImageFont.truetype(self.font_path, 40)
                except:
                    font = ImageFont.load_default()
            else:
                font = ImageFont.load_default()
            
            # Dividir texto en líneas
            wrapper = textwrap.TextWrapper(width=30)
            text_lines = wrapper.wrap(text)
            
            # Calcular altura total del texto
            total_height = 0
            for line in text_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                total_height += bbox[3] - bbox[1] + 5
            
            # Posición centrada
            y_position = (self.output_size[1] - total_height) // 2
            
            # Dibujar cada línea
            for line in text_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x_position = (self.output_size[0] - text_width) // 2
                
                # Fondo para legibilidad
                padding = 10
                draw.rectangle(
                    [x_position - padding, y_position - padding, 
                     x_position + text_width + padding, y_position + (bbox[3] - bbox[1]) + padding],
                    fill=(0, 0, 0, 180)
                )
                
                # Texto en blanco
                draw.text((x_position, y_position), line, fill='white', font=font)
                y_position += (bbox[3] - bbox[1]) + 5
            
            # Guardar
            if not output_path:
                output_path = f"data/memes/meme_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, 'JPEG', quality=95)
            
            logger.info(f"✅ Meme creado: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error creando meme: {e}")
            return None

    def create_post_image(self, title: str, subtitle: str = "", image_path: str = None) -> str:
        """Crea una imagen para la publicación"""
        try:
            # Crear fondo
            img = Image.new('RGB', self.output_size, self.config['image']['background_color'])
            draw = ImageDraw.Draw(img)
            
            # Si hay imagen de fondo, usarla
            if image_path and os.path.exists(image_path):
                try:
                    bg_img = Image.open(image_path)
                    bg_img.thumbnail(self.output_size, Image.Resampling.LANCZOS)
                    x = (self.output_size[0] - bg_img.width) // 2
                    y = (self.output_size[1] - bg_img.height) // 2
                    img.paste(bg_img, (x, y))
                    # Oscurecer un poco
                    overlay = Image.new('RGB', self.output_size, (0, 0, 0))
                    overlay.putalpha(100)
                    img = Image.blend(img, overlay, 0.3)
                except:
                    pass
            
            # Fuentes
            font_title = None
            font_subtitle = None
            
            if self.font_path and os.path.exists(self.font_path):
                try:
                    font_title = ImageFont.truetype(self.font_path, 48)
                    font_subtitle = ImageFont.truetype(self.font_path, 30)
                except:
                    font_title = ImageFont.load_default()
                    font_subtitle = ImageFont.load_default()
            else:
                font_title = ImageFont.load_default()
                font_subtitle = ImageFont.load_default()
            
            # Dibujar título
            wrapper = textwrap.TextWrapper(width=25)
            title_lines = wrapper.wrap(title)
            
            # Calcular altura total
            total_height = 0
            for line in title_lines:
                bbox = draw.textbbox((0, 0), line, font=font_title)
                total_height += bbox[3] - bbox[1] + 5
            
            y_text = (self.output_size[1] - total_height) // 2
            
            for line in title_lines:
                bbox = draw.textbbox((0, 0), line, font=font_title)
                x_text = (self.output_size[0] - (bbox[2] - bbox[0])) // 2
                # Sombra para legibilidad
                draw.text((x_text + 2, y_text + 2), line, fill='black', font=font_title)
                draw.text((x_text, y_text), line, fill='white', font=font_title)
                y_text += (bbox[3] - bbox[1]) + 5
            
            # Subtítulo
            if subtitle:
                bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
                x_text = (self.output_size[0] - (bbox[2] - bbox[0])) // 2
                y_text = self.output_size[1] - 100
                draw.text((x_text + 2, y_text + 2), subtitle, fill='black', font=font_subtitle)
                draw.text((x_text, y_text), subtitle, fill='white', font=font_subtitle)
            
            # Guardar
            output_path = f"data/images/post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, 'JPEG', quality=95)
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error creando imagen: {e}")
            return None