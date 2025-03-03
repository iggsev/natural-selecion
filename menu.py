import pygame
import pygame_gui

class Menu:
    """Classe que gerencia o menu de configuração do simulador"""
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        
        # Configurações padrão
        self.configuracoes = {
            'mapa': 'aleatorio',
            'n_presas': 20,
            'n_predadores': 3,
            'n_canibais': 1,
            'n_alimentos': 40,
            'taxa_alimento': 0.05,  # Novas unidades de comida por segundo
            'modo_atributos': 'aleatorio',  # 'padrao' ou 'aleatorio'
            
            # Porcentagens de terrenos (total deve ser 100%)
            'terrenos': {
                'grama': 40,
                'agua': 20,
                'lama': 10,
                'gelo': 5,
                'deserto': 10,
                'montanha': 5,
                'floresta': 5,
                'pantano': 5
            }
        }
        
        # Tipos de mapa disponíveis
        self.tipos_mapa = [
            'aleatorio',
            'planicie',
            'ilha',
            'labirinto',
            'montanhoso',
            'diversificado',
            'personalizado'  # Novo tipo para usar porcentagens personalizadas
        ]
        
        # Modos de atributos
        self.modos_atributos = [
            'aleatorio',  # Atributos totalmente aleatórios
            'padrao'      # Atributos com valores padrão
        ]
        
        # Estado
        self.ativo = True
        self.iniciou_simulacao = False
        
        # Controles para os percentuais de terreno
        self.sliders_terreno = {}
        self.labels_valor_terreno = {}
        
        # Aba atual
        self.aba_atual = 'geral'  # 'geral' ou 'terrenos'

        # Inicializa a UI
        self.gerenciador = pygame_gui.UIManager((largura, altura))
        self.inicializar_elementos_ui()
        
    
    def inicializar_elementos_ui(self):
        """Cria os elementos da interface de usuário do menu"""
        # Painel principal
        panel_width = 600
        panel_height = 500
        panel_x = (self.largura - panel_width) // 2
        panel_y = (self.altura - panel_height) // 2
        
        self.painel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((panel_x, panel_y), (panel_width, panel_height)),
            manager=self.gerenciador
        )
        
        # Título
        self.titulo = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 10), (panel_width, 40)),
            text="Simulador de Seleção Natural",
            manager=self.gerenciador,
            container=self.painel
        )
        
        # Abas
        self.botao_aba_geral = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((panel_width // 4 - 75, 60), (150, 30)),
            text="Configurações Gerais",
            manager=self.gerenciador,
            container=self.painel
        )
        
        self.botao_aba_terrenos = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((panel_width * 3 // 4 - 75, 60), (150, 30)),
            text="Configurações de Terreno",
            manager=self.gerenciador,
            container=self.painel
        )
        
        # Painéis para cada aba
        self.painel_geral = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((25, 100), (panel_width - 50, 320)),
            manager=self.gerenciador,
            container=self.painel
        )
        
        self.painel_terrenos = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((25, 100), (panel_width - 50, 320)),
            manager=self.gerenciador,
            container=self.painel
        )
        self.painel_terrenos.hide()  # Começa escondido
        
        # Inicializa elementos da aba geral
        self._inicializar_aba_geral()
        
        # Inicializa elementos da aba de terrenos
        self._inicializar_aba_terrenos()
        
        # Botão iniciar (fora das abas)
        self.botao_iniciar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((panel_width//2 - 50, 440), (100, 40)),
            text="Iniciar",
            manager=self.gerenciador,
            container=self.painel
        )
    
    def _inicializar_aba_geral(self):
        """Inicializa os elementos da aba de configurações gerais"""
        panel_width = self.painel_geral.rect.width
        
        # Seleção de mapa
        self.label_mapa = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 10), (150, 30)),
            text="Tipo de Mapa:",
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.dropdown_mapa = pygame_gui.elements.UIDropDownMenu(
            options_list=self.tipos_mapa,
            starting_option=self.configuracoes['mapa'],
            relative_rect=pygame.Rect((180, 10), (200, 30)),
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        # Modo de atributos
        self.label_modo_atributos = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 50), (150, 30)),
            text="Modo de Atributos:",
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.dropdown_modo_atributos = pygame_gui.elements.UIDropDownMenu(
            options_list=self.modos_atributos,
            starting_option=self.configuracoes['modo_atributos'],
            relative_rect=pygame.Rect((180, 50), (200, 30)),
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        # Sliders para números de criaturas e alimentos
        elementos_y = 90
        espacamento_y = 40
        
        # Presas
        self.label_presas = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, elementos_y), (150, 30)),
            text="Presas:",
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.slider_presas = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((180, elementos_y), (200, 30)),
            start_value=self.configuracoes['n_presas'],
            value_range=(0, 200),
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.label_valor_presas = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((390, elementos_y), (50, 30)),
            text=str(self.configuracoes['n_presas']),
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        elementos_y += espacamento_y
        
        # Predadores
        self.label_predadores = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, elementos_y), (150, 30)),
            text="Predadores:",
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.slider_predadores = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((180, elementos_y), (200, 30)),
            start_value=self.configuracoes['n_predadores'],
            value_range=(0, 50),
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.label_valor_predadores = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((390, elementos_y), (50, 30)),
            text=str(self.configuracoes['n_predadores']),
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        elementos_y += espacamento_y
        
        # Canibais
        self.label_canibais = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, elementos_y), (150, 30)),
            text="Canibais:",
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.slider_canibais = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((180, elementos_y), (200, 30)),
            start_value=self.configuracoes['n_canibais'],
            value_range=(0, 30),
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.label_valor_canibais = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((390, elementos_y), (50, 30)),
            text=str(self.configuracoes['n_canibais']),
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        elementos_y += espacamento_y
        
        # Alimentos
        self.label_alimentos = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, elementos_y), (150, 30)),
            text="Alimentos:",
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.slider_alimentos = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((180, elementos_y), (200, 30)),
            start_value=self.configuracoes['n_alimentos'],
            value_range=(0, 3000),
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.label_valor_alimentos = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((390, elementos_y), (50, 30)),
            text=str(self.configuracoes['n_alimentos']),
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        elementos_y += espacamento_y
        
        # Taxa de geração de alimentos
        self.label_taxa_alimento = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, elementos_y), (150, 30)),
            text="Taxa Alimento/s:",
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.slider_taxa_alimento = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((180, elementos_y), (200, 30)),
            start_value=self.configuracoes['taxa_alimento'] * 100,  # Convertido para porcentagem
            value_range=(0, 50),
            manager=self.gerenciador,
            container=self.painel_geral
        )
        
        self.label_valor_taxa_alimento = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((390, elementos_y), (50, 30)),
            text=f"{self.configuracoes['taxa_alimento'] * 100:.1f}%",
            manager=self.gerenciador,
            container=self.painel_geral
        )
    
    def _inicializar_aba_terrenos(self):
        """Inicializa os elementos da aba de configurações de terreno"""
        panel_width = self.painel_terrenos.rect.width
        
        # Nota informativa
        self.label_info_terrenos = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 10), (panel_width - 40, 30)),
            text="Percentual de cada tipo de terreno (total deve ser 100%)",
            manager=self.gerenciador,
            container=self.painel_terrenos
        )
        
        # Alerta para quando o total for diferente de 100%
        self.label_alerta_total = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((panel_width // 2 - 100, 270), (200, 30)),
            text="Total: 100%",
            manager=self.gerenciador,
            container=self.painel_terrenos
        )
        
        # Sliders para cada tipo de terreno
        tipos_terreno = list(self.configuracoes['terrenos'].keys())
        
        # Organizar em duas colunas
        coluna1 = tipos_terreno[:4]
        coluna2 = tipos_terreno[4:]
        
        # Primeira coluna
        elementos_y = 50
        espacamento_y = 40
        
        for tipo in coluna1:
            self._criar_slider_terreno(tipo, 20, elementos_y)
            elementos_y += espacamento_y
        
        # Segunda coluna
        elementos_y = 50
        for tipo in coluna2:
            self._criar_slider_terreno(tipo, panel_width // 2 + 20, elementos_y)
            elementos_y += espacamento_y
        
        # Botão para balancear automaticamente os percentuais
        self.botao_balancear = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((panel_width // 2 - 75, 230), (150, 30)),
            text="Balancear para 100%",
            manager=self.gerenciador,
            container=self.painel_terrenos
        )
    
    def _criar_slider_terreno(self, tipo_terreno, x, y):
        """Cria um slider e label para um tipo de terreno"""
        # Nome formatado (primeira letra maiúscula)
        nome_formatado = tipo_terreno.capitalize()
        
        # Label
        label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x, y), (120, 30)),
            text=f"{nome_formatado}:",
            manager=self.gerenciador,
            container=self.painel_terrenos
        )
        
        # Slider
        slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((x + 130, y), (80, 30)),
            start_value=self.configuracoes['terrenos'][tipo_terreno],
            value_range=(0, 100),
            manager=self.gerenciador,
            container=self.painel_terrenos
        )
        
        # Label para valor
        label_valor = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x + 220, y), (40, 30)),
            text=f"{self.configuracoes['terrenos'][tipo_terreno]}%",
            manager=self.gerenciador,
            container=self.painel_terrenos
        )
        
        # Armazenar referências
        self.sliders_terreno[tipo_terreno] = slider
        self.labels_valor_terreno[tipo_terreno] = label_valor
    
    def _mudar_aba(self, aba):
        """Muda entre as abas do menu"""
        if aba == 'geral':
            self.painel_geral.show()
            self.painel_terrenos.hide()
            self.aba_atual = 'geral'
        elif aba == 'terrenos':
            self.painel_geral.hide()
            self.painel_terrenos.show()
            self.aba_atual = 'terrenos'
    
    def _atualizar_alerta_total(self):
        """Atualiza o alerta de total de percentuais de terreno"""
        total = sum(self.configuracoes['terrenos'].values())
        
        texto = f"Total: {total}%"
        cor = (255, 0, 0) if total != 100 else (0, 255, 0)
        
        # Atualizar texto
        self.label_alerta_total.set_text(texto)
        
        # Mudar cor (precisamos recriar o elemento com a nova cor)
        rect = self.label_alerta_total.rect
        self.label_alerta_total.kill()
        
        self.label_alerta_total = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((rect.x, rect.y), (rect.width, rect.height)),
            text=texto,
            manager=self.gerenciador,
            container=self.painel_terrenos,
            text_colour=cor
        )
    
    def _balancear_terrenos(self):
        """Ajusta os percentuais de terreno para somar exatamente 100%"""
        total = sum(self.configuracoes['terrenos'].values())
        
        if total == 0:
            # Se todos forem zero, definir valores padrão
            for tipo, valor in {'grama': 40, 'agua': 20, 'lama': 10, 'floresta': 10, 
                              'deserto': 10, 'montanha': 5, 'gelo': 3, 'pantano': 2}.items():
                self.configuracoes['terrenos'][tipo] = valor
                self.sliders_terreno[tipo].set_current_value(valor)
                self.labels_valor_terreno[tipo].set_text(f"{valor}%")
        else:
            # Ajustar proporcionalmente
            fator = 100 / total
            
            for tipo, valor in self.configuracoes['terrenos'].items():
                novo_valor = round(valor * fator)
                self.configuracoes['terrenos'][tipo] = novo_valor
                self.sliders_terreno[tipo].set_current_value(novo_valor)
                self.labels_valor_terreno[tipo].set_text(f"{novo_valor}%")
        
        # Ajustar o último terreno para garantir soma exata de 100%
        total_atual = sum(self.configuracoes['terrenos'].values())
        if total_atual != 100:
            diferenca = 100 - total_atual
            ultimo_tipo = list(self.configuracoes['terrenos'].keys())[-1]
            self.configuracoes['terrenos'][ultimo_tipo] += diferenca
            valor_ultimo = self.configuracoes['terrenos'][ultimo_tipo]
            self.sliders_terreno[ultimo_tipo].set_current_value(valor_ultimo)
            self.labels_valor_terreno[ultimo_tipo].set_text(f"{valor_ultimo}%")
        
        self._atualizar_alerta_total()
    
    def processar_eventos(self, evento):
        """Processa eventos do menu"""
        if not self.ativo:
            return False
        
        if evento.type == pygame.USEREVENT:
            if evento.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if evento.ui_element == self.botao_iniciar:
                    # Verificar se os percentuais de terreno somam 100%
                    if sum(self.configuracoes['terrenos'].values()) != 100 and self.configuracoes['mapa'] == 'personalizado':
                        # Mostrar alerta e não iniciar
                        self._mudar_aba('terrenos')
                        return False
                    
                    self.iniciou_simulacao = True
                    self.ativo = False
                    return True
                
                elif evento.ui_element == self.botao_aba_geral:
                    self._mudar_aba('geral')
                
                elif evento.ui_element == self.botao_aba_terrenos:
                    self._mudar_aba('terrenos')
                
                elif evento.ui_element == self.botao_balancear:
                    self._balancear_terrenos()
            
            elif evento.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                # Sliders da aba geral
                if self.aba_atual == 'geral':
                    if evento.ui_element == self.slider_presas:
                        self.configuracoes['n_presas'] = int(evento.value)
                        self.label_valor_presas.set_text(str(self.configuracoes['n_presas']))
                    elif evento.ui_element == self.slider_predadores:
                        self.configuracoes['n_predadores'] = int(evento.value)
                        self.label_valor_predadores.set_text(str(self.configuracoes['n_predadores']))
                    elif evento.ui_element == self.slider_canibais:
                        self.configuracoes['n_canibais'] = int(evento.value)
                        self.label_valor_canibais.set_text(str(self.configuracoes['n_canibais']))
                    elif evento.ui_element == self.slider_alimentos:
                        self.configuracoes['n_alimentos'] = int(evento.value)
                        self.label_valor_alimentos.set_text(str(self.configuracoes['n_alimentos']))
                    elif evento.ui_element == self.slider_taxa_alimento:
                        self.configuracoes['taxa_alimento'] = evento.value / 100
                        self.label_valor_taxa_alimento.set_text(f"{evento.value:.1f}%")
                
                # Sliders da aba de terrenos
                elif self.aba_atual == 'terrenos':
                    for tipo, slider in self.sliders_terreno.items():
                        if evento.ui_element == slider:
                            self.configuracoes['terrenos'][tipo] = int(evento.value)
                            self.labels_valor_terreno[tipo].set_text(f"{int(evento.value)}%")
                            self._atualizar_alerta_total()
                            break
            
            elif evento.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if evento.ui_element == self.dropdown_mapa:
                    self.configuracoes['mapa'] = evento.text
                    
                    # Se selecionou mapa personalizado, alternar para a aba de terrenos
                    if evento.text == 'personalizado':
                        self._mudar_aba('terrenos')
                
                elif evento.ui_element == self.dropdown_modo_atributos:
                    self.configuracoes['modo_atributos'] = evento.text
        
        self.gerenciador.process_events(evento)
        return False
    
    def atualizar(self, dt):
        """Atualiza a interface do menu"""
        if not self.ativo:
            return
            
        self.gerenciador.update(dt)
    
    def desenhar(self, superficie):
        """Desenha o menu na superfície"""
        if not self.ativo:
            return
            
        # Fundo
        superficie.fill((30, 30, 50))
        
        # Desenha a UI
        self.gerenciador.draw_ui(superficie)
    
    def obter_configuracoes(self):
        """Retorna as configurações selecionadas"""
        return self.configuracoes