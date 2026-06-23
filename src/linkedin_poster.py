# linkedin_poster.py
import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logger = logging.getLogger(__name__)

class LinkedInPoster:
    def __init__(self, config, headless=True):
        self.config = config
        self.driver = None
        self.is_logged_in = False
        
        self.options = EdgeOptions()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        
        # Perfil persistente
        user_data_dir = os.path.join(os.getcwd(), "edge_profile")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        self.options.add_argument(f"--user-data-dir={user_data_dir}")

    def login(self, username, password):
        try:
            logger.info("Iniciando sesion con Edge (perfil persistente)...")
            service = EdgeService(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=self.options)
            
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(5)
            
            if "feed" in self.driver.current_url:
                self.is_logged_in = True
                logger.info("Sesion restaurada desde perfil")
                return True
            
            # Intentar login automático
            try:
                email = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                email.send_keys(username)
                password_field = self.driver.find_element(By.ID, "password")
                password_field.send_keys(password)
                self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
                time.sleep(5)
                if "feed" in self.driver.current_url:
                    self.is_logged_in = True
                    logger.info("Login automatico exitoso")
                    return True
            except Exception as e:
                logger.warning(f"Login automatico fallo: {e}")
            
            # Login manual (solo una vez)
            print("\n" + "="*60)
            print(" INICIA SESION MANUALMENTE (esto solo se hace una vez)")
            print("="*60)
            input("Presiona Enter despues de iniciar sesion...")
            if "feed" in self.driver.current_url:
                self.is_logged_in = True
                logger.info("Sesion manual guardada en perfil")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return False

    def _open_publisher(self):
        """Abre el publicador de publicaciones usando el selector correcto"""
        try:
            # Buscar el botón "Crear publicación" por aria-label
            start_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Crear publicación']"))
            )
            self.driver.execute_script("arguments[0].click();", start_button)
            logger.info("Clic en 'Crear publicación'")
            time.sleep(4)
            return True
        except Exception as e:
            logger.warning(f"No se pudo abrir con aria-label: {e}")
            # Fallback: buscar por texto "Crear publicación"
            try:
                start_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Crear publicación')]"))
                )
                self.driver.execute_script("arguments[0].click();", start_button)
                logger.info("Clic en 'Crear publicación' (texto)")
                time.sleep(4)
                return True
            except Exception as e2:
                logger.error(f"Todos los intentos fallaron: {e2}")
                return False

    def _write_content_with_js(self, content):
        """Escribe contenido usando JavaScript directamente en el editor"""
        try:
            # Esperar a que el editor esté presente en el DOM
            editor = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor[contenteditable='true']"))
            )
            # Asegurarse de que el editor esté visible
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", editor)
            time.sleep(0.5)
            
            # Enfocar el editor
            self.driver.execute_script("arguments[0].focus();", editor)
            time.sleep(0.5)
            
            # Limpiar contenido previo
            self.driver.execute_script("arguments[0].innerHTML = '';", editor)
            
            # Convertir saltos de línea a <br> y establecer innerHTML
            html_content = content.replace('\n', '<br>')
            # También podríamos envolver en párrafos, pero con <br> es suficiente
            self.driver.execute_script("arguments[0].innerHTML = arguments[1];", editor, html_content)
            
            # Disparar eventos para que LinkedIn detecte el cambio
            self.driver.execute_script("""
                var editor = arguments[0];
                var events = ['input', 'change', 'keydown', 'keyup', 'keypress', 'textInput'];
                events.forEach(function(evtType) {
                    var evt = new Event(evtType, { bubbles: true, cancelable: true });
                    editor.dispatchEvent(evt);
                });
                // También disparar un evento de teclado específico
                var keyEvent = new KeyboardEvent('keydown', {
                    key: 'Enter',
                    code: 'Enter',
                    bubbles: true,
                    cancelable: true
                });
                editor.dispatchEvent(keyEvent);
            """, editor)
            
            logger.info("Contenido escrito con JavaScript")
            return True
            
        except Exception as e:
            logger.error(f"Error al escribir con JavaScript: {e}")
            return False

    def _upload_image(self, image_path):
        """Sube una imagen al modal"""
        try:
            # Buscar botón de imagen
            img_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Foto']"))
            )
            img_btn.click()
            time.sleep(1)
            # Buscar input file
            file_input = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(os.path.abspath(image_path))
            time.sleep(5)  # Esperar a que se suba la imagen
            logger.info("Imagen subida")
            return True
        except Exception as e:
            logger.warning(f"No se pudo subir imagen: {e}")
            return False

    def _click_publish(self):
        """Hace clic en el botón Publicar"""
        try:
            # Esperar a que el botón "Publicar" se habilite (no deshabilitado)
            post_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'share-actions__primary-action') and not(@disabled)]"))
            )
            self.driver.execute_script("arguments[0].click();", post_btn)
            logger.info("Publicacion realizada!")
            time.sleep(3)
            return True
        except Exception as e:
            # Fallback: buscar por texto "Publicar"
            try:
                post_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Publicar') and not(@disabled)]"))
                )
                self.driver.execute_script("arguments[0].click();", post_btn)
                logger.info("Publicacion realizada! (texto)")
                time.sleep(3)
                return True
            except Exception as e2:
                logger.error(f"No se pudo publicar: {e2}")
                return False

    def create_post(self, content, image_path=None):
        if not self.is_logged_in:
            logger.error("No hay sesion")
            return False

        try:
            logger.info("Creando publicacion...")
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(4)

            # 1. Abrir el publicador
            if not self._open_publisher():
                logger.error("No se pudo abrir el publicador")
                return False

            # 2. Escribir el contenido con JavaScript
            if not self._write_content_with_js(content):
                logger.error("No se pudo escribir el contenido")
                return False

            # 3. Subir imagen (si se proporciona)
            if image_path and os.path.exists(image_path):
                self._upload_image(image_path)

            # 4. Publicar
            if not self._click_publish():
                return False

            return True

        except Exception as e:
            logger.error(f"Error en create_post: {e}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info("Sesion cerrada")