from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import urllib.parse
import psutil 
import sys # Importante para forçar o print

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.is_running = False

    def _log(self, message):
        """Força o print a aparecer no terminal do EXE imediatamente"""
        print(f"[ENGINE] {message}", flush=True)

    def _kill_zombies(self):
        self._log("Iniciando varredura de processos zumbis...")
        current_dir = os.getcwd()
        target_folder = "chrome_cache"
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline:
                        cmd_str = " ".join(cmdline)
                        if target_folder in cmd_str and current_dir in cmd_str:
                            proc.kill()
            except: pass

    def start(self):
        if self.is_running: 
            self._log("Tentativa de inicio ignorada: Já está rodando.")
            return {"status": "already_running"}

        try:
            self._kill_zombies()
            self._log("Configurando opções do Chrome...")
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Garante que o cache fique na pasta do EXE
            dir_path = os.getcwd()
            cache_path = os.path.join(dir_path, 'chrome_cache')
            self._log(f"Pasta de perfil definida para: {cache_path}")
            chrome_options.add_argument(f"user-data-dir={cache_path}")

            self._log("Baixando/Verificando Driver do Navegador (Isso pode demorar)...")
            try:
                driver_path = ChromeDriverManager().install()
                self._log(f"Driver encontrado em: {driver_path}")
            except Exception as e_driver:
                self._log(f"ERRO AO BAIXAR DRIVER: {e_driver}")
                raise e_driver

            self._log("Iniciando serviço do WebDriver...")
            service = Service(driver_path)
            
            self._log("Abrindo janela do Chrome...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self._log("Carregando WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            self.is_running = True
            self._log("SUCESSO: Navegador aberto!")
            return {"status": "success"}

        except Exception as e:
            self._log(f"ERRO FATAL AO INICIAR: {str(e)}")
            return {"status": "error", "message": str(e)}

    def stop(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.is_running = False
        return {"status": "success"}

    def send_message(self, phone, message_content):
        if not self.is_running: return {"status": "error", "message": "Robô desligado"}
        try:
            # Lógica simples e estável V1
            self._log(f"Enviando para {phone}...")
            text_msg = message_content
            media_path = None
            if "|||media:" in message_content:
                parts = message_content.split("|||media:")
                text_msg = parts[0].strip()
                media_path = parts[1].strip()

            encoded_text = urllib.parse.quote(text_msg) if text_msg else ""
            self.driver.get(f"https://web.whatsapp.com/send?phone={phone}&text={encoded_text}")
            
            try:
                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]')))
            except: 
                self._log(f"Timeout esperando chat de {phone}")
                return {"status": "error", "message": "Timeout"}
            
            time.sleep(2)

            if media_path and os.path.exists(media_path):
                self._log(f"Anexando arquivo: {media_path}")
                self.driver.execute_script("document.querySelectorAll(\"input[type='file']\").forEach(i => {i.style.display='block'; i.style.height='1px'; i.style.opacity='1';});")
                file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                if file_inputs:
                    file_inputs[0].send_keys(os.path.abspath(media_path))
                    time.sleep(3)
            
            if not media_path:
                try:
                    box = self.driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                    box.send_keys(Keys.ENTER)
                except: pass

            time.sleep(2)
            return {"status": "sent", "message": "Processado"}
        except Exception as e:
            self._log(f"Erro no envio: {e}")
            return {"status": "error", "message": str(e)}

bot_instance = WhatsAppBot()