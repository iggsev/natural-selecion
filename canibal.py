import pygame
import random
import math

class Canibal:
    contador_id = 0
    
    def __init__(self, x=None, y=None, velocidade=None, stamina=None, tamanho=None, velocidade_nado=None, pai=None, WIDTH=800, HEIGHT=600):
        # Atribuir ID único
        Canibal.contador_id += 1
        self.id = Canibal.contador_id
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
            self.velocidade = max(1.8, pai.velocidade * random.uniform(1 - mutacao, 1 + mutacao))
            self.stamina = max(120, pai.stamina * random.uniform(1 - mutacao, 1 + mutacao))
            self.tamanho = max(7, pai.tamanho * random.uniform(1 - mutacao, 1 + mutacao))
            
            # Herda velocidade de nado com mutação
            if hasattr(pai, 'velocidade_nado'):
                self.velocidade_nado = max(0, pai.velocidade_nado * random.uniform(1 - mutacao, 1 + mutacao))
            else:
                self.velocidade_nado = 0
                # Chance de desenvolver velocidade de nado
                if random.random() < 0.15:
                    self.velocidade_nado = random.uniform(0.4, 0.8)
        else:
            # Atributos para canibais novos
            self.velocidade = velocidade if velocidade is not None else random.uniform(2.5, 4.0)
            self.stamina = stamina if stamina is not None else random.uniform(180, 280)
            self.tamanho = tamanho if tamanho is not None else random.uniform(9, 14)
            
            # Velocidade de nado
            if velocidade_nado is not None:
                self.velocidade_nado = velocidade_nado
            else:
                # Canibais são mais adaptáveis, maior chance de habilidade de nado
                self.velocidade_nado = 0
                if random.random() < 0.25:  # 25% de chance
                    self.velocidade_nado = random.uniform(0.4, 1.0)
        
        # Status dinâmicos
        self.energia = self.stamina * 0.7  # Começa com 70% da stamina máxima
        self.direcao = random.uniform(0, 2 * math.pi)
        self.velocidade_atual = self.velocidade  # Velocidade afetada pelo terreno
        self.direção_bloqueada = False  # Para efeito de terrenos como gelo
        self.tempo_cacar = 0
        self.alvo = None
        self.idade = 0
        self.longevidade = random.uniform(700, 1400)  # Canibais vivem ainda mais
        self.filhos = 0
        self.campo_visao = self.tamanho * 18  # Campo de visão maior que predadores normais
        
        # Variáveis para efeito visual de natação
        self.esta_nadando = False
        self.contador_nado = 0
        self.amplitude_nado = random.uniform(0.8, 2.0)
        
        # Inverso da relação entre velocidade terrestre e aquática
        # (quanto mais adaptado à água, menos adaptado ao terreno seco)
        if self.velocidade_nado > 0:
            # Penalidade na velocidade terrestre proporcional à adaptação aquática
            # Canibais são mais adaptáveis, então a penalidade é menor
            self.velocidade *= max(0.4, 1 - (self.velocidade_nado * 0.4))
        
        # Cálculo da cor baseada nos atributos (vermelho mais forte para canibais)
        r = 255  # Vermelho máximo para canibais
        # Componente azul baseado na velocidade
        b = min(255, int(self.velocidade * 30))
        # Componente verde baseado na stamina
        g = min(80, int(self.stamina / 6))
        
        # Adiciona mais azul para canibais com alta velocidade de nado
        if self.velocidade_nado > 0:
            b = min(255, b + int(self.velocidade_nado * 60))
            # Reduz levemente o vermelho para dar aparência mais aquática
            r = max(200, r - int(self.velocidade_nado * 30))
        
        self.cor = (r, g, b)
        
        # Consumo de energia (mais eficiente que predadores normais devido à dieta variada)
        self.consumo_energia = 0.12 + (self.velocidade / 10)
    
    def atualizar(self, criaturas, predadores, mapa=None):
        # Verificar se morreu de velhice
        self.idade += 1
        if self.idade >= self.longevidade:
            return False  # Morreu de velhice
            
        # Verificar se morreu de fome
        if self.energia <= 0:
            return False  # Morreu de fome
        
        # Consumir energia constantemente
        self.energia -= self.consumo_energia
        
        # Se não estiver com direção bloqueada pelo terreno
        if not self.direção_bloqueada:
            # Se já está caçando um alvo
            if self.alvo:
                # Verificar se o alvo ainda existe
                alvo_existe = False
                
                # O alvo pode ser uma criatura ou outro predador
                if hasattr(self.alvo, 'id'):  # Se o alvo tem um ID
                    # Verificar se é uma criatura
                    for criatura in criaturas:
                        if criatura.id == self.alvo.id:
                            self.alvo = criatura  # Atualizar referência
                            alvo_existe = True
                            break
                    
                    # Se não encontrou nas criaturas, procurar nos predadores
                    if not alvo_existe and predadores:
                        for predador in predadores:
                            if predador.id == self.alvo.id and predador.id != self.id:  # Não perseguir a si mesmo
                                self.alvo = predador  # Atualizar referência
                                alvo_existe = True
                                break
                
                if not alvo_existe or self.tempo_cacar <= 0:
                    # Alvo não existe mais ou cansou de caçar, encontrar novo alvo
                    self.alvo = None
                    self.tempo_cacar = 0
                    self._movimento_aleatorio()
                else:
                    # Perseguir alvo
                    self._perseguir_alvo()
                    self.tempo_cacar -= 1
            else:
                # Decidir se vai caçar predadores ou criaturas (30% de chance de escolher predadores)
                if predadores and random.random() < 0.3:
                    presa = self._encontrar_predador_alvo(predadores)
                    if presa:
                        self.alvo = presa
                        self.tempo_cacar = 200
                    else:
                        # Se não encontrou predador, procurar criatura
                        presa = self._encontrar_presa(criaturas)
                        if presa:
                            self.alvo = presa
                            self.tempo_cacar = 200
                        else:
                            self._movimento_aleatorio()
                else:
                    # Procurar criatura primeiro
                    presa = self._encontrar_presa(criaturas)
                    if presa:
                        self.alvo = presa
                        self.tempo_cacar = 200  # Caçar por 200 frames (≈3.3 segundos a 60 FPS)
                    else:
                        # Se não encontrou criatura e houver predadores, tentar caçar predador
                        if predadores:
                            presa = self._encontrar_predador_alvo(predadores)
                            if presa:
                                self.alvo = presa
                                self.tempo_cacar = 200
                            else:
                                self._movimento_aleatorio()
                        else:
                            self._movimento_aleatorio()
        
        # Aplicar efeitos do terreno se houver mapa
        if mapa:
            mapa.aplicar_efeitos_terreno(self)
        else:
            # Sem mapa, usa velocidade padrão
            self.velocidade_atual = self.velocidade
        
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
        
        # Tentar comer alguma criatura ou predador
        if self._cacar(criaturas, predadores):
            # Se conseguiu caçar, tenta reproduzir
            self._reproduzir(predadores)
        
        return True  # Continua vivo
    
    def _calcular_distancia(self, outro):
        return math.sqrt((self.x - outro.x) ** 2 + (self.y - outro.y) ** 2)
    
    def _encontrar_presa(self, criaturas):
        if not criaturas:
            return None
        
        # Filtrar criaturas que estão dentro do campo de visão
        presas_proximas = [c for c in criaturas if self._calcular_distancia(c) < self.campo_visao]
        
        if not presas_proximas:
            return None
        
        # Escolher uma presa aleatória entre as próximas
        return random.choice(presas_proximas)
    
    def _encontrar_predador_alvo(self, predadores):
        if not predadores:
            return None
        
        # Filtrar predadores que estão dentro do campo de visão e não incluir a si mesmo
        predadores_proximos = [p for p in predadores if p.id != self.id and self._calcular_distancia(p) < self.campo_visao]
        
        if not predadores_proximos:
            return None
        
        # Escolher um predador aleatório para caçar
        return random.choice(predadores_proximos)
    
    def _perseguir_alvo(self):
        dx = self.alvo.x - self.x
        dy = self.alvo.y - self.y
        self.direcao = math.atan2(dy, dx)
    
    def _movimento_aleatorio(self):
        if random.random() < 0.03:  # 3% de chance de mudar de direção
            self.direcao = random.uniform(0, 2 * math.pi)
    
    def _cacar(self, criaturas, predadores):
        # Tentar comer criaturas
        for i, criatura in enumerate(criaturas):
            if self._calcular_distancia(criatura) < self.tamanho + criatura.tamanho:
                # Ganhar energia proporcional ao tamanho da criatura
                ganho_energia = criatura.tamanho * 5 + criatura.energia * 0.5
                self.energia += ganho_energia
                self.energia = min(self.energia, self.stamina)  # Limitar à stamina máxima
                
                # Remover a criatura comida
                criaturas.pop(i)
                
                # Resetar alvo
                self.alvo = None
                self.tempo_cacar = 0
                return True
        
        # Tentar comer outros predadores
        if predadores:
            for i, predador in enumerate(predadores):
                if predador.id != self.id and self._calcular_distancia(predador) < self.tamanho + predador.tamanho:
                    # Ganhar energia proporcional ao tamanho do predador (bônus por ser predador)
                    ganho_energia = predador.tamanho * 8 + predador.energia * 0.7
                    self.energia += ganho_energia
                    self.energia = min(self.energia, self.stamina)  # Limitar à stamina máxima
                    
                    # Remover o predador comido
                    predadores.pop(i)
                    
                    # Resetar alvo
                    self.alvo = None
                    self.tempo_cacar = 0
                    return True
        
        return False
        
    def _reproduzir(self, predadores):
        # Só reproduz se tiver energia suficiente
        custo_reproducao = self.stamina * 0.4  # 40% da stamina para reproduzir
        
        if self.energia > custo_reproducao and self.idade > 150:
            if random.random() < 0.004:  # 0.4% de chance de reproduzir a cada frame (mais raro)
                # Gastar energia para reproduzir
                self.energia -= custo_reproducao
                self.filhos += 1
                
                # Criar filho próximo ao pai
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
                
                filho = Canibal(
                    x=self.x + offset_x,
                    y=self.y + offset_y,
                    pai=self,
                    WIDTH=self.WIDTH,
                    HEIGHT=self.HEIGHT
                )
                
                predadores.append(filho)
                return True
        
        return False
    
    def desenhar(self, superficie):
        # Desenhar campo de visão como um círculo transparente
        s = pygame.Surface((self.campo_visao*2, self.campo_visao*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 0, 0, 15), (self.campo_visao, self.campo_visao), self.campo_visao)
        superficie.blit(s, (int(self.x - self.campo_visao), int(self.y - self.campo_visao)))
        
        # Ajustar cor baseada na idade (fica mais clara conforme envelhece)
        idade_rel = min(1.0, self.idade / self.longevidade)
        cor_ajustada = (
            min(255, self.cor[0]),
            min(255, self.cor[1] + int(40 * idade_rel)),
            min(255, self.cor[2] + int(40 * idade_rel))
        )
        
        # Desenhar corpo do canibal
        pygame.draw.circle(superficie, cor_ajustada, (int(self.x), int(self.y)), int(self.tamanho))
        
        # Desenhar contorno (vermelho mais intenso para canibais)
        cor_contorno = (255, 0, 0)
        pygame.draw.circle(superficie, cor_contorno, (int(self.x), int(self.y)), int(self.tamanho), 1)
        
        # Desenhar "olhos" na direção do movimento (canibais têm olhos mais brilhantes)
        olho_x = self.x + math.cos(self.direcao) * (self.tamanho * 0.6)
        olho_y = self.y + math.sin(self.direcao) * (self.tamanho * 0.6)
        cor_olho = (255, 255, 0)  # Olhos amarelos brilhantes
        pygame.draw.circle(superficie, cor_olho, (int(olho_x), int(olho_y)), max(2, int(self.tamanho / 2.5)))
        
        # Desenhar barra de energia
        max_barra = 20
        comprimento_barra = max(1, int((self.energia / self.stamina) * max_barra))
        pygame.draw.rect(superficie, (255, 255, 255), (int(self.x) - max_barra//2, int(self.y) - int(self.tamanho) - 5, max_barra, 3))
        cor_barra = (255, 0, 0)  # Barra de energia vermelha mais intensa
        pygame.draw.rect(superficie, cor_barra, (int(self.x) - max_barra//2, int(self.y) - int(self.tamanho) - 5, comprimento_barra, 3))