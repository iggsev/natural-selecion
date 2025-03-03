import pygame
import pygame_gui
import random
import math
from terreno import Grama, Agua, Lama, Gelo, Deserto, Montanha, Floresta, Pantano
from criatura import Criatura
from predador import Predador
from canibal import Canibal
from parede import Parede

class EditorTools:
    """Classe que gerencia as ferramentas de edição do mapa e criaturas"""
    
    def __init__(self, simulacao, largura, altura):
        self.simulacao = simulacao
        self.largura = largura
        self.altura = altura
        
        # Estados do editor
        self.ativo = False
        self.ferramenta_atual = None
        self.categoria_atual = "terreno"
        self.tamanho_pincel = 20
        self.tipo_terreno_atual = "grama"
        self.tipo_criatura_atual = "presa"
        self.tipo_mutacao_atual = "velocidade"
        
        # Valor da mutação
        self.valor_mutacao = 1.2  # Multiplicador (20% de aumento)
        
        # Mapeamento de terrenos
        self.terrenos = {
            "grama": Grama,
            "agua": Agua,
            "lama": Lama,
            "gelo": Gelo,
            "deserto": Deserto,
            "montanha": Montanha,
            "floresta": Floresta,
            "pantano": Pantano,
            "parede": "parede"  # Caso especial tratado separadamente
        }
        
        # Mapeamento de criaturas
        self.criaturas = {
            "presa": Criatura,
            "predador": Predador,
            "canibal": Canibal
        }
        
        # Mapeamento de mutações
        self.mutacoes = {
            "velocidade": "velocidade",
            "stamina": "stamina",
            "energia": "energia",
            "tamanho": "tamanho",
            "velocidade_nado": "velocidade_nado",
            "campo_visao": "campo_visao"
        }
        
        # Valores dos tamanhos do pincel
        self.tamanhos_pincel = [5, 10, 20, 50, 100]
        self.indice_tamanho_atual = 2  # Começa com o tamanho médio (20)
        
        # Inicializa UI
        self.gerenciador = pygame_gui.UIManager((largura, altura))
        self._inicializar_ui()
        
        # Estado do mouse
        self.mouse_pressionado = False
        self.posicao_mouse = (0, 0)
        
    def _inicializar_ui(self):
        """Inicializa os elementos da interface de usuário do editor"""
        # Painel principal da barra de ferramentas - aumentado em altura
        self.painel_ferramentas = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, 10), (self.largura - 20, 100)),
            manager=self.gerenciador
        )
        
        # Botões para selecionar categoria de ferramentas - aumentados e reposicionados
        self.botao_terreno = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 10), (200, 35)),
            text='Ferramentas de Terreno',
            manager=self.gerenciador,
            container=self.painel_ferramentas
        )
        
        self.botao_criatura = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((230, 10), (200, 35)),
            text='Adicionar Criatura',
            manager=self.gerenciador,
            container=self.painel_ferramentas
        )
        
        self.botao_mutacao = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((440, 10), (200, 35)),
            text='Mutação de Criatura',
            manager=self.gerenciador,
            container=self.painel_ferramentas
        )
        
        # Botão para aumentar/diminuir tamanho do pincel
        self.botao_diminuir_pincel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((650, 10), (40, 35)),
            text='-',
            manager=self.gerenciador,
            container=self.painel_ferramentas
        )
        
        self.texto_tamanho_pincel = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((700, 10), (100, 35)),
            text=f'Pincel: {self.tamanho_pincel}px',
            manager=self.gerenciador,
            container=self.painel_ferramentas
        )
        
        self.botao_aumentar_pincel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((810, 10), (40, 35)),
            text='+',
            manager=self.gerenciador,
            container=self.painel_ferramentas
        )
        
        # Botão para voltar à simulação
        self.botao_voltar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.largura - 200, 10), (170, 35)),
            text='Voltar à Simulação',
            manager=self.gerenciador,
            container=self.painel_ferramentas
        )
        
        # Inicializa painéis para cada categoria de ferramentas
        self._inicializar_painel_terreno()
        self._inicializar_painel_criatura()
        self._inicializar_painel_mutacao()
        
        # Começa com o painel de terreno visível
        self._mostrar_painel("terreno")
    
    def _inicializar_painel_terreno(self):
        """Inicializa o painel de ferramentas de terreno"""
        self.painel_terreno = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((20, 55), (self.largura - 40, 40)),
            manager=self.gerenciador,
            container=self.painel_ferramentas
        )
        
        # Botões para cada tipo de terreno
        terrenos = ["grama", "agua", "lama", "gelo", "deserto", "montanha", "floresta", "pantano", "parede"]
        x_pos = 20
        largura_botao = 100
        
        for terreno in terrenos:
            botao = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x_pos, 5), (largura_botao, 30)),
                text=terreno.capitalize(),
                manager=self.gerenciador,
                container=self.painel_terreno
            )
            x_pos += largura_botao + 10
            
            # Armazena referência ao botão para acesso posterior
            setattr(self, f"botao_{terreno}", botao)
    
    def _inicializar_painel_criatura(self):
        """Inicializa o painel de ferramentas de criatura"""
        self.painel_criatura = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((20, 55), (self.largura - 40, 40)),
            manager=self.gerenciador,
            container=self.painel_ferramentas,
            visible=False
        )
        
        # Botões para cada tipo de criatura
        criaturas = ["presa", "predador", "canibal"]
        x_pos = 20
        largura_botao = 150
        
        for criatura in criaturas:
            botao = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x_pos, 5), (largura_botao, 30)),
                text=criatura.capitalize(),
                manager=self.gerenciador,
                container=self.painel_criatura
            )
            x_pos += largura_botao + 20
            
            # Armazena referência ao botão para acesso posterior
            setattr(self, f"botao_{criatura}", botao)
            
        # Opções adicionais para criaturas
        self.checkbox_aquatico = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_pos + 50, 5), (200, 30)),
            text='Com adaptação aquática',
            manager=self.gerenciador,
            container=self.painel_criatura
        )
        self.aquatico_ativo = False
        
    def _inicializar_painel_mutacao(self):
        """Inicializa o painel de ferramentas de mutação"""
        self.painel_mutacao = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((20, 55), (self.largura - 40, 40)),
            manager=self.gerenciador,
            container=self.painel_ferramentas,
            visible=False
        )
        
        # Botões para cada tipo de mutação
        mutacoes = ["velocidade", "stamina", "energia", "tamanho", "velocidade_nado", "campo_visao"]
        x_pos = 20
        largura_botao = 130
        
        for mutacao in mutacoes:
            botao = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x_pos, 5), (largura_botao, 30)),
                text=mutacao.replace('_', ' ').capitalize(),
                manager=self.gerenciador,
                container=self.painel_mutacao
            )
            x_pos += largura_botao + 10
            
            # Armazena referência ao botão para acesso posterior
            setattr(self, f"botao_{mutacao}", botao)
            
        # Controle para valor da mutação
        self.botao_reduzir = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_pos + 20, 5), (40, 30)),
            text='-',
            manager=self.gerenciador,
            container=self.painel_mutacao
        )
        
        self.label_valor_mutacao = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x_pos + 70, 5), (70, 30)),
            text=f'{int(self.valor_mutacao*100-100):+}%',
            manager=self.gerenciador,
            container=self.painel_mutacao
        )
        
        self.botao_aumentar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_pos + 150, 5), (40, 30)),
            text='+',
            manager=self.gerenciador,
            container=self.painel_mutacao
        )
    
    def _mostrar_painel(self, categoria):
        """Mostra apenas o painel da categoria selecionada"""
        self.painel_terreno.hide()
        self.painel_criatura.hide()
        self.painel_mutacao.hide()
        
        if categoria == "terreno":
            self.painel_terreno.show()
        elif categoria == "criatura":
            self.painel_criatura.show()
        elif categoria == "mutacao":
            self.painel_mutacao.show()
        
        self.categoria_atual = categoria
    
    def toggle_editor(self):
        """Ativa ou desativa o modo de edição"""
        self.ativo = not self.ativo
        
        if self.ativo:
            self.simulacao.pausa = True
        else:
            self.simulacao.pausa = False
            
        return self.ativo
    
    def atualizar_tamanho_pincel(self, aumentar=True):
        """Aumenta ou diminui o tamanho do pincel"""
        if aumentar and self.indice_tamanho_atual < len(self.tamanhos_pincel) - 1:
            self.indice_tamanho_atual += 1
        elif not aumentar and self.indice_tamanho_atual > 0:
            self.indice_tamanho_atual -= 1
            
        self.tamanho_pincel = self.tamanhos_pincel[self.indice_tamanho_atual]
        self.texto_tamanho_pincel.set_text(f'Pincel: {self.tamanho_pincel}px')
    
    def atualizar_valor_mutacao(self, aumentar=True):
        """Aumenta ou diminui o valor da mutação"""
        if aumentar:
            self.valor_mutacao = min(2.0, self.valor_mutacao + 0.1)  # Máximo de +100%
        else:
            self.valor_mutacao = max(0.5, self.valor_mutacao - 0.1)  # Mínimo de -50%
            
        # Atualiza label
        porcentagem = int(self.valor_mutacao * 100 - 100)
        sinal = '+' if porcentagem >= 0 else ''
        self.label_valor_mutacao.set_text(f'{sinal}{porcentagem}%')
    
    def toggle_adaptacao_aquatica(self):
        """Ativa ou desativa a opção de adaptação aquática para criaturas"""
        self.aquatico_ativo = not self.aquatico_ativo
        
        # Atualiza visual do botão
        if self.aquatico_ativo:
            self.checkbox_aquatico.set_text('✓ Com adaptação aquática')
        else:
            self.checkbox_aquatico.set_text('Com adaptação aquática')
    
    def processar_eventos(self, evento):
        """Processa eventos de entrada do editor"""
        # Se não estiver ativo, verifica se é para ativar
        if not self.ativo:
            # Processa ativação do editor (tecla E)
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_e:
                self.toggle_editor()
            return
        
        # Processa eventos de UI
        self.gerenciador.process_events(evento)
        
        # Processa eventos do mouse
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:  # Botão esquerdo do mouse
                self.mouse_pressionado = True
                self.aplicar_ferramenta(evento.pos)
        elif evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 1:  # Botão esquerdo do mouse
                self.mouse_pressionado = False
        elif evento.type == pygame.MOUSEMOTION:
            self.posicao_mouse = evento.pos
            if self.mouse_pressionado:
                self.aplicar_ferramenta(evento.pos)
                
        # Processa eventos de UI personalizados
        if evento.type == pygame.USEREVENT:
            if evento.user_type == pygame_gui.UI_BUTTON_PRESSED:
                # Botões de categoria
                if evento.ui_element == self.botao_terreno:
                    self._mostrar_painel("terreno")
                elif evento.ui_element == self.botao_criatura:
                    self._mostrar_painel("criatura")
                elif evento.ui_element == self.botao_mutacao:
                    self._mostrar_painel("mutacao")
                    
                # Botões de controle de editor
                elif evento.ui_element == self.botao_voltar:
                    self.toggle_editor()
                elif evento.ui_element == self.botao_aumentar_pincel:
                    self.atualizar_tamanho_pincel(True)
                elif evento.ui_element == self.botao_diminuir_pincel:
                    self.atualizar_tamanho_pincel(False)
                    
                # Verificar botões de terreno
                for terreno in self.terrenos.keys():
                    botao = getattr(self, f"botao_{terreno}", None)
                    if evento.ui_element == botao:
                        self.tipo_terreno_atual = terreno
                        break
                        
                # Verificar botões de criatura
                for criatura in self.criaturas.keys():
                    botao = getattr(self, f"botao_{criatura}", None)
                    if evento.ui_element == botao:
                        self.tipo_criatura_atual = criatura
                        break
                
                # Verificar botão de adaptação aquática
                if evento.ui_element == self.checkbox_aquatico:
                    self.toggle_adaptacao_aquatica()
                    
                # Verificar botões de mutação
                for mutacao in self.mutacoes.keys():
                    botao = getattr(self, f"botao_{mutacao}", None)
                    if evento.ui_element == botao:
                        self.tipo_mutacao_atual = mutacao
                        break
                
                # Botões de valor de mutação
                if evento.ui_element == self.botao_aumentar:
                    self.atualizar_valor_mutacao(True)
                elif evento.ui_element == self.botao_reduzir:
                    self.atualizar_valor_mutacao(False)
                    
        # Processar tecla ESC para fechar o editor
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.toggle_editor()
    
    def aplicar_ferramenta(self, pos_mouse):
        """Aplica a ferramenta atual na posição do mouse"""
        if not self.ativo:
            return
            
        # Extrai coordenadas do mouse
        x, y = pos_mouse
        
        # Aplica a ferramenta baseada na categoria atual
        if self.categoria_atual == "terreno":
            self._aplicar_terreno(x, y)
        elif self.categoria_atual == "criatura":
            self._aplicar_criatura(x, y)
        elif self.categoria_atual == "mutacao":
            self._aplicar_mutacao(x, y)
    
    def _aplicar_terreno(self, x, y):
        """Aplica a ferramenta de terreno na posição especificada"""
        if self.tipo_terreno_atual == "parede":
            # Caso especial para paredes
            meia_largura = self.tamanho_pincel // 2
            self.simulacao.mapa.adicionar_parede(
                x - meia_largura, 
                y - meia_largura, 
                self.tamanho_pincel, 
                self.tamanho_pincel
            )
        else:
            # Para outros terrenos, aplica em área circular
            classe_terreno = self.terrenos[self.tipo_terreno_atual]
            raio = self.tamanho_pincel // 2
            
            # Define a área retangular afetada para limitar o número de células a verificar
            x_min = max(0, x - raio) // self.simulacao.mapa.tamanho_celula
            y_min = max(0, y - raio) // self.simulacao.mapa.tamanho_celula
            x_max = min(self.simulacao.mapa.largura, x + raio) // self.simulacao.mapa.tamanho_celula
            y_max = min(self.simulacao.mapa.altura, y + raio) // self.simulacao.mapa.tamanho_celula
            
            # Para cada célula na área, verifica se está dentro do círculo
            for cx in range(x_min, x_max + 1):
                for cy in range(y_min, y_max + 1):
                    # Calcula o centro da célula
                    centro_x = cx * self.simulacao.mapa.tamanho_celula + self.simulacao.mapa.tamanho_celula // 2
                    centro_y = cy * self.simulacao.mapa.tamanho_celula + self.simulacao.mapa.tamanho_celula // 2
                    
                    # Verifica se o centro da célula está dentro do círculo de aplicação
                    distancia = math.sqrt((centro_x - x)**2 + (centro_y - y)**2)
                    if distancia <= raio:
                        # Define o novo terreno
                        self.simulacao.mapa.terrenos[cx][cy] = classe_terreno()
    
    def _aplicar_criatura(self, x, y):
        """Aplica a ferramenta de criatura na posição especificada"""
        # Obtém a classe da criatura
        classe_criatura = self.criaturas[self.tipo_criatura_atual]
        
        # Define a velocidade de nado se a opção estiver ativa
        velocidade_nado = None
        if self.aquatico_ativo:
            velocidade_nado = random.uniform(0.5, 1.2)
        
        # Adiciona uma nova criatura na posição do mouse
        nova_criatura = classe_criatura(
            x=x, 
            y=y,
            velocidade_nado=velocidade_nado,
            WIDTH=self.simulacao.WIDTH,
            HEIGHT=self.simulacao.HEIGHT
        )
        
        # Adiciona a criatura à lista apropriada
        if self.tipo_criatura_atual == "presa":
            self.simulacao.criaturas.append(nova_criatura)
        else:
            self.simulacao.predadores.append(nova_criatura)
    
    def _aplicar_mutacao(self, x, y):
        """Aplica a ferramenta de mutação nas criaturas próximas"""
        # Define o raio de aplicação
        raio = self.tamanho_pincel // 2
        
        # Nome do atributo a modificar
        atributo = self.mutacoes[self.tipo_mutacao_atual]
        
        # Lista para armazenar todas as criaturas (presas e predadores)
        todas_criaturas = []
        todas_criaturas.extend(self.simulacao.criaturas)
        todas_criaturas.extend(self.simulacao.predadores)
        
        # Para cada criatura, verifica se está dentro do raio de aplicação
        for criatura in todas_criaturas:
            distancia = math.sqrt((criatura.x - x)**2 + (criatura.y - y)**2)
            if distancia <= raio:
                # Aplica a mutação
                if hasattr(criatura, atributo):
                    # Obtém o valor atual
                    valor_atual = getattr(criatura, atributo)
                    
                    # Caso especial para energia: não pode ultrapassar stamina
                    if atributo == "energia":
                        novo_valor = min(criatura.stamina, valor_atual * self.valor_mutacao)
                    else:
                        novo_valor = valor_atual * self.valor_mutacao
                    
                    # Define o novo valor
                    setattr(criatura, atributo, novo_valor)
                    
                    # Caso especial para velocidade de nado: se era zero, torna possível nadar
                    if atributo == "velocidade_nado" and valor_atual == 0 and self.valor_mutacao > 1:
                        setattr(criatura, atributo, random.uniform(0.3, 0.8))
    
    def atualizar(self, dt):
        """Atualiza a interface do editor"""
        self.gerenciador.update(dt)
    
    def desenhar(self, superficie):
        """Desenha a interface do editor e visualizações de ferramentas"""
        # Desenha a interface do usuário
        self.gerenciador.draw_ui(superficie)
        
        # Se o editor estiver ativo, desenha visualização da ferramenta atual
        if self.ativo:
            x, y = self.posicao_mouse
            raio = self.tamanho_pincel // 2
            
            # Desenha círculo de visualização da área afetada
            cor_visualizacao = (255, 255, 255, 100)  # Branco semi-transparente
            
            # Ajusta a cor conforme a categoria
            if self.categoria_atual == "terreno":
                if self.tipo_terreno_atual == "agua":
                    cor_visualizacao = (0, 0, 255, 100)  # Azul para água
                elif self.tipo_terreno_atual == "parede":
                    cor_visualizacao = (100, 100, 100, 150)  # Cinza para paredes
                else:
                    cor_visualizacao = (0, 255, 0, 100)  # Verde para outros terrenos
            elif self.categoria_atual == "criatura":
                if self.tipo_criatura_atual == "presa":
                    cor_visualizacao = (100, 255, 100, 100)  # Verde claro para presas
                elif self.tipo_criatura_atual == "predador":
                    cor_visualizacao = (255, 100, 100, 100)  # Vermelho para predadores
                elif self.tipo_criatura_atual == "canibal":
                    cor_visualizacao = (255, 0, 0, 100)  # Vermelho escuro para canibais
            elif self.categoria_atual == "mutacao":
                # Cor baseada no valor da mutação (verde para positivo, vermelho para negativo)
                if self.valor_mutacao > 1:
                    intensidade = min(255, int((self.valor_mutacao - 1) * 255))
                    cor_visualizacao = (0, intensidade, 0, 150)  # Verde para aumento
                else:
                    intensidade = min(255, int((1 - self.valor_mutacao) * 255))
                    cor_visualizacao = (intensidade, 0, 0, 150)  # Vermelho para redução
            
            # Cria superfície transparente para visualização
            s = pygame.Surface((self.tamanho_pincel, self.tamanho_pincel), pygame.SRCALPHA)
            
            if self.tipo_terreno_atual == "parede" and self.categoria_atual == "terreno":
                # Retângulo para paredes
                s.fill(cor_visualizacao)
                superficie.blit(s, (x - raio, y - raio))
            else:
                # Círculo para outras ferramentas
                pygame.draw.circle(s, cor_visualizacao, (raio, raio), raio)
                superficie.blit(s, (x - raio, y - raio))
            
            # Desenha borda do círculo/retângulo
            if self.tipo_terreno_atual == "parede" and self.categoria_atual == "terreno":
                pygame.draw.rect(superficie, (255, 255, 255), (x - raio, y - raio, self.tamanho_pincel, self.tamanho_pincel), 1)
            else:
                pygame.draw.circle(superficie, (255, 255, 255), (x, y), raio, 1)