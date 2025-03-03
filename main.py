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
        
        # Configuração da tela
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Simulador de Seleção Natural Avançado")
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
            
            # Processar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if mostrar_menu:
                    # O menu processa o evento e retorna True se o usuário iniciou a simulação
                    if menu.processar_eventos(event):
                        # Obter configurações do menu e inicializar simulação
                        configuracoes = menu.obter_configuracoes()
                        simulacao.inicializar(configuracoes)
                        mostrar_menu = False
                else:
                    # A simulação processa seus próprios eventos
                    simulacao.processar_eventos(event)
                    
                    # Checar tecla de escape para voltar ao menu
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        mostrar_menu = True
            
            # Atualizar
            if mostrar_menu:
                menu.atualizar(dt)
            else:
                simulacao.atualizar()
            
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
        # Catch any exceptions and print a more helpful error message
        print(f"Erro durante a execução: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()