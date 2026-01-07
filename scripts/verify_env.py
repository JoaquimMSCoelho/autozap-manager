import sys
import os
import subprocess

def print_status(component, status, message=""):
    # Cores: Verde (92) = OK, Vermelho (91) = ERRO, Amarelo (93) = ALERTA
    color = "\033[92m" if status == "OK" else ("\033[91m" if status in ["ERRO", "CRÍTICO", "AUSENTE"] else "\033[93m")
    reset = "\033[0m"
    print(f"[{component.ljust(15)}] {color}{status}{reset} {message}")

def check_command(command, version_flag="--version"):
    """Verifica se um comando existe no sistema e retorna a versão."""
    try:
        result = subprocess.run(f"{command} {version_flag}", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip().split('\n')[0]
        else:
            return False, None
    except Exception:
        return False, None

def main():
    print("="*60)
    print("   VERIFICADOR DE AMBIENTE - AUTOZAP MANAGER")
    print("   Norma: Extremo Zero | Status: Validando...")
    print("="*60)
    
    # 1. Verificar Python
    py_version = sys.version.split()[0]
    if sys.version_info >= (3, 10):
        print_status("PYTHON", "OK", f"Versão: {py_version}")
    else:
        print_status("PYTHON", "ERRO", f"Versão obsoleta: {py_version}. Requer 3.10+")

    # 2. Verificar Node.js
    node_ok, node_ver = check_command("node", "-v")
    if node_ok:
        print_status("NODE.JS", "OK", f"Versão: {node_ver}")
    else:
        print_status("NODE.JS", "CRÍTICO", "Não instalado ou não está no PATH.")

    # 3. Verificar Ferramentas Essenciais
    tools = ["git", "npm"]
    for tool in tools:
        ok, ver = check_command(tool)
        if ok:
            print_status(tool.upper(), "OK", "Instalado")
        else:
            print_status(tool.upper(), "AUSENTE", "Instalação obrigatória necessária.")

    # 4. Verificar Estrutura de Pastas
    folders = ["backend", "frontend", "docs", "scripts"]
    print("-" * 60)
    all_folders_ok = True
    for folder in folders:
        if os.path.isdir(folder):
            print_status(f"DIR: {folder}", "OK", "Encontrado")
        else:
            print_status(f"DIR: {folder}", "ALERTA", "Não encontrado.")
            all_folders_ok = False

    # 5. Verificar Arquivos Críticos
    req_file = os.path.join("backend", "requirements.txt")
    if os.path.exists(req_file):
        print_status("REQ.TXT", "OK", "Encontrado em backend/")
    else:
        print_status("REQ.TXT", "ERRO", "backend/requirements.txt sumiu!")

    print("-" * 60)
    print("CONCLUSÃO DA ANÁLISE:")
    if all_folders_ok: 
        print("AMBIENTE APROVADO PARA DESENVOLVIMENTO.")
    else:
        print("AMBIENTE REQUER ATENÇÃO.")
    print("=" * 60)

if __name__ == "__main__":
    main()
