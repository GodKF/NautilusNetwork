import os
import subprocess
import time
import webbrowser
import threading
import datetime

# --- CONFIGURACIÓN ---
GITHUB_PROFILE = "https://github.com/DasVicgeta"
BASE_DIR = "Network_Master"
BRANCH = "main"

SERVERS = {
    "Proxy": "https://api.papermc.io/v2/projects/velocity/versions/3.3.0-SNAPSHOT/builds/400/downloads/velocity-3.3.0-SNAPSHOT-400.jar",
    "Lobby": "https://api.papermc.io/v2/projects/paper/versions/1.21.1/builds/120/downloads/paper-1.21.1-120.jar",
    "Survival": "https://api.papermc.io/v2/projects/paper/versions/1.21.1/builds/120/downloads/paper-1.21.1-120.jar"
}
PLAYIT_URL = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux-amd64"

CLR = {"CYAN": "\033[96m", "GREEN": "\033[92m", "YELLOW": "\033[93m", "RED": "\033[91m", "BOLD": "\033[1m", "END": "\033[0m"}

watchdog_active = False

def run_command(command, silent=False):
    try:
        if silent:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        else:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            if result.stdout: print(f"{CLR['GREEN']}{result.stdout}{CLR['END']}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"{CLR['RED']}❌ Error en: {command}{CLR['END']}")
        return False

def check_remote():
    """Detecta automáticamente el repo del Codespace o pide uno."""
    result = subprocess.run("git remote", shell=True, capture_output=True, text=True)
    if "origin" not in result.stdout:
        # Intentar obtener el repo del entorno de Codespace
        codespace_repo = os.getenv("GITHUB_REPOSITORY")
        if codespace_repo:
            repo_url = f"https://github.com/{(codespace_repo)}.git"
            print(f"{CLR['YELLOW']}🤖 Codespace detectado. Vinculando a: {repo_url}{CLR['END']}")
            run_command(f"git remote add origin {repo_url}")
        else:
            print(f"\n{CLR['YELLOW']}⚠️ No se detectó repositorio remoto.{CLR['END']}")
            repo_url = input(f"{CLR['CYAN']}➤ Pega la URL de tu repo de GitHub: {CLR['END']}")
            if repo_url.strip():
                run_command(f"git remote add origin {repo_url.strip()}")

def setup_lfs():
    print(f"{CLR['YELLOW']}⚙️ Configurando Git LFS...{CLR['END']}")
    run_command("git lfs install")
    run_command('git lfs track "*.mca" "*.jar" "*.db" "*.zip" "*.exe" "*.dat"')
    run_command("git add .gitattributes")

def make_backup():
    check_remote()
    print(f"\n{CLR['CYAN']}🚀 Iniciando backup en {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...{CLR['END']}")
    
    # Asegurar que estamos en la rama correcta
    run_command(f"git branch -M {BRANCH}", silent=True)
    
    run_command("git add .")
    commit_msg = f"Backup automático: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    # Ejecutamos commit. Si no hay cambios, no fallará el script.
    subprocess.run(f'git commit -m "{commit_msg}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"{CLR['YELLOW']}📤 Subiendo cambios a GitHub...{CLR['END']}")
    if run_command(f"git push origin {BRANCH}"):
        print(f"{CLR['GREEN']}✅ Respaldo exitoso en el repositorio del Codespace.{CLR['END']}")
    else:
        print(f"{CLR['RED']}❌ Falló el envío. Verifica tus permisos de escritura.{CLR['END']}")

def setup_network():
    if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
    os.chdir(BASE_DIR)
    
    # Solo abre el navegador si NO estamos en un Codespace (para no molestar en la terminal)
    if not os.getenv("CODESPACES"):
        webbrowser.open(GITHUB_PROFILE)
    
    print(f"{CLR['CYAN']}📦 Instalando entorno de red...{CLR['END']}")
    run_command("sudo apt update && sudo apt install -y openjdk-17-jdk openjdk-21-jdk wget screen git git-lfs", silent=True)
    
    if not os.path.exists(".git"):
        run_command("git init", silent=True)
        setup_lfs()
        check_remote()

    for name, url in SERVERS.items():
        if not os.path.exists(name):
            os.makedirs(name)
            print(f"📥 Descargando núcleo {name}...")
            run_command(f"wget -O {name}/server.jar {url}", silent=True)
            with open(f"{name}/eula.txt", "w") as f: f.write("eula=true")

    if not os.path.exists("playit"):
        run_command(f"wget -O playit {PLAYIT_URL} && chmod +x playit", silent=True)

def is_running(name):
    result = subprocess.run(f"screen -list | grep {name}", shell=True, capture_output=True, text=True)
    return name in result.stdout

def start_node(name):
    if is_running(name): return
    # Asignación de RAM dinámica (1GB por defecto)
    subprocess.run(f"screen -dmS {name} bash -c 'cd {name} && java -Xmx1G -jar server.jar nogui'", shell=True)

def watchdog_loop():
    while watchdog_active:
        for name in SERVERS.keys():
            if not is_running(name): start_node(name)
        time.sleep(25)

def main_menu():
    global watchdog_active
    if os.path.basename(os.getcwd()) != BASE_DIR:
        if os.path.exists(BASE_DIR): os.chdir(BASE_DIR)

    while True:
        os.system('clear')
        wd_status = f"{CLR['GREEN']}ON{CLR['END']}" if watchdog_active else f"{CLR['RED']}OFF{CLR['END']}"
        print(f"""
{CLR['CYAN']}╔══════════════════════════════════════════╗
║     {CLR['BOLD']}GESTOR DE NETWORK - DasVicgeta{CLR['END']}       {CLR['CYAN']}║
╠══════════════════════════════════════════╣
║ {CLR['YELLOW']}1. ⚡ Playit{CLR['END']}      | {CLR['YELLOW']}4. 💾 Backup (Auto-Repo){CLR['END']}║
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
            make_backup()
            input("\nPresiona Enter...")
        elif opc == "5":
            restore_backup()
            input("\nPresiona Enter...")
        elif opc == "0":
            break

if __name__ == "__main__":
    setup_network()
    main_menu()