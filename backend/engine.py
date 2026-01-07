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
import psutil # BIBLIOTECA DE LIMPEZA SEGURA

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.is_running = False

    def _kill_zombies(self):
        """
        FAXINEIRO CIRÚRGICO (SAFE MODE):
        Varre os processos e só mata o Chrome se ele estiver rodando 
        dentro da pasta 'chrome_cache' deste projeto.
        Protege o navegador pessoal do usuário.
        """
        print("[INFO] Iniciando varredura de processos zumbis...")
        
        current_dir = os.getcwd()
        target_folder = "chrome_cache"
        killed_count = 0
        
        # 1. Mata Drivers (ChromeDriver é seguro matar pois é só de automação)
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and 'chromedriver' in proc.info['name'].lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # 2. Mata Chromes ESPECÍFICOS do Robô
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Verifica se é chrome
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline:
                        # Transforma lista de comandos em string
                        cmd_str = " ".join(cmdline)
                        
                        # A LÓGICA DE SEGURANÇA:
                        # Só mata se o comando conter o caminho da nossa pasta de cache
                        if target_folder in cmd_str and current_dir in cmd_str:
                            print(f"[CLEANER] Matando Chrome Zumbi (PID: {proc.info['pid']})...")
                            proc.kill()
                            killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed_count > 0:
            print(f"[INFO] Limpeza concluída. {killed_count} processos do robô removidos.")
            time.sleep(2) # Tempo para o Windows liberar o arquivo
        else:
            print("[INFO] Nenhum processo zumbi encontrado. Sistema limpo.")

    def start(self):
        """Inicia o navegador Chrome controlado."""
        if self.is_running:
            return {"status": "already_running", "message": "Robo ja esta rodando!"}

        try:
            # --- LIMPEZA SEGURA ANTES DE INICIAR ---
            self._kill_zombies()

            print("[INFO:AutoZapEngine] --- MOTOR V11: SURGICAL CLEANER & OMNI-ENGINE ---")
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Cache do Perfil (Onde fica o Login)
            dir_path = os.getcwd()
            profile_path = os.path.join(dir_path, "chrome_cache")
            chrome_options.add_argument(f"user-data-dir={profile_path}")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("[INFO] Abrindo WhatsApp...")
            self.driver.get("https://web.whatsapp.com")
            
            self.is_running = True
            return {"status": "success", "message": "Navegador iniciado com sucesso."}
        except Exception as e:
            print(f"[ERRO CRITICO AO INICIAR] {str(e)}")
            return {"status": "error", "message": str(e)}

    def stop(self):
        """Para o navegador."""
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.is_running = False
        return {"status": "success", "message": "Navegador fechado."}

    def _force_click(self, element):
        """Clique via JS para garantir que nada bloqueie"""
        self.driver.execute_script("arguments[0].click();", element)

    def send_message(self, phone, message_content):
        """Lógica central de envio unificada."""
        if not self.is_running or not self.driver:
            return {"status": "error", "message": "O robo esta desligado."}

        try:
            # 1. Preparação
            text_msg = message_content
            media_path = None
            
            if "|||media:" in message_content:
                parts = message_content.split("|||media:")
                text_msg = parts[0].strip()
                media_path = parts[1].strip()

            print(f"\n[ENGINE] Disparando para: {phone} | Mídia: {'SIM' if media_path else 'NÃO'}")

            # 2. Navegação
            encoded_text = urllib.parse.quote(text_msg) if text_msg else ""
            link = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_text}"
            self.driver.get(link)

            # 3. Aguarda Chat
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
            except:
                print(f"[TIMEOUT] Chat nao carregou para {phone}. Pulando...")
                return {"status": "error", "message": "Timeout chat"}

            time.sleep(2)

            # 4. ROTINA DE ARQUIVO
            if media_path:
                if not os.path.exists(media_path):
                    print(f"[ERRO] Arquivo nao existe: {media_path}")
                else:
                    try:
                        print(f"[ENGINE] Injetando midia: {media_path}")
                        
                        # Revela inputs ocultos
                        self.driver.execute_script("""
                        document.querySelectorAll("input[type='file']").forEach(i => {
                            i.style.display='block'; i.style.height='1px'; i.style.opacity='1';
                        });
                        """)
                        
                        file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                        if not file_inputs: raise Exception("Input file sumiu")

                        target = file_inputs[0]
                        ext = os.path.splitext(media_path)[1].lower()
                        is_video = ext in ['.mp4', '.avi', '.mov', '.mkv']
                        
                        # Tenta input especifico de imagem/video se necessario
                        if ext in ['.jpg', '.jpeg', '.png', '.mp4', '.avi']:
                             for inp in file_inputs:
                                if "image" in (inp.get_attribute("accept") or ""):
                                    target = inp
                                    break
                        
                        target.send_keys(os.path.abspath(media_path))
                        print("[ENGINE] Caminho injetado. Aguardando Preview...")

                        # SMART WAIT (Espera Inteligente)
                        wait_time = 15 if is_video else 4
                        time.sleep(wait_time) 
                        
                        # OMNI-CLICKER (Busca agressiva pelo botão enviar)
                        selectors = [
                            '//span[@data-icon="send"]', 
                            '//div[@aria-label="Enviar"]',
                            '//span[@data-icon="send-light"]'
                        ]
                        
                        clicked = False
                        start_try = time.time()
                        print("[ENGINE] Procurando botão de enviar no preview...")
                        while time.time() - start_try < 10:
                            for xpath in selectors:
                                try:
                                    btns = self.driver.find_elements(By.XPATH, xpath)
                                    for btn in btns:
                                        if btn.is_displayed():
                                            self._force_click(btn)
                                            clicked = True
                                            print(f"[ENGINE] SUCESSO: Clicado no Preview com {xpath}")
                                            break
                                    if clicked: break
                                except: pass
                            if clicked: break
                            time.sleep(1)

                        if not clicked:
                            print("[AVISO] Omni-Clicker falhou. Tentando Enter.")
                            webdriver.ActionChains(self.driver).send_keys(Keys.ENTER).perform()

                        time.sleep(15 if is_video else 5)
                        return {"status": "sent", "message": "Enviado com anexo"}

                    except Exception as e:
                        print(f"[FALHA ANEXO] {str(e)}")

            # 5. ROTINA DE TEXTO (Só se tiver texto e anexo falhou ou não existe)
            if text_msg and text_msg.strip() != "":
                try:
                    if "http" in text_msg:
                        print("[ENGINE] Link detectado. Aguardando preview...")
                        time.sleep(3)

                    box = self.driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                    if box.text.strip():
                        box.send_keys(Keys.ENTER)
                        print("[ENGINE] Texto/Link enviado.")
                    else:
                        print("[ENGINE] Caixa vazia (Texto ja foi com anexo).")
                except:
                    pass 

            time.sleep(2)
            return {"status": "sent", "message": "Processado"}

        except Exception as e:
            print(f"[ERRO GERAL] {str(e)}")
            return {"status": "error", "message": str(e)}

bot_instance = WhatsAppBot()