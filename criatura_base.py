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
            else:
                self.velocidade_nado = 0
                # Chance de desenvolver velocidade de nado
                if random.random() < 0.05:
                    self.velocidade_nado = random.uniform(0.3, 0.7)
        else:
            # Atributos iniciais para criaturas novas
            self.velocidade = velocidade if velocidade is not None else random.uniform(1.5, 3.0)
            self.stamina = stamina if stamina is not None else random.uniform(100, 200)
            self.longevidade = longevidade if longevidade is not None else random.uniform(500, 1000)
            self.tamanho = tamanho if tamanho is not None else random.uniform(4, 8)
            
            # Velocidade de nado (normalmente inicia baixa ou zero)
            self.velocidade_nado = velocidade_nado if velocidade_nado is not None else 0
            if velocidade_nado is None and random.random() < 0.1:  # 10% de chance de ter alguma habilidade inicial
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