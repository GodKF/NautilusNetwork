import os
import subprocess
import time
import webbrowser
import threading
import datetime

# --- CONFIGURACIÓN ---
GITHUB_PROFILE = "https://github.com/DasVicgeta"
BASE_DIR = os.getcwd() # Usaremos el directorio actual para evitar conflictos de rutas
BRANCH = "main"

SERVERS = {
    "Proxy": "https://api.papermc.io/v2/projects/velocity/versions/3.3.0-SNAPSHOT/builds/400/downloads/velocity-3.3.0-SNAPSHOT-400.jar",
    "Lobby": "https://api.papermc.io/v2/projects/paper/versions/1.21.1/builds/120/downloads/paper-1.21.1-120.jar",
    "Survival": "https://api.papermc.io/v2/projects/paper/versions/1.21.1/builds/120/downloads/paper-1.21.1-120.jar"
}
PLAYIT_URL = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux-amd64"

CLR = {"CYAN": "\033[96m", "GREEN": "\033[92m", "YELLOW": "\033[93m", "RED": "\033[91m", "BOLD": "\033[1m", "END": "\033[0m"}

watchdog_active = False

def run_command_direct(command):
    """Lógica exacta de tu backup_manager que sí funciona."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        if result.stdout: print(f"{CLR['GREEN']}{result.stdout}{CLR['END']}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{CLR['RED']}❌ Error: {e.stderr}{CLR['END']}")
        return False

def check_remote_codespace():
    """Detecta el repo del codespace automáticamente."""
    result = subprocess.run("git remote", shell=True, capture_output=True, text=True)
    if "origin" not in result.stdout:
        repo_env = os.getenv("GITHUB_REPOSITORY")
        if repo_env:
            url = f"https://github.com/{repo_env}.git"
            print(f"{CLR['YELLOW']}🤖 Vinculando Codespace: {url}{CLR['END']}")
            run_command_direct(f"git remote add origin {url}")
        else:
            print(f"{CLR['RED']}⚠️ No hay origin. Usa 'git remote add origin URL'{CLR['END']}")

def setup_lfs_direct():
    print(f"{CLR['YELLOW']}⚙️ Configurando Git LFS...{CLR['END']}")
    run_command_direct("git lfs install")
    run_command_direct('git lfs track "*.mca" "*.jar" "*.db" "*.zip" "*.exe" "*.dat"')
    run_command_direct("git add .gitattributes")
    print(f"{CLR['GREEN']}✅ LFS configurado.{CLR['END']}")

def make_backup_final():
    """Copia exacta de la lógica que te funciona."""
    check_remote_codespace()
    print(f"\n{CLR['CYAN']}🚀 Iniciando backup en {datetime.datetime.now()}...{CLR['END']}")
    
    # 1. Añadir archivos
    if run_command_direct("git add ."):
        # 2. Commit
        msg = f"Backup automático: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(f'git commit -m "{msg}"', shell=True)
        
        # 3. Push (Aquí es donde fallaba)
        print(f"{CLR['YELLOW']}📤 Subiendo a GitHub...{CLR['END']}")
        if run_command_direct(f"git push origin {BRANCH}"):
            print(f"{CLR['GREEN']}✅ Backup completado con éxito.{CLR['END']}")
        else:
            print(f"{CLR['RED']}❌ Error en el Push. Revisa permisos.{CLR['END']}")

def setup_network():
    # Instalar dependencias primero
    print(f"{CLR['CYAN']}📦 Instalando Java y herramientas...{CLR['END']}")
    subprocess.run("sudo apt update && sudo apt install -y openjdk-17-jdk openjdk-21-jdk wget screen git git-lfs", shell=True, stdout=subprocess.DEVNULL)
    
    if not os.path.exists(".git"):
        run_command_direct("git init")
        setup_lfs_direct()
    
    for name, url in SERVERS.items():
        if not os.path.exists(name):
            os.makedirs(name)
            print(f"📥 Descargando {name}...")
            subprocess.run(f"wget -O {name}/server.jar {url}", shell=True, stdout=subprocess.DEVNULL)
            with open(f"{name}/eula.txt", "w") as f: f.write("eula=true")

    if not os.path.exists("playit"):
        subprocess.run(f"wget -O playit {PLAYIT_URL} && chmod +x playit", shell=True, stdout=subprocess.DEVNULL)

def is_running(name):
    result = subprocess.run(f"screen -list | grep {name}", shell=True, capture_output=True, text=True)
    return name in result.stdout

def start_node(name):
    if is_running(name): return
    # Abrir en screen
    subprocess.run(f"screen -dmS {name} bash -c 'cd {name} && java -Xmx1G -jar server.jar nogui'", shell=True)

def watchdog_loop():
    while watchdog_active:
        for name in SERVERS.keys():
            if not is_running(name): start_node(name)
        time.sleep(20)

def main_menu():
    global watchdog_active
    while True:
        os.system('clear')
        wd_status = f"{CLR['GREEN']}ON{CLR['END']}" if watchdog_active else f"{CLR['RED']}OFF{CLR['END']}"
        print(f"""
{CLR['CYAN']}╔══════════════════════════════════════════╗
║     {CLR['BOLD']}GESTOR DE NETWORK - DasVicgeta{CLR['END']}       {CLR['CYAN']}║
╠══════════════════════════════════════════╣
║ {CLR['YELLOW']}1. ⚡ Playit{CLR['END']}      | {CLR['YELLOW']}4. 💾 Backup (LFS){CLR['END']}  ║
║ {CLR['GREEN']}2. 🎮 Iniciar Red{CLR['END']} | {CLR['GREEN']}5. 📥 Restaurar{CLR['END']}     ║
║ {CLR['BOLD']}3. 🛡️  Watchdog: {wd_status}{CLR['END']}                ║
║ {CLR['RED']}0. ❌ Salir{CLR['END']}                            ║
╚══════════════════════════════════════════╝{CLR['END']}""")
        
        opc = input(f"{CLR['CYAN']}➤ Selección: {CLR['END']}")

        if opc == "1":
            subprocess.run("screen -dmS playit ./playit", shell=True)
        elif opc == "2":
            for s in SERVERS.keys(): start_node(s)
        elif opc == "3":
            watchdog_active = not watchdog_active
            if watchdog_active: threading.Thread(target=watchdog_loop, daemon=True).start()
        elif opc == "4":
            make_backup_final()
            input("\nPresiona Enter...")
        elif opc == "5":
            run_command_direct("git fetch origin && git reset --hard origin/main && git lfs pull")
            input("\nPresiona Enter...")
        elif opc == "0":
            break

if __name__ == "__main__":
    setup_network()
    main_menu()