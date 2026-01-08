import os
import subprocess
import datetime

# --- CONFIGURACIÓN ---
REPO_PATH = os.getcwd()  # La carpeta actual donde está tu servidor
BRANCH = "main"          # Tu rama principal

def run_command(command):
    """Ejecuta comandos de consola y muestra la salida."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar: {command}")
        print(e.stderr)

def setup_lfs():
    """Configura Git LFS para archivos pesados de Minecraft."""
    print("⚙️ Configurando Git LFS...")
    run_command("git lfs install")
    # Rastreamos archivos comunes pesados de Minecraft
    run_command('git lfs track "*.mca" "*.jar" "*.db" "*.zip" "*.exe"')
    run_command("git add .gitattributes")
    print("✅ Git LFS configurado.")

def make_backup():
    """Sube todos los cambios al repositorio de GitHub."""
    print(f"🚀 Iniciando backup en {datetime.datetime.now()}...")
    
    # 1. Añadir todos los archivos
    run_command("git add .")
    
    # 2. Crear commit con fecha
    commit_msg = f"Backup automático: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run_command(f'git commit -m "{commit_msg}"')
    
    # 3. Subir a GitHub
    print("📤 Subiendo archivos a GitHub (esto puede tardar según el tamaño del mapa)...")
    run_command(f"git push origin {BRANCH}")
    print("✅ Backup completado con éxito.")

def restore_backup():
    """Descarga la última versión del repositorio (Sobrescribe local)."""
    confirm = input("⚠️ Esto sobrescribirá tus archivos locales con lo que hay en GitHub. ¿Continuar? (s/n): ")
    if confirm.lower() != 's':
        return

    print("📥 Descargando respaldo desde GitHub...")
    run_command("git fetch origin")
    run_command(f"git reset --hard origin/{BRANCH}")
    run_command("git lfs pull") # Asegura que los archivos pesados se descarguen
    print("✅ Servidor restaurado a la última versión de la nube.")

if __name__ == "__main__":
    print("--- Administrador de Respaldo Minecraft ---")
    print("1. Hacer Backup (Subir)")
    print("2. Restaurar Respaldo (Bajar)")
    print("3. Configurar Git LFS (Solo la primera vez)")
    
    opcion = input("Selecciona una opción: ")
    
    if opcion == "1":
        make_backup()
    elif opcion == "2":
        restore_backup()
    elif opcion == "3":
        setup_lfs()
    else:
        print("Opción no válida.")