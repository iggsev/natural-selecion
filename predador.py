import pygame
import random
import math
from criatura_base import CriaturaBase

class Predador(CriaturaBase):
    """Classe que representa predadores carnívoros"""
    
    def __init__(self, x=None, y=None, velocidade=None, stamina=None, tamanho=None, 
                velocidade_nado=None, pai=None, WIDTH=800, HEIGHT=600):
        # Inicializar a classe base primeiro
        super().__init__(x, y, velocidade, stamina, None, tamanho, velocidade_nado, pai, WIDTH, HEIGHT)
        
        # Atributos específicos de predadores
        # Ajustar valores específicos para predadores
        if pai and isinstance(pai, Predador):
            # Herança de atributos já aconteceu no construtor da classe base
            pass  # As mutações já foram aplicadas na classe base
        else:
            # Atributos para predadores novos (quando não vem de mutação)
            self.velocidade = velocidade if velocidade is not None else random.uniform(2.0, 3.5)
            self.stamina = stamina if stamina is not None else random.uniform(1500, 2500)
            self.tamanho = tamanho if tamanho is not None else random.uniform(8, 12)
            
            # Predadores vivem mais tempo
            self.longevidade = random.uniform(600, 1200)  # Predadores vivem um pouco mais
        
        # Status dinâmicos específicos de predadores
        self.tempo_cacar = 0
        self.alvo = None
        self.campo_visao = self.tamanho * 15  # Campo de visão maior que presas
        
        # Consumo de energia (predadores gastam mais)
        self.consumo_energia = 0.1 + (self.velocidade / 10)
        self.custo_reproducao = self.energia * 0.15

        # Calcular cor com base nos atributos
        self._calcular_cor()
    
    def _calcular_cor(self):
        """Define a cor baseada nos atributos do predador"""
        # Base: vermelho claro para predadores normais
        r = 220
        # Componente azul baseado na velocidade
        b = min(255, int(self.velocidade * 40))
        # Componente verde baseado na stamina
        g = min(100, int(self.stamina / 5))
        
        self.cor = (r, g, b)
    
    def atualizar(self, criaturas, predadores=None, mapa=None):
        # Chamar o método base primeiro para verificações de vida e energia
        if not super().atualizar(mapa=mapa):
            return False  # Morreu de velhice ou fome
        
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
                                     velocidade_nado=self.velocidade_nado,
                                     WIDTH=self.WIDTH, HEIGHT=self.HEIGHT)
                predadores.append(novo_canibal)
                return False  # O predador se transforma em canibal
        
        return True  # Continua vivo
    
    def _encontrar_presa(self, criaturas):
        """Encontra uma presa potencial dentro do campo de visão"""
        if not criaturas:
            return None
        
        # Filtrar criaturas que estão dentro do campo de visão
        presas_proximas = [c for c in criaturas if self._calcular_distancia(c) < self.campo_visao]
        
        if not presas_proximas:
            return None
        
        # Escolher uma presa aleatória entre as próximas (mais realista)
        return random.choice(presas_proximas)
    
    def _perseguir_alvo(self):
        """Direciona o predador em direção ao alvo"""
        dx = self.alvo.x - self.x
        dy = self.alvo.y - self.y
        self.direcao = math.atan2(dy, dx)
    
    def _movimento_aleatorio(self):
        """Faz o predador se mover aleatoriamente"""
        if random.random() < 0.03:  # 3% de chance de mudar de direção
            self.direcao = random.uniform(0, 2 * math.pi)
    
    def _cacar(self, criaturas):
        """Tenta capturar e comer uma presa próxima"""
        # Tentar comer criaturas
        for i, criatura in enumerate(criaturas):
            if self._calcular_distancia(criatura) < self.tamanho + criatura.tamanho:
                # Ganhar energia proporcional ao tamanho da criatura
                ganho_energia = criatura.tamanho * 50 + criatura.energia * 5
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
        """Tenta reproduzir se tiver energia suficiente"""
        
        if self.energia > self.custo_reproducao and self.idade > 20:
            if random.random() < 0.1:  # 0.5% de chance de reproduzir a cada frame
                # Gastar energia para reproduzir
                self.energia -= self.custo_reproducao
                self.filhos += 1
                
                # Criar filho próximo ao pai
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
                
                # 15% de chance de mutação para canibal durante a reprodução
                if random.random() < 0.05:
                    # Importação local para evitar circular import
                    from canibal import Canibal
                    filho = Canibal(
                        x=self.x + offset_x,
                        y=self.y + offset_y,
                        velocidade=self.velocidade,
                        stamina=self.stamina,
                        tamanho=self.tamanho,
                        velocidade_nado=self.velocidade_nado,
                        WIDTH=self.WIDTH,
                        HEIGHT=self.HEIGHT
                    )
                else:
                    filho = Predador(
                        x=self.x + offset_x,
                        y=self.y + offset_y,
                        pai=self,  # Herdar atributos com mutação
                        WIDTH=self.WIDTH,
                        HEIGHT=self.HEIGHT
                    )
                
                predadores.append(filho)
                return True
        
        return False
    
    def _desenhar_corpo(self, superficie, pos_x, pos_y, cor_ajustada):
        """Desenha o corpo do predador"""
        # Desenhar corpo do predador
        pygame.draw.circle(superficie, cor_ajustada, (pos_x, pos_y), int(self.tamanho))
        
        # Desenhar contorno
        cor_contorno = (200, 50, 50)
        pygame.draw.circle(superficie, cor_contorno, (pos_x, pos_y), int(self.tamanho), 1)
        
        # Desenhar "olhos" na direção do movimento (predadores têm olhos maiores)
        olho_x = pos_x + math.cos(self.direcao) * (self.tamanho * 0.6)
        olho_y = pos_y + math.sin(self.direcao) * (self.tamanho * 0.6)
        
        # Cor dos olhos muda se for aquático e estiver nadando
        if self.velocidade_nado > 0.5 and self.esta_nadando:
            cor_olho = (0, 200, 255)  # Azul claro para predadores aquáticos quando nadando
        else:
            cor_olho = (255, 200, 0)  # Cor padrão
            
        pygame.draw.circle(superficie, cor_olho, (int(olho_x), int(olho_y)), max(2, int(self.tamanho / 2.5)))
        
        # Indicador visual de velocidade de nado para predadores aquáticos
        if self.velocidade_nado > 0:
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
    
    def desenhar(self, superficie):
        """Sobrescreve o método de desenho para incluir o campo de visão específico do predador"""
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
            if random.random() < 0.3 and self.velocidade_nado > 0:
                # Cria pequenas bolhas atrás do predador
                bolha_x = pos_x - math.cos(self.direcao) * (self.tamanho + 3)
                bolha_y = pos_y - math.sin(self.direcao) * (self.tamanho + 3)
                pygame.draw.circle(superficie, (200, 240, 255, 180), (int(bolha_x), int(bolha_y)), 
                                 random.randint(1, max(3, int(self.velocidade_nado * 4))))
        
        # Desenhar corpo do predador
        self._desenhar_corpo(superficie, pos_x, pos_y, cor_ajustada)
        
        # Desenhar barra de energia
        max_barra = 20
        comprimento_barra = max(1, int((self.energia / self.stamina) * max_barra))
        pygame.draw.rect(superficie, (255, 255, 255), (pos_x - max_barra//2, pos_y - int(self.tamanho) - 5, max_barra, 3))
        cor_barra = (220, 50, 50)
        pygame.draw.rect(superficie, cor_barra, (pos_x - max_barra//2, pos_y - int(self.tamanho) - 5, comprimento_barra, 3))
    
    def _obter_cor_barra_energia(self):
        """Retorna a cor da barra de energia"""
        return (220, 50, 50)  # Vermelho para predadores
