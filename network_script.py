import os
import subprocess
import time
import datetime
import json
import threading

# ───────────────────────────────
# CONFIGURACIÓN GENERAL
# ───────────────────────────────
CONFIG_FILE = "config.json"
ROOT_DIR = os.getcwd()
NETWORK_DIR = os.path.join(ROOT_DIR, "my_network")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")

WATCHDOG_INTERVAL = 15  # segundos

CLR = {
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "BOLD": "\033[1m",
    "END": "\033[0m"
}

DEFAULT_CONFIG = {
    "github_profile": "https://github.com/DasVicgeta",
    "branch": "main",
    "idioma": "es",
    "ram": {"proxy": "1G", "lobby": "2G", "survival": "2G"},
    "urls": {
        "proxy": "velocity.jar",
        "lobby": "paper.jar",
        "survival": "paper.jar"
    },
    "playit_url": "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux-amd64"
}

watchdog_active = False

# ───────────────────────────────
# UTILIDADES
# ───────────────────────────────
def run(cmd, silent=True):
    subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.DEVNULL if silent else None,
        stderr=subprocess.DEVNULL if silent else None
    )

def clear():
    os.system("clear")

def pause(msg="Presiona Enter para continuar..."):
    input(f"\n{CLR['CYAN']}{msg}{CLR['END']}")

def header(title):
    clear()
    print(f"""{CLR['CYAN']}
╔══════════════════════════════════════════╗
║ {CLR['BOLD']}{title.center(40)}{CLR['END']}{CLR['CYAN']} ║
╚══════════════════════════════════════════╝{CLR['END']}
""")

# ───────────────────────────────
# PANTALLA DE CARGA
# ───────────────────────────────
def splash_screen():
    clear()
    print(f"{CLR['CYAN']}{CLR['BOLD']}")
    print("Verificando sistema...")
    time.sleep(0.8)
    print("Cargando dependencias...")
    time.sleep(0.8)
    print("Preparando Network...")
    time.sleep(0.8)
    clear()

    print(f"""{CLR['CYAN']}{CLR['BOLD']}
███╗   ██╗███████╗████████╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗
████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝
██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║██║   ██║██████╔╝█████╔╝ 
██║╚██╗██║██╔══╝     ██║   ██║███╗██║██║   ██║██╔══██╗██╔═██╗ 
██║ ╚████║███████╗   ██║   ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗
╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝

                NetworkSystem
{CLR['END']}""")
    time.sleep(1.5)

# ───────────────────────────────
# CONFIG
# ───────────────────────────────
def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return DEFAULT_CONFIG.copy()

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

config = load_config()

# ───────────────────────────────
# SETUP
# ───────────────────────────────
def setup_tools():
    header("INICIALIZANDO SISTEMA")
    print("• Instalando Java (JDK 8, 11, 17, 21)...")

    run(
        "sudo apt-get update -y && "
        "sudo apt-get install -y screen wget git git-lfs "
        "openjdk-8-jdk openjdk-11-jdk openjdk-17-jdk openjdk-21-jdk"
    )

    os.makedirs(NETWORK_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    print(f"{CLR['GREEN']}✓ Todos los JDK instalados correctamente{CLR['END']}")
    time.sleep(1)

def is_running(name):
    result = subprocess.run(
        ["screen", "-list"],
        capture_output=True,
        text=True
    )
    return name in result.stdout

# ───────────────────────────────
# NETWORK
# ───────────────────────────────
def start_single_server(name):
    if is_running(name):
        return

    path = os.path.join(NETWORK_DIR, name)
    os.makedirs(path, exist_ok=True)

    jar_path = os.path.join(path, "server.jar")
    if not os.path.exists(jar_path):
        print(f"{CLR['RED']}✗ server.jar no encontrado en {path}{CLR['END']}")
        return

    # Selección de Java
    if name == "lobby":
        java_bin = "/usr/lib/jvm/java-8-openjdk-amd64/bin/java"
        java_flags = ""   # ❗ Paper 1.8 NO flags
    elif name == "proxy":
        java_bin = "/usr/lib/jvm/java-17-openjdk-amd64/bin/java"
        ram = config["ram"].get(name, "1G")
        java_flags = f"-Xms{ram} -Xmx{ram}"
    else:
        java_bin = "/usr/lib/jvm/java-17-openjdk-amd64/bin/java"
        ram = config["ram"].get(name, "2G")
        java_flags = f"-Xms{ram} -Xmx{ram}"

    cmd = (
        f"cd '{path}' && "
        f"'{java_bin}' {java_flags} -jar server.jar"
    )

    run(f"screen -dmS {name} bash -lc \"{cmd}\"", silent=False)


def start_network_native():
    header("INICIO DE SERVIDORES")

    servers = list(config["urls"].keys())
    print(f"{CLR['CYAN']}Servidores disponibles:{CLR['END']}")
    print("  - " + "\n  - ".join(servers))

    seleccion = input(
        f"\n{CLR['BOLD']}➤ Selecciona (coma) o Enter para TODOS:{CLR['END']} "
    ).lower().strip()

    targets = servers if not seleccion else [
        s for s in map(str.strip, seleccion.split(",")) if s in servers
    ]

    if not targets:
        print(f"\n{CLR['RED']}✗ Selección inválida{CLR['END']}")
        pause()
        return

    for name in targets:
        if is_running(name):
            print(f"{CLR['YELLOW']}⚠ {name} ya está activo{CLR['END']}")
            continue

        start_single_server(name)
        print(f"{CLR['GREEN']}✓ {name} iniciado{CLR['END']}")
        time.sleep(0.7)

    pause()

# ───────────────────────────────
# WATCHDOG
# ───────────────────────────────
def watchdog_loop():
    global watchdog_active
    while True:
        if watchdog_active:
            for server in config["urls"].keys():
                if not is_running(server):
                    print(
                        f"{CLR['YELLOW']}[WATCHDOG]{CLR['END']} "
                        f"{server} caído → reiniciando"
                    )
                    start_single_server(server)
        time.sleep(WATCHDOG_INTERVAL)

# ───────────────────────────────
# SISTEMA
# ───────────────────────────────
def kill_all_processes():
    header("CIERRE DEL SISTEMA")
    print("• Cerrando sesiones screen...")

    for name in list(config["urls"].keys()) + ["playit"]:
        if is_running(name):
            run(f"screen -S {name} -X quit", silent=False)

    run("screen -wipe")
    print(f"{CLR['GREEN']}✓ Todo detenido correctamente{CLR['END']}")
    pause()

def make_backup_final():
    header("BACKUP TOTAL")
    print("• Preparando backup...")
    os.chdir(ROOT_DIR)
    run("git add .")
    msg = f"Backup {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
    run(f'git commit -m "{msg}"')
    run(f"git push origin {config['branch']}")
    print(f"{CLR['GREEN']}✓ Backup enviado a GitHub{CLR['END']}")
    pause()

# ───────────────────────────────
# MENÚ PRINCIPAL
# ───────────────────────────────
def main_menu():
    global watchdog_active

    while True:
        header("GESTOR DE NETWORK")
        wd = f"{CLR['GREEN']}ON{CLR['END']}" if watchdog_active else f"{CLR['RED']}OFF{CLR['END']}"

        print(f"""
1) ⚡ Playit
2) 🎮 Iniciar Network
3) 🛡 Watchdog      [{wd}]
4) 💾 Backup Total
5) ⚙ Ajustes
6) 🛑 Cerrar Todo

0) ❌ Salir
""")

        opc = input("➤ ")

        if opc == "1" and not is_running("playit"):
            run("screen -dmS playit ./playit", silent=False)
        elif opc == "2":
            start_network_native()
        elif opc == "3":
            watchdog_active = not watchdog_active
        elif opc == "4":
            make_backup_final()
        elif opc == "5":
            settings_menu()
        elif opc == "6":
            kill_all_processes()
        elif opc == "0":
            clear()
            break

# ───────────────────────────────
# MAIN
# ───────────────────────────────
if __name__ == "__main__":
    splash_screen()
    setup_tools()

    watchdog_thread = threading.Thread(
        target=watchdog_loop,
        daemon=True
    )
    watchdog_thread.start()

    main_menu()
