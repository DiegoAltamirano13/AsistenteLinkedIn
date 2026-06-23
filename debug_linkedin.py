# debug_buttons.py
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
import os
from dotenv import load_dotenv

load_dotenv()

def debug():
    options = Options()
    options.add_argument("--start-maximized")
    
    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
    driver.get("https://www.linkedin.com/feed/")
    
    print("Abriendo navegador. Inicia sesion manualmente.")
    input("Presiona Enter despues de iniciar sesion...")
    
    # Buscar botones
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"\nTotal botones: {len(buttons)}")
    
    for i, btn in enumerate(buttons[:20]):  # Primeros 20
        text = btn.text[:50] if btn.text else ""
        aria = btn.get_attribute("aria-label") or ""
        if "Iniciar" in text or "Publicar" in text or "Iniciar" in aria or "Publicar" in aria:
            print(f"Botón {i}: text='{text}', aria='{aria}', class='{btn.get_attribute('class')}'")
    
    input("\nPresiona Enter para cerrar...")
    driver.quit()

if __name__ == "__main__":
    debug()