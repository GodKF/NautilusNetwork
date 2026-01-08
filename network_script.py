import os
import subprocess
import time
import webbrowser
import threading
import sys

# --- CONFIGURACIÓN ---
GITHUB_PROFILE = "https://github.com/DasVicgeta"
BASE_DIR = "Network_Master"
# URLs actualizadas a versiones estables
SERVERS = {
    "Proxy": "https://api.papermc.io/v2/projects/velocity/versions/3.3.0-SNAPSHOT/builds/400/downloads/velocity-3.3.0-SNAPSHOT-400.jar",
    "Lobby": "https://api.papermc.io/v2/projects/paper/versions/1.21.1/builds/120/downloads/paper-1.21.1-120.jar",
    "Survival": "https://api.papermc.io/v2/projects/paper/versions/1.21.1/builds/120/downloads/paper-1.21.1-120.jar"
}
PLAYIT_URL = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux-amd64"

# --- COLORES ANSI ---
CLR = {
    "HEADER": "\033[95m", "BLUE": "\033[94m", "CYAN": "\033[96m",
    "GREEN": "\033[92m", "YELLOW": "\033[93m", "RED": "\033[91m",
    "BOLD": "\033[1m", "END": "\033[0m"
}

watchdog_active = False

def run_silent(cmd):
    """Ejecuta comandos ocultando la salida técnica."""
    return subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def setup_network():
    print(f"\n{CLR['HEADER']}🚀 INICIANDO INSTALACIÓN PROFESIONAL{CLR['END']}")
    if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
    os.chdir(BASE_DIR)

    # Validación Visual
    print(f"{CLR['CYAN']}📢 Abriendo perfil de {CLR['BOLD']}DasVicgeta{CLR['END']}...")
    webbrowser.open(GITHUB_PROFILE)
    
    # Instalación de Dependencias
    print(f"{CLR['YELLOW']}📦 Instalando Java 17, 21 y herramientas de sistema...{CLR['END']}", end="", flush=True)
    run_silent("sudo apt update && sudo apt install -y openjdk-17-jdk openjdk-21-jdk wget screen git git-lfs")
    print(f" {CLR['GREEN']}[LISTO]{CLR['END']}")

    # Git & LFS
    print(f"{CLR['YELLOW']}⚙️ Configurando repositorio y Git LFS...{CLR['END']}", end="", flush=True)
    run_silent("git init && git lfs install")
    run_silent('git lfs track "*.mca" "*.jar" "*.db" "*.dat"')
    print(f" {CLR['GREEN']}[LISTO]{CLR['END']}")
    
    # Descarga de Servidores
    for name, url in SERVERS.items():
        if not os.path.exists(name):
            os.makedirs(name)
            print(f"{CLR['CYAN']}📥 Descargando núcleo para {CLR['BOLD']}{name}{CLR['END']}...", end="", flush=True)
            run_silent(f"wget -O {name}/server.jar {url}")
            with open(f"{name}/eula.txt", "w") as f: f.write("eula=true")
            print(f" {CLR['GREEN']}[OK]{CLR['END']}")

    # Playit
    if not os.path.exists("playit"):
        print(f"{CLR['CYAN']}🌐 Preparando puente Playit.gg...{CLR['END']}", end="", flush=True)
        run_silent(f"wget -O playit {PLAYIT_URL} && chmod +x playit")
        print(f" {CLR['GREEN']}[OK]{CLR['END']}")

def is_running(name):
    result = subprocess.run(f"screen -list | grep {name}", shell=True, capture_output=True, text=True)
    return name in result.stdout

def start_node(name):
    if is_running(name): return
    # El Proxy suele requerir Java 17, el resto 21. El sistema usará el default del sistema o puedes especificar rutas.
    run_silent(f"screen -dmS {name} bash -c 'cd {name} && java -Xmx1G -jar server.jar nogui'")

def watchdog_loop():
    global watchdog_active
    while watchdog_active:
        for name in SERVERS.keys():
            if not is_running(name):
                start_node(name)
        time.sleep(20)

def backup_process():
    print(f"\n{CLR['YELLOW']}💾 Sincronizando con GitHub...{CLR['END']}")
    run_silent("git add .")
    msg = f"Backup_{time.strftime('%Y%m%d_%H%M')}"
    run_silent(f'git commit -m "{msg}"')
    process = subprocess.Popen("git push origin main", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    print(f"{CLR['GREEN']}✅ Respaldo completado en la nube.{CLR['END']}")

def main_menu():
    global watchdog_active
    # Asegurar posición en carpeta madre
    if os.path.basename(os.getcwd()) != BASE_DIR:
        if os.path.exists(BASE_DIR): os.chdir(BASE_DIR)

    while True:
        os.system('clear')
        wd_status = f"{CLR['GREEN']}ACTIVO{CLR['END']}" if watchdog_active else f"{CLR['RED']}INACTIVO{CLR['END']}"
        
        print(f"""
{CLR['BLUE']}╔════════════════════════════════════════════╗
║{CLR['END']}       {CLR['BOLD']}{CLR['CYAN']}NETWORK MASTER CONTROL{CLR['END']}          {CLR['BLUE']}║
╠════════════════════════════════════════════╣
{CLR['BLUE']}║{CLR['END']}  1. {CLR['YELLOW']}⚡ Iniciar Playit (Túnel){CLR['END']}           {CLR['BLUE']}║
{CLR['BLUE']}║{CLR['END']}  2. {CLR['GREEN']}🎮 Encender Network Completa{CLR['END']}        {CLR['BLUE']}║
{CLR['BLUE']}║{CLR['END']}  3. {CLR['BLUE']}🛡️  Auto-Reinicio: {wd_status}            {CLR['BLUE']}║
{CLR['BLUE']}║{CLR['END']}  4. {CLR['HEADER']}📂 Backup Manual a GitHub{CLR['END']}           {CLR['BLUE']}║
{CLR['BLUE']}║{CLR['END']}  5. {CLR['CYAN']}📥 Restaurar / Actualizar Datos{CLR['END']}     {CLR['BLUE']}║
{CLR['BLUE']}║{CLR['END']}  0. {CLR['RED']}❌ Salir{CLR['END']}                           {CLR['BLUE']}║
{CLR['BLUE']}╚════════════════════════════════════════════╝{CLR['END']}
        """)
        
        opc = input(f"{CLR['BOLD']}➤ Selección:{CLR['END']} ")

        if opc == "1":
            run_silent("screen -dmS playit ./playit")
            print(f"{CLR['GREEN']}✔ Playit iniciado.{CLR['END']}")
            time.sleep(1)
        elif opc == "2":
            print(f"{CLR['YELLOW']}⏳ Encendiendo servidores...{CLR['END']}")
            for s in SERVERS.keys(): start_node(s)
            time.sleep(2)
        elif opc == "3":
            watchdog_active = not watchdog_active
            if watchdog_active:
                threading.Thread(target=watchdog_loop, daemon=True).start()
        elif opc == "4":
            backup_process()
            time.sleep(2)
        elif opc == "5":
            print(f"{CLR['YELLOW']}📥 Descargando cambios...{CLR['END']}")
            run_silent("git pull origin main && git lfs pull")
            print(f"{CLR['GREEN']}✔ Sincronizado.{CLR['END']}")
            time.sleep(2)
        elif opc == "0":
            break

if __name__ == "__main__":
    if not os.path.exists(BASE_DIR):
        setup_network()
    main_menu()