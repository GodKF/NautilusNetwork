import os
import subprocess
import time
import datetime
import json

# ───────────────────────────────
# CONFIGURACIÓN GENERAL
# ───────────────────────────────
CONFIG_FILE = "config.json"
ROOT_DIR = os.getcwd()
NETWORK_DIR = os.path.join(ROOT_DIR, "my_network")

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
    print("• Verificando dependencias...")
    run(
        "sudo apt-get update -y && "
        "sudo apt-get install -y screen openjdk-17-jdk openjdk-21-jdk wget git git-lfs"
    )
    os.makedirs(NETWORK_DIR, exist_ok=True)
    print(f"{CLR['GREEN']}✓ Sistema listo{CLR['END']}")
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

        path = os.path.join(NETWORK_DIR, name)
        os.makedirs(path, exist_ok=True)

        ram = config["ram"].get(name, "1G")
        cmd = f"cd {path} && java -Xms{ram} -Xmx{ram} -jar server.jar nogui"

        run(f"screen -dmS {name} bash -c '{cmd}'", silent=False)
        print(f"{CLR['GREEN']}✓ {name} iniciado ({ram}){CLR['END']}")
        time.sleep(0.7)

    pause()

# ───────────────────────────────
# SISTEMA
# ───────────────────────────────
def kill_all_processes():
    header("CIERRE DEL SISTEMA")
    print("• Deteniendo servicios...")
    run("pkill -f java")
    run("pkill playit")
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
# AJUSTES
# ───────────────────────────────
def settings_menu():
    while True:
        header("CONFIGURACIÓN")
        print(f"""
1) RAM Proxy     [{config['ram']['proxy']}]
2) RAM Lobby     [{config['ram']['lobby']}]
3) RAM Survival  [{config['ram']['survival']}]
4) Rama Git      [{config['branch']}]

0) Volver
""")
        opc = input("➤ ")

        if opc == "1": config["ram"]["proxy"] = input("Nueva RAM Proxy: ")
        elif opc == "2": config["ram"]["lobby"] = input("Nueva RAM Lobby: ")
        elif opc == "3": config["ram"]["survival"] = input("Nueva RAM Survival: ")
        elif opc == "4": config["branch"] = input("Nueva rama: ")
        elif opc == "0": break

        save_config(config)

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
    setup_tools()
    main_menu()
