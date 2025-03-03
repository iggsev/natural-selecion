import pygame
import random
import math

class CriaturaBase:
    """Classe base para todos os tipos de criaturas (presas, predadores e canibais)"""
    contador_id = 0
    
    def __init__(self, x=None, y=None, velocidade=None, stamina=None, longevidade=None, 
                tamanho=None, velocidade_nado=None, pai=None, WIDTH=800, HEIGHT=600):
        # Atribuir ID único
        CriaturaBase.contador_id += 1
        self.id = CriaturaBase.contador_id
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        
        # Posição
        self.x = x if x is not None else random.randint(50, WIDTH - 50)
        self.y = y if y is not None else random.randint(50, HEIGHT - 50)
        
        # Aplicar verificação de limites logo na inicialização
        self._aplicar_limites_absolutos()
        
        # Se tem pai, herda atributos com mutação
        if pai:
            # Taxa de mutação (porcentagem de variação)
            mutacao = 0.2
            
            # Herda com mutação
            self.velocidade = max(1, pai.velocidade * random.uniform(1 - mutacao, 1 + mutacao))
            self.stamina = max(100, pai.stamina * random.uniform(1 - mutacao, 1 + mutacao))
            self.longevidade = max(500, pai.longevidade * random.uniform(1 - mutacao, 1 + mutacao))
            self.tamanho = max(3, pai.tamanho * random.uniform(1 - mutacao, 1 + mutacao))
            
            # Herda velocidade de nado com mutação
            if hasattr(pai, 'velocidade_nado'):
                self.velocidade_nado = max(0, pai.velocidade_nado * random.uniform(1 - mutacao, 1 + mutacao))
                # 5% de chance de mutação que altera significativamente a velocidade de nado
                if random.random() < 0.05:
                    if self.velocidade_nado > 0:
                        # Possibilidade de perder a habilidade
                        if random.random() < 0.2:
                            self.velocidade_nado = 0
                    else:
                        # Possibilidade de ganhar a habilidade
                        if random.random() < 0.2:
                            self.velocidade_nado = random.uniform(0.3, 0.7)
            else:
                self.velocidade_nado = 0
        else:
            # Atributos iniciais para criaturas novas
            self.velocidade = velocidade if velocidade is not None else random.uniform(1.5, 3.0)
            self.longevidade = longevidade if longevidade is not None else random.uniform(500, 1000)
            self.tamanho = tamanho if tamanho is not None else random.uniform(4, 8)
            self.stamina = stamina if stamina is not None else random.uniform(self.tamanho*20, self.tamanho*50)

            # Velocidade de nado (agora com apenas 5% de chance de ter habilidade inicial)
            self.velocidade_nado = velocidade_nado if velocidade_nado is not None else 0
            if velocidade_nado is None and random.random() < 0.05:  # 5% de chance de ter alguma habilidade inicial
                self.velocidade_nado = random.uniform(0.3, 0.8)
        
        # Status dinâmicos
        self.energia = self.stamina * 0.8  # Começa com 80% da stamina máxima
        self.idade = 0
        self.direcao = random.uniform(0, 2 * math.pi)
        self.direção_bloqueada = False  # Para efeito de terrenos como gelo
        self.velocidade_atual = self.velocidade  # Velocidade afetada pelo terreno
        self.filhos = 0
        self.campo_visao = self.tamanho * 10  # Campo de visão básico
        
        # Variáveis para efeito visual de natação
        self.esta_nadando = False
        self.contador_nado = 0
        self.amplitude_nado = random.uniform(0.5, 1.5)
        
        # Detector de terreno próximo (para evitar água se não souber nadar)
        self.detectar_distancia = 30  # Distância para detectar água à frente
        self.distancia_seguranca_parede = self.tamanho * 3  # Distância mínima para manter de paredes
        
        # Ajuste de velocidade baseado na adaptação aquática
        if self.velocidade_nado > 0:
            # Penalidade na velocidade terrestre proporcional à adaptação aquática
            self.velocidade *= max(0.3, 1 - (self.velocidade_nado * 0.5))
        
        # Consumo de energia básico
        self.consumo_energia = 0.1 + (self.velocidade / 10) + (self.tamanho / 20)
        
        # Cor padrão (será substituída pelas subclasses)
        self.cor = (100, 100, 100)
        self._calcular_cor()
    
    def _aplicar_limites_absolutos(self):
        """Força a criatura a ficar dentro dos limites do mapa com uma margem de segurança"""
        # Definir margem de segurança baseada no tamanho da criatura
        margem = self.tamanho + 25 if hasattr(self, 'tamanho') else 30  # Adicionar margem extra grande
        
        # Aplicar limites com a margem de segurança
        self.x = max(margem, min(self.WIDTH - margem, self.x))
        self.y = max(margem, min(self.HEIGHT - margem, self.y))
    
    def _calcular_cor(self):
        """Método a ser sobrescrito pelas subclasses para definir cores específicas"""
        pass
    
    def _calcular_distancia(self, outro):
        """Calcula a distância entre esta criatura e outra entidade"""
        return math.sqrt((self.x - outro.x) ** 2 + (self.y - outro.y) ** 2)
    
    def _detectar_agua_a_frente(self, mapa):
        """Detecta se há água na direção do movimento"""
        if not mapa:
            return False
            
        # Calcula posição à frente baseada na direção atual
        pos_x = self.x + math.cos(self.direcao) * self.detectar_distancia
        pos_y = self.y + math.sin(self.direcao) * self.detectar_distancia
        
        # Verifica se a posição está dentro dos limites do mapa
        if 0 <= pos_x < self.WIDTH and 0 <= pos_y < self.HEIGHT:
            terreno_a_frente = mapa.obter_terreno(pos_x, pos_y)
            # Retorna True se for água e a criatura não sabe nadar
            return terreno_a_frente.nome == "Água" and self.velocidade_nado <= 0
        
        return False
    
    def _ha_agua_no_caminho(self, destino_x, destino_y, mapa, distancia_verificacao=50):
        """Verifica se há água no caminho entre a criatura e o destino"""
        if not mapa or self.velocidade_nado > 0:
            # Se não há mapa ou a criatura sabe nadar, não precisa verificar
            return False
            
        # Distância total até o destino
        distancia_total = math.sqrt((destino_x - self.x)**2 + (destino_y - self.y)**2)
        
        # Se a distância for muito pequena, não precisa verificar
        if distancia_total < 10:
            return False
            
        # Ângulo em direção ao destino
        angulo = math.atan2(destino_y - self.y, destino_x - self.x)
        
        # Número de pontos a verificar (mais pontos para distâncias maiores)
        num_pontos = min(10, max(3, int(distancia_total / 20)))
        
        # Verifica vários pontos ao longo do caminho
        for i in range(1, num_pontos + 1):
            # Posição do ponto a verificar (distribuído ao longo do caminho)
            fator = i / (num_pontos + 1)  # Evita verificar exatamente no início e no fim
            check_x = self.x + (destino_x - self.x) * fator
            check_y = self.y + (destino_y - self.y) * fator
            
            # Verifica se o ponto está dentro dos limites do mapa
            if 0 <= check_x < self.WIDTH and 0 <= check_y < self.HEIGHT:
                terreno = mapa.obter_terreno(check_x, check_y)
                if terreno.nome == "Água":
                    return True  # Encontrou água no caminho
        
        # Também verifica se há água nas proximidades do caminho
        # (para criar um comportamento mais cauteloso)
        for i in range(1, num_pontos + 1):
            fator = i / (num_pontos + 1)
            check_x = self.x + (destino_x - self.x) * fator
            check_y = self.y + (destino_y - self.y) * fator
            
            # Verifica pontos perpendiculares ao caminho
            perpendicular_angulo = angulo + math.pi/2
            offset = 15  # Distância lateral para verificar
            
            # Verifica à direita do caminho
            check_x_right = check_x + math.cos(perpendicular_angulo) * offset
            check_y_right = check_y + math.sin(perpendicular_angulo) * offset
            
            # Verifica à esquerda do caminho
            check_x_left = check_x - math.cos(perpendicular_angulo) * offset
            check_y_left = check_y - math.sin(perpendicular_angulo) * offset
            
            if (0 <= check_x_right < self.WIDTH and 0 <= check_y_right < self.HEIGHT and
                mapa.obter_terreno(check_x_right, check_y_right).nome == "Água"):
                return True
                
            if (0 <= check_x_left < self.WIDTH and 0 <= check_y_left < self.HEIGHT and
                mapa.obter_terreno(check_x_left, check_y_left).nome == "Água"):
                return True
        
        return False  # Não encontrou água no caminho
    
    def _esta_perto_de_parede(self, mapa, x=None, y=None, distancia=None):
        """Verifica se a criatura está perto de uma parede"""
        if not mapa:
            return False
        
        # Usar posição fornecida ou atual da criatura
        pos_x = x if x is not None else self.x
        pos_y = y if y is not None else self.y
        
        # Usar distância fornecida ou a padrão da criatura
        dist = distancia if distancia is not None else self.distancia_seguranca_parede
        
        # Verificar se alguma parede está próxima
        for parede in mapa.paredes:
            # Encontra o ponto mais próximo na parede
            closest_x = max(parede.rect.left, min(pos_x, parede.rect.right))
            closest_y = max(parede.rect.top, min(pos_y, parede.rect.bottom))
            
            # Calcula a distância entre o ponto e a parede
            distancia_x = pos_x - closest_x
            distancia_y = pos_y - closest_y
            distancia_parede = math.sqrt(distancia_x**2 + distancia_y**2)
            
            if distancia_parede < dist:
                return True
                
        return False
    
    def _ha_parede_no_caminho(self, destino_x, destino_y, mapa):
        """Verifica se há parede no caminho entre a criatura e o destino"""
        if not mapa:
            return False
            
        # Distância total até o destino
        distancia_total = math.sqrt((destino_x - self.x)**2 + (destino_y - self.y)**2)
        
        # Se a distância for muito pequena, não precisa verificar
        if distancia_total < 10:
            return False
            
        # Número de pontos a verificar (mais pontos para distâncias maiores)
        num_pontos = min(10, max(3, int(distancia_total / 20)))
        
        # Verifica vários pontos ao longo do caminho
        for i in range(1, num_pontos + 1):
            # Posição do ponto a verificar
            fator = i / (num_pontos + 1)
            check_x = self.x + (destino_x - self.x) * fator
            check_y = self.y + (destino_y - self.y) * fator
            
            # Verifica se o ponto está perto de uma parede
            if self._esta_perto_de_parede(mapa, check_x, check_y, self.distancia_seguranca_parede * 0.8):
                return True  # Encontrou parede no caminho
        
        # Verifica se o destino está perto de uma parede
        if self._esta_perto_de_parede(mapa, destino_x, destino_y, self.distancia_seguranca_parede):
            return True  # O destino está muito perto de uma parede
            
        return False  # Não encontrou parede no caminho
    
    def _direção_fuga_parede(self, mapa):
        """Calcula a direção para fugir da parede mais próxima"""
        if not mapa:
            return None
            
        parede_mais_proxima = None
        ponto_mais_proximo = None
        menor_distancia = float('inf')
        
        # Encontrar a parede mais próxima
        for parede in mapa.paredes:
            # Encontra o ponto mais próximo na parede
            closest_x = max(parede.rect.left, min(self.x, parede.rect.right))
            closest_y = max(parede.rect.top, min(self.y, parede.rect.bottom))
            
            # Calcula a distância entre a criatura e o ponto na parede
            distancia_x = self.x - closest_x
            distancia_y = self.y - closest_y
            distancia = math.sqrt(distancia_x**2 + distancia_y**2)
            
            if distancia < menor_distancia:
                menor_distancia = distancia
                parede_mais_proxima = parede
                ponto_mais_proximo = (closest_x, closest_y)
        
        if ponto_mais_proximo:
            # Calcular ângulo na direção oposta à parede
            dx = self.x - ponto_mais_proximo[0]
            dy = self.y - ponto_mais_proximo[1]
            
            # Se a distância for muito pequena, adicionar um pequeno offset aleatório
            # para evitar divisão por zero
            if abs(dx) < 0.1 and abs(dy) < 0.1:
                dx += random.uniform(-1, 1)
                dy += random.uniform(-1, 1)
                
            return math.atan2(dy, dx)
            
        return None
    
    def _evitar_agua(self):
        """Muda a direção para evitar água detectada à frente"""
        # Muda a direção para uma direção perpendicular
        novo_angulo = self.direcao + random.choice([math.pi/2, -math.pi/2])
        self.direcao = novo_angulo % (2 * math.pi)  # Normaliza o ângulo
    
    def _evitar_parede(self, mapa):
        """Ajusta a direção para evitar colidir com paredes"""
        # Obter direção de fuga da parede
        direcao_fuga = self._direção_fuga_parede(mapa)
        
        if direcao_fuga is not None:
            # Ajusta a direção para a direção de fuga
            self.direcao = direcao_fuga
            
            # Adiciona um pequeno desvio aleatório para comportamento mais natural
            self.direcao += random.uniform(-0.2, 0.2)
            return True
            
        return False
    
    def atualizar(self, *args, **kwargs):
        """Método base de atualização a ser implementado pelas subclasses"""
        # Verificar se morreu de velhice
        self.idade += 1
        if self.idade >= self.longevidade:
            return False  # Morreu de velhice
            
        # Verificar se morreu de fome
        if self.energia <= 0:
            return False  # Morreu de fome
        
        # Consumir energia constantemente
        self.energia -= self.consumo_energia
        
        # Verificar se está em água para atualizar estado de natação
        self.esta_nadando = False
        if 'mapa' in kwargs and kwargs['mapa']:
            mapa = kwargs['mapa']
            
            # Verificar se está perto de uma parede e evitar se necessário
            if self._esta_perto_de_parede(mapa):
                self._evitar_parede(mapa)
            
            # Detectar água à frente e evitar se não souber nadar
            if self._detectar_agua_a_frente(mapa):
                self._evitar_agua()
            
            terreno_atual = mapa.obter_terreno(self.x, self.y)
            if terreno_atual.nome == "Água":
                self.esta_nadando = True
                self.contador_nado += 0.2
                
                # A criatura está na água mas não sabe nadar - efeito de desespero
                if self.velocidade_nado <= 0:
                    # Tentar sair da água com movimentos mais rápidos e aleatórios
                    if random.random() < 0.3:  # 30% de chance de mudar direção em pânico
                        self.direcao = random.uniform(0, 2 * math.pi)
        
        # Como uma última linha de defesa, forçar limites absolutos do mapa
        self._aplicar_limites_absolutos()
        
        return True  # Continua vivo por padrão
    
    def desenhar(self, superficie):
        """Método base de desenho com comportamentos comuns"""
        # Desenhar campo de visão como um círculo transparente
        s = pygame.Surface((self.campo_visao*2, self.campo_visao*2), pygame.SRCALPHA)
        # A cor do campo de visão varia por tipo - será definida nas subclasses
        cor_campo = (100, 100, 100, 10)  # Cinza transparente padrão
        pygame.draw.circle(s, cor_campo, (self.campo_visao, self.campo_visao), self.campo_visao)
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
        if self.esta_nadando:
            # Ondulação vertical senoidal para simular movimento de nado
            ondulacao = math.sin(self.contador_nado) * self.amplitude_nado
            pos_y += int(ondulacao)
            
            # Rastro de bolhas na água (representando movimento)
            if random.random() < 0.2 and self.velocidade_nado > 0:
                # Cria pequenas bolhas atrás da criatura
                bolha_x = pos_x - math.cos(self.direcao) * (self.tamanho + 2)
                bolha_y = pos_y - math.sin(self.direcao) * (self.tamanho + 2)
                pygame.draw.circle(superficie, (200, 240, 255, 150), (int(bolha_x), int(bolha_y)), 
                                 random.randint(1, max(2, int(self.velocidade_nado * 3))))
        
        # Desenhar corpo (implementação específica nas subclasses)
        self._desenhar_corpo(superficie, pos_x, pos_y, cor_ajustada)
        
        # Desenhar barra de energia
        max_barra = 20
        comprimento_barra = max(1, int((self.energia / self.stamina) * max_barra))
        pygame.draw.rect(superficie, (255, 255, 255), (pos_x - max_barra//2, pos_y - int(self.tamanho) - 5, max_barra, 3))
        cor_barra = self._obter_cor_barra_energia()
        pygame.draw.rect(superficie, cor_barra, (pos_x - max_barra//2, pos_y - int(self.tamanho) - 5, comprimento_barra, 3))
    
    def _desenhar_corpo(self, superficie, pos_x, pos_y, cor_ajustada):
        """Método para desenhar o corpo da criatura, a ser sobrescrito pelas subclasses"""
        # Implementação padrão - círculo simples
        pygame.draw.circle(superficie, cor_ajustada, (pos_x, pos_y), int(self.tamanho))
        pygame.draw.circle(superficie, (255, 255, 255), (pos_x, pos_y), int(self.tamanho), 1)
    
    def _obter_cor_barra_energia(self):
        """Retorna a cor da barra de energia, pode ser sobrescrito pelas subclasses"""
        return (0, 255, 0)  # Verde padrão