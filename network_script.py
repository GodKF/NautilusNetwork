import os
import subprocess
import time
import threading
import datetime

# --- CONFIGURACIÓN ---
GITHUB_PROFILE = "https://github.com/DasVicgeta"
BRANCH = "main"
ROOT_DIR = os.getcwd()
NETWORK_DIR = "my_network"

SERVERS = {
    "proxy": {"url": "https://api.papermc.io/v2/projects/velocity/versions/3.3.0-SNAPSHOT/builds/400/downloads/velocity-3.3.0-SNAPSHOT-400.jar", "java": "17"},
    "lobby": {"url": "https://api.papermc.io/v2/projects/paper/versions/1.21.1/builds/120/downloads/paper-1.21.1-120.jar", "java": "21"},
    "survival": {"url": "https://api.papermc.io/v2/projects/paper/versions/1.21.1/builds/120/downloads/paper-1.21.1-120.jar", "java": "21"}
}
PLAYIT_URL = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux-amd64"

CLR = {"CYAN": "\033[96m", "GREEN": "\033[92m", "YELLOW": "\033[93m", "RED": "\033[91m", "BOLD": "\033[1m", "END": "\033[0m"}
watchdog_active = False

def run_command_direct(command):
    try:
        subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{CLR['RED']}❌ Error: {e.stderr}{CLR['END']}")
        return False

# --- GESTIÓN DE HERRAMIENTAS ---

def setup_tools():
    """Prepara el entorno sin eliminar archivos existentes."""
    print(f"{CLR['CYAN']}📦 Verificando dependencias...{CLR['END']}")
    subprocess.run("sudo apt update && sudo apt install -y screen openjdk-17-jdk openjdk-21-jdk wget git git-lfs", shell=True, stdout=subprocess.DEVNULL)
    
    if not os.path.exists(NETWORK_DIR):
        os.makedirs(NETWORK_DIR)

# --- INICIO DE RED (MODO TERMINALES NATIVAS) ---

def is_running(name):
    """Verifica si la sesión de consola existe."""
    result = subprocess.run(f"screen -list | grep {name}", shell=True, capture_output=True, text=True)
    return name in result.stdout

def start_network_native():
    """Inicia los servidores en sesiones independientes compatibles con pestañas de VS Code."""
    print(f"{CLR['CYAN']}🚀 Lanzando servidores en pestañas independientes...{CLR['END']}")
    
    for name, data in SERVERS.items():
        if is_running(name):
            print(f"{CLR['YELLOW']}⚠️ {name} ya está encendido.{CLR['END']}")
            continue
            
        path = os.path.join(ROOT_DIR, NETWORK_DIR, name)
        if not os.path.exists(path): os.makedirs(path)
        
        # Comando de inicio
        java_cmd = "java -Xmx1G -jar server.jar nogui"
        
        # Lanzamos en una sesión de screen dedicada
        subprocess.run(f"screen -dmS {name} bash -c 'cd {path} && {java_cmd}'", shell=True)
        print(f"{CLR['GREEN']}✅ Consola creada para: {CLR['BOLD']}{name}{CLR['END']}")
        time.sleep(1)

# --- BACKUP Y RESTAURACIÓN ---

def make_backup_final():
    print(f"\n{CLR['CYAN']}🚀 Iniciando backup total...{CLR['END']}")
    os.chdir(ROOT_DIR)
    run_command_direct("git add .")
    msg = f"Backup: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(f'git commit -m "{msg}"', shell=True, stderr=subprocess.DEVNULL)
    if run_command_direct(f"git push origin {BRANCH}"):
        print(f"{CLR['GREEN']}✅ Todo guardado en GitHub.{CLR['END']}")

def restore_advanced():
    print(f"\n{CLR['YELLOW']}📥 RECUPERACIÓN PRO{CLR['END']}")
    print("1. Sincronizar repo actual | 2. Cargar desde otro link")
    opc = input("Selecciona: ")
    if opc == "1":
        run_command_direct("git fetch origin && git reset --hard origin/main && git lfs pull")
    elif opc == "2":
        url = input("Link del repo: ")
        if url:
            run_command_direct("rm -rf .git && git init")
            run_command_direct(f"git remote add origin {url}")
            run_command_direct("git fetch origin && git reset --hard origin/main && git lfs pull")

# --- MONITOR (WATCHDOG) ---

def watchdog_loop():
    while watchdog_active:
        for name in SERVERS.keys():
            if not is_running(name):
                path = os.path.join(ROOT_DIR, NETWORK_DIR, name)
                subprocess.run(f"screen -dmS {name} bash -c 'cd {path} && java -Xmx1G -jar server.jar nogui'", shell=True)
        time.sleep(25)

# --- MENÚ PRINCIPAL ---

def main_menu():
    global watchdog_active
    while True:
        os.system('clear')
        wd_status = f"{CLR['GREEN']}ON{CLR['END']}" if watchdog_active else f"{CLR['RED']}OFF{CLR['END']}"
        print(f"""
{CLR['CYAN']}╔══════════════════════════════════════════╗
║     {CLR['BOLD']}GESTOR DE NETWORK - CODESPACES{CLR['END']}       {CLR['CYAN']}║
╠══════════════════════════════════════════╣
║ {CLR['YELLOW']}1. ⚡ Playit{CLR['END']}      | {CLR['YELLOW']}4. 💾 Backup Total{CLR['END']}  ║
║ {CLR['GREEN']}2. 🎮 Iniciar Red (Pestañas VS Code){CLR['END']}    ║
║ {CLR['BOLD']}3. 🛡️  Watchdog: {wd_status}{CLR['END']}                ║
║ {CLR['CYAN']}5. 📥 Restaurar PRO{CLR['END']} | {CLR['RED']}0. ❌ Salir{CLR['END']}        ║
╚══════════════════════════════════════════╝{CLR['END']}
{CLR['YELLOW']}¿Cómo ver y usar las consolas?{CLR['END']}
  1. Dale al botón {CLR['BOLD']}(+){CLR['END']} en tu panel de Terminal (abajo).
  2. Crea una terminal nueva por cada servidor.
  3. Escribe: {CLR['BOLD']}screen -r proxy{CLR['END']} (o lobby / survival).
  4. Para salir de la consola sin apagar: {CLR['BOLD']}Ctrl + A, luego D{CLR['END']}.
""")
        
        opc = input(f"{CLR['CYAN']}➤ Selección: {CLR['END']}")
        if opc == "1": subprocess.run("screen -dmS playit ./playit", shell=True)
        elif opc == "2": start_network_native(); input("\nPresiona Enter...")
        elif opc == "3":
            watchdog_active = not watchdog_active
            if watchdog_active: threading.Thread(target=watchdog_loop, daemon=True).start()
        elif opc == "4": make_backup_final(); input("Enter...")
        elif opc == "5": restore_advanced(); input("Enter...")
        elif opc == "0": break

if __name__ == "__main__":
    setup_tools()
    main_menu()