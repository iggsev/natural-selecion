import random
import math
import pygame

class Criatura:
    contador_id = 0
    
    def __init__(self, x=None, y=None, velocidade=None, stamina=None, longevidade=None, tamanho=None, velocidade_nado=None, comunicacao=None, tipo_comunicacao=None, forma=None, pai=None, WIDTH=800, HEIGHT=600):
        # Atribuir ID único
        Criatura.contador_id += 1
        self.id = Criatura.contador_id
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        
        # Posição
        self.x = x if x is not None else random.randint(50, WIDTH - 50)
        self.y = y if y is not None else random.randint(50, HEIGHT - 50)
        
        # Se tem pai, herda atributos com mutação
        if pai:
            # Taxa de mutação (porcentagem de variação)
            mutacao = 0.2
            
            # Herda com mutação
            self.velocidade = max(1, pai.velocidade * random.uniform(1 - mutacao, 1 + mutacao))
            self.stamina = max(2000, pai.stamina * random.uniform(1 - mutacao, 1 + mutacao))
            self.longevidade = max(1000, pai.longevidade * random.uniform(1 - mutacao, 1 + mutacao))
            self.tamanho = max(3, pai.tamanho * random.uniform(1 - mutacao, 1 + mutacao))
            self.comunicacao = max(1, pai.comunicacao * random.uniform(1 - mutacao, 1 + mutacao))
            self.tipo_comunicacao = pai.tipo_comunicacao
            self.forma = pai.forma
            
            # Herda velocidade de nado com mutação
            self.velocidade_nado = max(0, pai.velocidade_nado * random.uniform(1 - mutacao, 1 + mutacao))
            # Chance de desenvolver velocidade de nado se o pai não tem
            if self.velocidade_nado < 0.1 and random.random() < 0.05:
                self.velocidade_nado = random.uniform(0.3, 0.7)
            
            # 10% de chance de mutar o tipo de comunicação
            if random.random() < 0.1:
                if self.comunicacao > 3:  # Se tiver comunicação alta
                    self.tipo_comunicacao = random.choice(["egoista", "altruista"])
                    # Forma baseada no tipo de comunicação
                    self.forma = "quadrado" if self.tipo_comunicacao == "egoista" else "triangulo"
                else:
                    self.tipo_comunicacao = "nenhuma"
                    self.forma = "circulo"
        else:
            # Atributos iniciais para criaturas novas
            self.velocidade = velocidade if velocidade is not None else random.uniform(1.0, 3.0)
            self.stamina = stamina if stamina is not None else random.uniform(100, 200)
            self.longevidade = longevidade if longevidade is not None else random.uniform(500, 1000)
            self.tamanho = tamanho if tamanho is not None else random.uniform(4, 8)
            self.comunicacao = comunicacao if comunicacao is not None else random.uniform(1.0, 5.0)
            
            # Atributo novo: velocidade de nado (normalmente inicia baixa ou zero)
            # A grande maioria começa sem saber nadar
            self.velocidade_nado = 0
            if random.random() < 0.1:  # 10% de chance de ter alguma habilidade inicial
                self.velocidade_nado = random.uniform(0.3, 0.8)
            
            # Tipo de comunicação e forma
            if tipo_comunicacao is not None:
                self.tipo_comunicacao = tipo_comunicacao
            elif self.comunicacao > 3:  # Se tiver comunicação alta
                self.tipo_comunicacao = random.choice(["egoista", "altruista"])
            else:
                self.tipo_comunicacao = "nenhuma"
            
            # Forma baseada no tipo de comunicação
            if forma is not None:
                self.forma = forma
            elif self.tipo_comunicacao == "egoista":
                self.forma = "quadrado"
            elif self.tipo_comunicacao == "altruista":
                self.forma = "triangulo"
            else:
                self.forma = "circulo"
        
        # Status dinâmicos
        self.energia = self.stamina * 0.8  # Começa com 80% da stamina máxima
        self.idade = 0
        self.direcao = random.uniform(0, 2 * math.pi)
        self.direção_bloqueada = False  # Para efeito de terrenos como gelo
        self.velocidade_atual = self.velocidade  # Velocidade afetada pelo terreno
        self.tempo_descanso = 0
        self.filhos = 0
        self.ultimo_alimento = 0
        self.campo_visao = self.tamanho * 10 + self.comunicacao * 5  # Campo de visão baseado no tamanho e comunicação
        self.predadores_detectados = []  # Lista de predadores que esta criatura detectou
        self.alertada = False  # Indica se foi alertada por outras criaturas
        self.tempo_alerta = 0  # Duração do alerta
        self.direcao_fuga = None  # Direção de fuga compartilhada
        
        # Variáveis para efeito visual de natação
        self.esta_nadando = False
        self.contador_nado = 0
        self.amplitude_nado = random.uniform(0.5, 1.5)
        
        # Inverso da relação entre velocidade terrestre e aquática
        # (quanto mais adaptado à água, menos adaptado ao terreno seco)
        if self.velocidade_nado > 0:
            # Penalidade na velocidade terrestre proporcional à adaptação aquática
            self.velocidade *= max(0.3, 1 - (self.velocidade_nado * 0.5))
        
        # Penalidades baseadas nos atributos
        self.consumo_energia = 0.1 + (self.velocidade / 10) + (self.tamanho / 20) + (self.comunicacao / 30)
        self.custo_reproducao = self.stamina * 0.3  # 30% da stamina para reproduzir
        
        # Calcular cor baseada nos atributos
        self._calcular_cor()
        
    def _calcular_cor(self):
        # Componente vermelho é baixo para presas
        r = 100
        # Componente verde baseado na stamina
        g = min(255, int(self.stamina / 1.2))
        # Componente azul baseado na velocidade
        b = min(255, int(self.velocidade * 70))
        
        # Adiciona mais azul para criaturas com alta velocidade de nado
        if hasattr(self, 'velocidade_nado') and self.velocidade_nado > 0:
            b = min(255, b + int(self.velocidade_nado * 100))
            # Reduz vermelho para dar aparência mais aquática
            r = max(50, r - int(self.velocidade_nado * 50))
        
        self.cor = (r, g, b)
    
    def atualizar(self, alimentos, criaturas, predadores, mapa=None):
        # Verificar se morreu de velhice
        self.idade += 1
        if self.idade >= self.longevidade:
            return False  # Morreu de velhice
        
        # Verificar se morreu de fome
        if self.energia <= 0:
            return False  # Morreu de fome
        
        # Verificar se está em água para atualizar estado de natação
        self.esta_nadando = False
        if mapa:
            terreno_atual = mapa.obter_terreno(self.x, self.y)
            if terreno_atual.nome == "Água":
                self.esta_nadando = True
                self.contador_nado += 0.2
                
                # Verificar se está se afogando (sem velocidade de nado)
                if self.velocidade_nado <= 0:
                    # Chance de desenvolver velocidade de nado em situação de quase afogamento
                    if random.random() < 0.001:  # Chance muito baixa
                        self.velocidade_nado = random.uniform(0.2, 0.4)
                        # Efeito visual de adaptação
                        if hasattr(mapa, 'simulacao') and hasattr(mapa.simulacao, 'efeitos'):
                            mapa.simulacao.efeitos.adicionar_texto_flutuante(
                                self.x, self.y - 20,
                                "Adaptação aquática!",
                                (0, 200, 255)
                            )
        
        # Se estiver descansando, diminuir o tempo de descanso
        if self.tempo_descanso > 0:
            self.tempo_descanso -= 1
            self.energia += self.stamina * 0.005  # Recupera energia ao descansar
            self.energia = min(self.energia, self.stamina)  # Limitar à stamina máxima
            return True
        
        # Diminuir tempo de alerta
        if self.tempo_alerta > 0:
            self.tempo_alerta -= 1
            if self.tempo_alerta == 0:
                self.alertada = False
                self.direcao_fuga = None
        
        # Consumir energia constantemente (metabolismo basal)
        self.energia -= self.consumo_energia
        
        # Detectar predadores no campo de visão
        self.predadores_detectados = []
        for predador in predadores:
            if self._calcular_distancia(predador) < self.campo_visao:
                self.predadores_detectados.append(predador)
                
        # Comunicar alerta a outras presas se tiver capacidade de comunicação
        if self.comunicacao > 3 and len(self.predadores_detectados) > 0:
            self._alertar_outras_presas(criaturas)
            
        # Decidir próxima ação (se não estiver com direção bloqueada pelo terreno)
        if not self.direção_bloqueada:
            if self.alertada and self.direcao_fuga is not None:
                # Se foi alertada, usar a direção de fuga compartilhada
                self.direcao = self.direcao_fuga
            elif len(self.predadores_detectados) > 0:
                # Fugir do predador mais próximo
                predador_proximo = min(self.predadores_detectados, key=lambda p: self._calcular_distancia(p))
                self._fugir_de_predador(predador_proximo)
                # Esta criatura agora está em alerta
                self.alertada = True
                self.tempo_alerta = 60  # 1 segundo de alerta (60 frames)
            else:
                # Se não há predadores, procurar comida
                alimento_proximo = self._alimento_mais_proximo(alimentos)
                if alimento_proximo:
                    self._buscar_alimento(alimento_proximo)
                else:
                    # Movimento aleatório se não houver alimento
                    if random.random() < 0.05:  # 5% de chance de mudar de direção
                        self.direcao = random.uniform(0, 2 * math.pi)
        
        # Aplicar efeitos do terreno se houver mapa
        if mapa:
            mapa.aplicar_efeitos_terreno(self)
        
        # Mover usando a velocidade afetada pelo terreno
        self.x += math.cos(self.direcao) * self.velocidade_atual
        self.y += math.sin(self.direcao) * self.velocidade_atual
        
        # Verificar colisão com paredes se houver mapa
        if mapa:
            mapa.verificar_colisao_paredes(self)
        else:
            # Manter dentro dos limites da tela (comportamento padrão se não houver mapa)
            self.x = max(0, min(self.WIDTH, self.x))
            self.y = max(0, min(self.HEIGHT, self.y))
        
        # Resetar o efeito de bloqueio de direção
        self.direção_bloqueada = False
        
        # Verificar se pode comer algum alimento
        self._comer(alimentos)
        
        # Tentar reproduzir
        self._reproduzir(criaturas)
        
        # 0.5% de chance de mutar para predador na reprodução
        if random.random() < 0.005 and self.idade > 200:  # Menos frequente e apenas em criaturas maduras
            # Importação local para evitar dependência circular
            from predador import Predador
            novo_predador = Predador(x=self.x, y=self.y, velocidade=self.velocidade*1.2, 
                        stamina=self.stamina*1.2, tamanho=self.tamanho*1.2, 
                        velocidade_nado=self.velocidade_nado,  # Herda a velocidade de nado
                        WIDTH=self.WIDTH, HEIGHT=self.HEIGHT)
            predadores.append(novo_predador)
            return False  # A criatura se transforma e "morre" como presa
        
        return True  # Continua vivo
    
    def _calcular_distancia(self, outro):
        return math.sqrt((self.x - outro.x) ** 2 + (self.y - outro.y) ** 2)
    
    def _alimento_mais_proximo(self, alimentos):
        if not alimentos:
            return None
        
        alimento_proximo = min(alimentos, key=lambda a: self._calcular_distancia(a))
        
        if self._calcular_distancia(alimento_proximo) < 250:  # Só considera comida num raio de 250px
            return alimento_proximo
        return None
    
    def _buscar_alimento(self, alimento):
        # Calcular ângulo de direção para o alimento
        dx = alimento.x - self.x
        dy = alimento.y - self.y
        self.direcao = math.atan2(dy, dx)
    
    def _fugir_de_predador(self, predador):
        # Calcular ângulo na direção oposta ao predador
        dx = self.x - predador.x
        dy = self.y - predador.y
        self.direcao = math.atan2(dy, dx)
        
        # Salvar direção de fuga para comunicar a outras presas
        self.direcao_fuga = self.direcao
        
        # Gastar mais energia ao fugir (adrenalina)
        self.energia -= self.consumo_energia * 1.5
        
    def _alertar_outras_presas(self, criaturas):
        # Se não tiver direção de fuga, não pode alertar
        if self.direcao_fuga is None:
            return
            
        # Comunicar alerta a outras presas no campo de visão
        for criatura in criaturas:
            if criatura.id != self.id and self._calcular_distancia(criatura) < self.campo_visao:
                # Se for egoísta, só alerta criaturas da mesma forma
                if self.tipo_comunicacao == "egoista" and criatura.forma != self.forma:
                    continue
                    
                # Alerta a criatura e compartilha direção de fuga
                criatura.alertada = True
                criatura.tempo_alerta = 60  # 1 segundo de alerta
                criatura.direcao_fuga = self.direcao_fuga
    
    def _comer(self, alimentos):
        for i, alimento in enumerate(alimentos):
            if self._calcular_distancia(alimento) < self.tamanho + alimento.tamanho:
                # Ganhar energia proporcional ao valor nutricional
                self.energia += alimento.valor_nutricional
                self.energia = min(self.energia, self.stamina)  # Limitar à stamina máxima
                self.ultimo_alimento = 0
                
                # Remover o alimento consumido
                alimentos.pop(i)
                return True
        
        self.ultimo_alimento += 1
        return False
    
    def _reproduzir(self, criaturas):
        # Só reproduz se tiver energia suficiente e for "adulto"
        if self.energia > self.custo_reproducao and self.idade > 100 and self.ultimo_alimento < 60:
            if random.random() < 0.01:  # 1% de chance de reproduzir a cada frame
                # Gastar energia para reproduzir
                self.energia -= self.custo_reproducao
                self.filhos += 1
                
                # Criar filho próximo ao pai
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
                
                filho = Criatura(
                    x=self.x + offset_x,
                    y=self.y + offset_y,
                    pai=self,
                    WIDTH=self.WIDTH,
                    HEIGHT=self.HEIGHT
                )
                
                criaturas.append(filho)
                
                # Descansar após reproduzir
                self.tempo_descanso = 60  # 1 segundo de descanso (60 frames a 60 FPS)
                return True
        
        return False
    
    def desenhar(self, superficie):
        # Desenhar campo de visão como um círculo transparente
        if self.comunicacao > 1:
            s = pygame.Surface((self.campo_visao*2, self.campo_visao*2), pygame.SRCALPHA)
            
            # Cor do campo de visão baseada no tipo de comunicação
            if self.tipo_comunicacao == "egoista":
                cor_campo = (180, 180, 0, 10)  # Amarelo para egoísta
            elif self.tipo_comunicacao == "altruista":
                cor_campo = (0, 200, 200, 10)  # Ciano para altruísta
            else:
                cor_campo = (100, 100, 100, 5)  # Cinza para sem comunicação
                
            pygame.draw.circle(s, cor_campo, (self.campo_visao, self.campo_visao), self.campo_visao)
            superficie.blit(s, (int(self.x - self.campo_visao), int(self.y - self.campo_visao)))
        
        # Ajustar cor baseada na idade (fica mais clara conforme envelhece)
        idade_rel = min(1.0, self.idade / self.longevidade)
        cor_ajustada = (
            min(255, self.cor[0] + int(40 * idade_rel)),
            min(255, self.cor[1] + int(40 * idade_rel)),
            min(255, self.cor[2] + int(40 * idade_rel))
        )
        
        # Destacar se estiver alertada
        if self.alertada:
            cor_contorno = (255, 255, 0)  # Amarelo para alertada
        else:
            cor_contorno = (255, 255, 255)
        
        # Posição ajustada para efeito de natação
        pos_x = int(self.x)
        pos_y = int(self.y)
        
        # Se estiver nadando, adicionar efeitos visuais de natação
        if self.esta_nadando:
            # Ondulação vertical senoidal para simular movimento de nado
            ondulacao = math.sin(self.contador_nado) * self.amplitude_nado
            pos_y += int(ondulacao)
            
            # Rastro de bolhas na água (representando movimento)
            if random.random() < 0.2 and hasattr(self, 'velocidade_nado') and self.velocidade_nado > 0:
                # Cria pequenas bolhas atrás da criatura
                bolha_x = pos_x - math.cos(self.direcao) * (self.tamanho + 2)
                bolha_y = pos_y - math.sin(self.direcao) * (self.tamanho + 2)
                pygame.draw.circle(superficie, (200, 240, 255, 150), (int(bolha_x), int(bolha_y)), 
                                 random.randint(1, max(2, int(self.velocidade_nado * 3))))
        
        # Desenhar forma baseada no tipo de comunicação
        if self.forma == "quadrado":
            # Quadrado para comunicação egoísta
            tamanho_rect = self.tamanho * 1.8
            rect = pygame.Rect(
                pos_x - tamanho_rect/2,
                pos_y - tamanho_rect/2,
                tamanho_rect,
                tamanho_rect
            )
            pygame.draw.rect(superficie, cor_ajustada, rect)
            pygame.draw.rect(superficie, cor_contorno, rect, 1)
        elif self.forma == "triangulo":
            # Triângulo para comunicação altruísta
            tamanho_tri = self.tamanho * 2
            pontos = [
                (pos_x, pos_y - tamanho_tri),
                (pos_x - tamanho_tri * 0.866, pos_y + tamanho_tri * 0.5),
                (pos_x + tamanho_tri * 0.866, pos_y + tamanho_tri * 0.5)
            ]
            pygame.draw.polygon(superficie, cor_ajustada, pontos)
            pygame.draw.polygon(superficie, cor_contorno, pontos, 1)
        else:
            # Círculo para sem comunicação
            pygame.draw.circle(superficie, cor_ajustada, (pos_x, pos_y), int(self.tamanho))
            pygame.draw.circle(superficie, cor_contorno, (pos_x, pos_y), int(self.tamanho), 1)
        
        # Desenhar "olhos" na direção do movimento
        olho_x = pos_x + math.cos(self.direcao) * (self.tamanho * 0.6)
        olho_y = pos_y + math.sin(self.direcao) * (self.tamanho * 0.6)
        
        # Ajuste nos olhos para criaturas aquáticas
        if hasattr(self, 'velocidade_nado') and self.velocidade_nado > 0.5:
            # Olhos maiores para criaturas aquáticas
            tamanho_olho = max(1, int(self.tamanho / 2.5))
            cor_olho = (0, 0, 0) if not self.esta_nadando else (0, 150, 200)
            pygame.draw.circle(superficie, cor_olho, (int(olho_x), int(olho_y)), tamanho_olho)
        else:
            # Olhos normais
            pygame.draw.circle(superficie, (0, 0, 0), (int(olho_x), int(olho_y)), max(1, int(self.tamanho / 3)))
        
        # Desenhar barra de energia
        max_barra = 20
        comprimento_barra = max(1, int((self.energia / self.stamina) * max_barra))
        pygame.draw.rect(superficie, (255, 255, 255), (pos_x - max_barra//2, pos_y - int(self.tamanho) - 5, max_barra, 3))
        pygame.draw.rect(superficie, (0, 255, 0), (pos_x - max_barra//2, pos_y - int(self.tamanho) - 5, comprimento_barra, 3))
        
        # Indicador visual de velocidade de nado para criaturas aquáticas
        if hasattr(self, 'velocidade_nado') and self.velocidade_nado > 0:
            # Desenhar pequenas barbatanas ou indicação de adaptação aquática
            # Barbatanas laterais
            barbatana_x1 = pos_x + math.cos(self.direcao + math.pi/2) * self.tamanho
            barbatana_y1 = pos_y + math.sin(self.direcao + math.pi/2) * self.tamanho
            barbatana_x2 = pos_x + math.cos(self.direcao - math.pi/2) * self.tamanho
            barbatana_y2 = pos_y + math.sin(self.direcao - math.pi/2) * self.tamanho
            
            tamanho_barbatana = self.tamanho * self.velocidade_nado * 0.7
            
            # Pontos das barbatanas
            ponta_x1 = barbatana_x1 + math.cos(self.direcao + math.pi/2) * tamanho_barbatana
            ponta_y1 = barbatana_y1 + math.sin(self.direcao + math.pi/2) * tamanho_barbatana
            ponta_x2 = barbatana_x2 + math.cos(self.direcao - math.pi/2) * tamanho_barbatana
            ponta_y2 = barbatana_y2 + math.sin(self.direcao - math.pi/2) * tamanho_barbatana
            
            # Desenhar barbatanas
            pygame.draw.line(superficie, (0, 150, 220), (barbatana_x1, barbatana_y1), (ponta_x1, ponta_y1), max(1, int(self.tamanho/4)))
            pygame.draw.line(superficie, (0, 150, 220), (barbatana_x2, barbatana_y2), (ponta_x2, ponta_y2), max(1, int(self.tamanho/4)))