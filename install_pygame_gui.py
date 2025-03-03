import subprocess
import sys

def install_pygame_gui():
    """
    Script auxiliar para instalar pygame_gui se não estiver presente
    """
    print("Verificando instalação do pygame_gui...")
    try:
        import pygame_gui
        print("pygame_gui já está instalado!")
    except ImportError:
        print("pygame_gui não encontrado. Tentando instalar...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame_gui"])
            print("pygame_gui instalado com sucesso!")
        except Exception as e:
            print(f"Erro ao instalar pygame_gui: {e}")
            print("Por favor, instale manualmente usando: pip install pygame_gui")
            return False
    return True

if __name__ == "__main__":
    # Verifica se pygame está instalado
    try:
        import pygame
        print("pygame já está instalado!")
    except ImportError:
        print("pygame não encontrado. Tentando instalar...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            print("pygame instalado com sucesso!")
        except Exception as e:
            print(f"Erro ao instalar pygame: {e}")
            print("Por favor, instale manualmente usando: pip install pygame")
            sys.exit(1)
    
    # Verifica e instala pygame_gui
    if install_pygame_gui():
        print("Todas as dependências estão instaladas! Você pode executar o simulador com 'python main.py'")
    else:
        print("Falha ao verificar dependências. Por favor, instale manualmente conforme instruções no README.md")
