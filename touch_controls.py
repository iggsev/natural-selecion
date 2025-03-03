import pygame

class TouchControls:
    """Sistema de controles para dispositivos sensíveis ao toque."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Definições de botões
        button_height = 60
        button_margin = 10
        
        # Botões principais
        self.buttons = {
            'menu': {
                'rect': pygame.Rect(10, height - button_height - button_margin, 180, button_height),
                'text': 'Voltar ao Menu',
                'color': (50, 50, 80),
                'hover_color': (70, 70, 100),
                'action': 'menu'
            },
            'pause': {
                'rect': pygame.Rect(200, height - button_height - button_margin, 120, button_height),
                'text': 'Pausar',
                'alt_text': 'Continuar',
                'color': (50, 80, 50),
                'hover_color': (70, 100, 70),
                'action': 'pause',
                'toggled': False
            },
            'editor': {
                'rect': pygame.Rect(330, height - button_height - button_margin, 120, button_height),
                'text': 'Editor',
                'color': (80, 50, 50),
                'hover_color': (100, 70, 70),
                'action': 'editor',
                'toggled': False
            },
            'speed_down': {
                'rect': pygame.Rect(460, height - button_height - button_margin, 60, button_height),
                'text': '-',
                'color': (50, 50, 50),
                'hover_color': (70, 70, 70),
                'action': 'speed_down'
            },
            'speed_up': {
                'rect': pygame.Rect(530, height - button_height - button_margin, 60, button_height),
                'text': '+',
                'color': (50, 50, 50),
                'hover_color': (70, 70, 70),
                'action': 'speed_up'
            },
            'add_food': {
                'rect': pygame.Rect(600, height - button_height - button_margin, 180, button_height),
                'text': 'Adicionar Alimento',
                'color': (80, 80, 50),
                'hover_color': (100, 100, 70),
                'action': 'add_food'
            }
        }
        
        # Fonte para os botões
        self.font = pygame.font.SysFont("Arial", 24)
        
        # Estado de hover e clique
        self.hovered_button = None
        
    def update(self, mouse_pos):
        """Atualiza o estado dos botões baseado na posição do mouse."""
        self.hovered_button = None
        for button_key, button in self.buttons.items():
            if button['rect'].collidepoint(mouse_pos):
                self.hovered_button = button_key
                break
    
    def handle_event(self, event, simulation):
        """Processa eventos de toque/clique nos botões."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clique esquerdo
            if self.hovered_button:
                button = self.buttons[self.hovered_button]
                action = button['action']
                
                # Executar ação correspondente
                if action == 'menu':
                    return 'voltar_menu'
                elif action == 'pause':
                    simulation.pausa = not simulation.pausa
                    button['toggled'] = simulation.pausa
                    button['text'] = 'Continuar' if simulation.pausa else 'Pausar'
                elif action == 'editor':
                    if simulation.editor:
                        simulation.editor.toggle_editor()
                        button['toggled'] = simulation.editor.ativo
                elif action == 'speed_down':
                    simulation.aceleracao = max(1, simulation.aceleracao - 1)
                elif action == 'speed_up':
                    simulation.aceleracao = min(10, simulation.aceleracao + 1)
                elif action == 'add_food':
                    alimento = simulation._criar_alimento_em_posicao_valida()
                    if alimento:
                        simulation.alimentos.append(alimento)
        
        return None
    
    def draw(self, surface):
        """Desenha todos os botões na superfície."""
        for button_key, button in self.buttons.items():
            # Determinar cor (normal ou hover)
            color = button['hover_color'] if self.hovered_button == button_key else button['color']
            
            # Cor especial para botões alternados
            if 'toggled' in button and button['toggled']:
                # Fazer botão mais brilhante quando ativado
                r, g, b = color
                color = (min(255, r + 30), min(255, g + 30), min(255, b + 30))
            
            # Desenhar fundo do botão com cantos arredondados
            pygame.draw.rect(surface, color, button['rect'], 0, 15)
            
            # Desenhar borda
            pygame.draw.rect(surface, (255, 255, 255), button['rect'], 2, 15)
            
            # Desenhar texto
            text = button['text']
            if 'toggled' in button and button['toggled'] and 'alt_text' in button:
                text = button['alt_text']
                
            text_surf = self.font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=button['rect'].center)
            surface.blit(text_surf, text_rect)