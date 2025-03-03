import pygame
import sys
from menu import Menu
from simulacao import Simulacao

# Constantes
WIDTH, HEIGHT = 1024, 768  # Janela maior para acomodar terrenos mais complexos
FPS = 60

def main():
    try:
        # Inicialização do Pygame
        pygame.init()
        
        # Configuração para dispositivos móveis
        if hasattr(pygame, 'FINGERUP'):
            # Estamos em um dispositivo móvel
            flags = pygame.FULLSCREEN | pygame.RESIZABLE
        else:
            # Desktop
            flags = pygame.RESIZABLE
            
        # Configuração da tela
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        pygame.display.set_caption("Simulador de Seleção Natural")
        clock = pygame.time.Clock()
        
        # Criar menu e simulação
        menu = Menu(WIDTH, HEIGHT)
        simulacao = Simulacao(WIDTH, HEIGHT)
        
        # Estado inicial: mostrar menu
        mostrar_menu = True
        
        running = True
        while running:
            # Tempo decorrido desde o último frame (para animações suaves)
            dt = clock.tick(FPS) / 1000.0  # Converte para segundos
            
            # Posição atual do mouse ou último toque
            current_pos = pygame.mouse.get_pos()
            
            # Processar eventos
            for event in pygame.event.get():
                # Tratamento para evento de saída
                if event.type == pygame.QUIT:
                    running = False
                
                # Traduzir eventos de toque para eventos de mouse em dispositivos móveis
                if hasattr(pygame, 'FINGERDOWN') and event.type == pygame.FINGERDOWN:
                    # Converter posição de toque (0-1) para coordenadas da tela
                    x = event.x * WIDTH
                    y = event.y * HEIGHT
                    # Criar evento de mouse a partir do toque
                    mouse_event = pygame.event.Event(
                        pygame.MOUSEBUTTONDOWN,
                        {'pos': (x, y), 'button': 1}
                    )
                    if mostrar_menu:
                        menu.processar_eventos(mouse_event)
                    else:
                        simulacao.processar_eventos(mouse_event)
                    continue
                    
                # Processamento normal de eventos
                if mostrar_menu:
                    # O menu processa o evento e retorna True se o usuário iniciou a simulação
                    if menu.processar_eventos(event):
                        # Obter configurações do menu e inicializar simulação
                        configuracoes = menu.obter_configuracoes()
                        simulacao.inicializar(configuracoes)
                        mostrar_menu = False
                else:
                    # A simulação processa seus próprios eventos
                    resultado = simulacao.processar_eventos(event)
                    
                    # Checar se o usuário quer voltar ao menu
                    if resultado == "voltar_menu":
                        mostrar_menu = True
            
            # Atualizar
            if mostrar_menu:
                menu.atualizar(dt)
            else:
                # Passar posição do mouse para atualização dos controles de toque
                simulacao.atualizar(dt, current_pos)
            
            # Desenhar
            if mostrar_menu:
                menu.desenhar(screen)
            else:
                simulacao.desenhar(screen)
            
            # Atualizar tela
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
        
    except Exception as e:
        # Captura qualquer exceção e imprime uma mensagem de erro mais útil
        print(f"Erro durante a execução: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()