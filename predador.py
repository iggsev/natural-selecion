import pygame
import random
import math

class Predador:
    contador_id = 0
    
    def __init__(self, x=None, y=None, velocidade=None, stamina=None, tamanho=None,velocidade_nado=None, pai=None, WIDTH=800, HEIGHT=600):
        # Atribuir ID único
        Predador.contador_id += 1
        self.id = Predador.contador_id
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
            self.velocidade = max(0.5, pai.velocidade * random.uniform(1 - mutacao, 1 + mutacao))
            self.stamina = max(1000, pai.stamina * random.uniform(1 - mutacao, 1 + mutacao))
            self.tamanho = max(6, pai.tamanho * random.uniform(1 - mutacao, 1 + mutacao))

                        # Herda velocidade de nado com mutação
            if hasattr(pai, 'velocidade_nado'):
                self.velocidade_nado = max(0, pai.velocidade_nado * random.uniform(1 - mutacao, 1 + mutacao))
            else:
                self.velocidade_nado = 0
                # Chance de desenvolver velocidade de nado
                if random.random() < 0.15:
                    self.velocidade_nado = random.uniform(0.4, 0.8)
        else:
            # Atributos para predadores novos (quando não vem de mutação)
            self.velocidade = velocidade if velocidade is not None else random.uniform(2.0, 3.5)
            self.stamina = stamina if stamina is not None else random.uniform(150, 250)
            self.tamanho = tamanho if tamanho is not None else random.uniform(8, 12)
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
        self.tempo_cacar = 0
        self.alvo = None
        self.idade = 0
        self.longevidade = random.uniform(600, 1200)  # Predadores vivem um pouco mais
        self.filhos = 0
        self.campo_visao = self.tamanho * 15  # Campo de visão maior que presas
        

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
        # Cálculo da cor baseada nos atributos
        # Base: vermelho claro para predadores normais
        r = 220
        # Componente azul baseado na velocidade
        b = min(255, int(self.velocidade * 40))
        # Componente verde baseado na stamina
        g = min(100, int(self.stamina / 5))
        
        self.cor = (r, g, b)
        
        # Consumo de energia
        self.consumo_energia = 0.15 + (self.velocidade / 8)
    
    def atualizar(self, criaturas, predadores=None, mapa=None):
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
                    if random.random() < 0.001:
                        self.velocidade_nado = random.uniform(0.2, 0.5)
                        # Efeito visual de adaptação
                        if hasattr(mapa, 'simulacao') and hasattr(mapa.simulacao, 'efeitos'):
                            mapa.simulacao.efeitos.adicionar_texto_flutuante(
                                self.x, self.y - 20,
                                "Adaptação aquática!",
                                (200, 100, 255)
                            )
        
        # Consumir energia constantemente
        self.energia -= self.consumo_energia
        
        # Se não estiver com direção bloqueada pelo terreno
        if not hasattr(self, 'direção_bloqueada') or not self.direção_bloqueada:
            # Se já está caçando um alvo
            if self.alvo:
                # Verificar se o alvo ainda existe
                alvo_existe = False
                
                # O alvo é sempre uma criatura para predadores normais
                for criatura in criaturas:
                    if criatura.id == self.alvo.id:
                        self.alvo = criatura  # Atualizar referência
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
                # Encontrar novo alvo
                presa = self._encontrar_presa(criaturas)
                if presa:
                    self.alvo = presa
                    self.tempo_cacar = 200  # Caçar por 200 frames (≈3.3 segundos a 60 FPS)
                else:
                    self._movimento_aleatorio()
        
        # Aplicar efeitos do terreno se houver mapa
        if mapa:
            # Garante que as propriedades necessárias existam
            if not hasattr(self, 'velocidade_atual'):
                self.velocidade_atual = self.velocidade
            if not hasattr(self, 'direção_bloqueada'):
                self.direção_bloqueada = False
                
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
        if hasattr(self, 'direção_bloqueada'):
            self.direção_bloqueada = False
        
        # Tentar comer alguma criatura
        if self._cacar(criaturas):
            # Se conseguiu caçar, tenta reproduzir
            self._reproduzir(predadores)
            
            # Pequena chance de evoluir para canibal
            if random.random() < 0.05 and self.energia > self.stamina * 0.8:
                # Importação local para evitar circular import
                from canibal import Canibal
                novo_canibal = Canibal(x=self.x, y=self.y, velocidade=self.velocidade, 
                                     stamina=self.stamina, tamanho=self.tamanho, 
                                     velocidade_nado=self.velocidade_nado if hasattr(self, 'velocidade_nado') else 0,
                                     WIDTH=self.WIDTH, HEIGHT=self.HEIGHT)
                predadores.append(novo_canibal)
                return False  # O predador se transforma em canibal
        
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
        
        # Escolher uma presa aleatória entre as próximas (mais realista)
        return random.choice(presas_proximas)
    
    def _perseguir_alvo(self):
        dx = self.alvo.x - self.x
        dy = self.alvo.y - self.y
        self.direcao = math.atan2(dy, dx)
    
    def _movimento_aleatorio(self):
        if random.random() < 0.03:  # 3% de chance de mudar de direção
            self.direcao = random.uniform(0, 2 * math.pi)
    
    def _cacar(self, criaturas):
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
        
        return False
        
    def _reproduzir(self, predadores):
        # Só reproduz se tiver energia suficiente
        custo_reproducao = self.stamina * 0.4  # 40% da stamina para reproduzir
        
        if self.energia > custo_reproducao and self.idade > 150:
            if random.random() < 0.005:  # 0.5% de chance de reproduzir a cada frame
                # Gastar energia para reproduzir
                self.energia -= custo_reproducao
                self.filhos += 1
                
                # Criar filho próximo ao pai
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
                
                # 15% de chance de mutação para canibal
                if random.random() < 0.15:
                    # Importação local para evitar circular import
                    from canibal import Canibal
                    filho = Canibal(
                        x=self.x + offset_x,
                        y=self.y + offset_y,
                        velocidade=self.velocidade,
                        stamina=self.stamina,
                        tamanho=self.tamanho,
                        WIDTH=self.WIDTH,
                        HEIGHT=self.HEIGHT
                    )
                else:
                    filho = Predador(
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
        pygame.draw.circle(s, (200, 0, 0, 10), (self.campo_visao, self.campo_visao), self.campo_visao)
        superficie.blit(s, (int(self.x - self.campo_visao), int(self.y - self.campo_visao)))
        
        # Ajustar cor baseada na idade (fica mais clara conforme envelhece)
        idade_rel = min(1.0, self.idade / self.longevidade)
        cor_ajustada = (
            min(255, self.cor[0] + int(40 * idade_rel)),
            min(255, self.cor[1] + int(40 * idade_rel)),
            min(255, self.cor[2] + int(40 * idade_rel))
        )
        
        # Posição ajustada para efeito de natação
        pos_x = int(self.x)
        pos_y = int(self.y)
        
        # Se estiver nadando, adicionar efeitos visuais de natação
        if hasattr(self, 'esta_nadando') and self.esta_nadando:
            # Ondulação vertical senoidal para simular movimento de nado
            if hasattr(self, 'contador_nado') and hasattr(self, 'amplitude_nado'):
                ondulacao = math.sin(self.contador_nado) * self.amplitude_nado
                pos_y += int(ondulacao)
            
            # Rastro de bolhas na água (representando movimento)
            if random.random() < 0.3 and hasattr(self, 'velocidade_nado') and self.velocidade_nado > 0:
                # Cria pequenas bolhas atrás do predador
                bolha_x = pos_x - math.cos(self.direcao) * (self.tamanho + 3)
                bolha_y = pos_y - math.sin(self.direcao) * (self.tamanho + 3)
                pygame.draw.circle(superficie, (200, 240, 255, 180), (int(bolha_x), int(bolha_y)), 
                                 random.randint(1, max(3, int((self.velocidade_nado if hasattr(self, 'velocidade_nado') else 0) * 4))))
        
        # Desenhar corpo do predador
        pygame.draw.circle(superficie, cor_ajustada, (pos_x, pos_y), int(self.tamanho))
        
        # Desenhar contorno
        cor_contorno = (200, 50, 50)
        pygame.draw.circle(superficie, cor_contorno, (pos_x, pos_y), int(self.tamanho), 1)
        
        # Desenhar "olhos" na direção do movimento (predadores têm olhos maiores)
        olho_x = pos_x + math.cos(self.direcao) * (self.tamanho * 0.6)
        olho_y = pos_y + math.sin(self.direcao) * (self.tamanho * 0.6)
        
        # Cor dos olhos muda se for aquático e estiver nadando
        if (hasattr(self, 'velocidade_nado') and self.velocidade_nado > 0.5 and
            hasattr(self, 'esta_nadando') and self.esta_nadando):
            cor_olho = (0, 200, 255)  # Azul claro para predadores aquáticos quando nadando
        else:
            cor_olho = (255, 200, 0)  # Cor padrão
            
        pygame.draw.circle(superficie, cor_olho, (int(olho_x), int(olho_y)), max(2, int(self.tamanho / 2.5)))
        
        # Desenhar barra de energia
        max_barra = 20
        comprimento_barra = max(1, int((self.energia / self.stamina) * max_barra))
        pygame.draw.rect(superficie, (255, 255, 255), (pos_x - max_barra//2, pos_y - int(self.tamanho) - 5, max_barra, 3))
        cor_barra = (220, 50, 50)
        pygame.draw.rect(superficie, cor_barra, (pos_x - max_barra//2, pos_y - int(self.tamanho) - 5, comprimento_barra, 3))
        
        # Indicador visual de velocidade de nado para predadores aquáticos
        if hasattr(self, 'velocidade_nado') and self.velocidade_nado > 0:
            # Desenhar barbatanas dorsais ou nadadeiras
            # Nadadeira dorsal (mais proeminente em predadores)
            nadadeira_base_x = pos_x - math.cos(self.direcao) * (self.tamanho * 0.2)
            nadadeira_base_y = pos_y - math.sin(self.direcao) * (self.tamanho * 0.2)
            
            # Altura da nadadeira baseada na velocidade de nado
            altura_nadadeira = self.tamanho * self.velocidade_nado * 1.2
            
            # Ponta da nadadeira
            ponta_x = nadadeira_base_x + math.cos(self.direcao + math.pi/2) * altura_nadadeira
            ponta_y = nadadeira_base_y + math.sin(self.direcao + math.pi/2) * altura_nadadeira
            
            # Desenhar nadadeira como um triângulo
            pontos_nadadeira = [
                (nadadeira_base_x, nadadeira_base_y),
                (ponta_x, ponta_y),
                (nadadeira_base_x + math.cos(self.direcao) * (self.tamanho * 0.6), 
                 nadadeira_base_y + math.sin(self.direcao) * (self.tamanho * 0.6))
            ]
            
            pygame.draw.polygon(superficie, (0, 100, 200), pontos_nadadeira)