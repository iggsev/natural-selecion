import pygame
import random

class Parede:
    """Classe que representa obstáculos intransponíveis no mapa"""
    def __init__(self, x, y, largura, altura, cor=None):
        self.rect = pygame.Rect(x, y, largura, altura)
        
        # Se não for fornecida uma cor, gerar uma variação de cinza ou marrom para as paredes
        if cor is None:
            # Decidir entre uma parede de pedra (cinza) ou madeira (marrom)
            if random.random() < 0.7:  # 70% de chance de ser pedra
                # Variação de cinza para paredes de pedra
                cinza = random.randint(40, 70)
                self.cor = (cinza, cinza, cinza)
            else:
                # Variação de marrom para paredes de madeira/troncos
                r = random.randint(80, 120)
                g = random.randint(40, 70)
                b = random.randint(10, 30)
                self.cor = (r, g, b)
        else:
            self.cor = cor
            
        # Decorações para a parede (rachaduras, etc.) - serão desenhadas na superfície
        self.decoracoes = []
        
        # Gerar algumas decorações aleatórias (rachaduras, manchas)
        num_decoracoes = random.randint(1, 5)
        for _ in range(num_decoracoes):
            # Posição relativa na parede
            x_rel = random.random()
            y_rel = random.random()
            # Tamanho da decoração
            tamanho = random.uniform(0.05, 0.2) * min(largura, altura)
            # Tipo de decoração (1: rachadura, 2: mancha, 3: buraco)
            tipo = random.randint(1, 3)
            # Cor da decoração (variação da cor principal)
            if tipo == 1:  # Rachadura - mais clara
                cor_dec = self._clarear_cor(self.cor, 30)
            elif tipo == 2:  # Mancha - mais escura
                cor_dec = self._escurecer_cor(self.cor, 30)
            else:  # Buraco - muito escuro
                cor_dec = self._escurecer_cor(self.cor, 70)
                
            self.decoracoes.append({
                'x_rel': x_rel,
                'y_rel': y_rel,
                'tamanho': tamanho,
                'tipo': tipo,
                'cor': cor_dec
            })
    
    def _clarear_cor(self, cor, valor):
        """Retorna uma versão mais clara da cor"""
        return (
            min(255, cor[0] + valor),
            min(255, cor[1] + valor),
            min(255, cor[2] + valor)
        )
    
    def _escurecer_cor(self, cor, valor):
        """Retorna uma versão mais escura da cor"""
        return (
            max(0, cor[0] - valor),
            max(0, cor[1] - valor),
            max(0, cor[2] - valor)
        )
    
    def colidir(self, x, y, raio):
        """Verifica se um círculo com centro (x,y) e raio especificado colide com a parede"""
        # Encontra o ponto mais próximo na parede do centro do círculo
        closest_x = max(self.rect.left, min(x, self.rect.right))
        closest_y = max(self.rect.top, min(y, self.rect.bottom))
        
        # Calcula a distância entre o centro do círculo e o ponto mais próximo
        distancia_x = x - closest_x
        distancia_y = y - closest_y
        
        # Se a distância for menor que o raio, há colisão
        return (distancia_x**2 + distancia_y**2) < raio**2
    
    def resolver_colisao(self, entidade):
        """Ajusta a posição da entidade para evitar a sobreposição com a parede"""
        # Encontra o ponto mais próximo da parede ao centro da entidade
        closest_x = max(self.rect.left, min(entidade.x, self.rect.right))
        closest_y = max(self.rect.top, min(entidade.y, self.rect.bottom))
        
        # Vetores da entidade ao ponto mais próximo
        dx = entidade.x - closest_x
        dy = entidade.y - closest_y
        
        # Distância
        distancia = (dx**2 + dy**2)**0.5
        
        if distancia < entidade.tamanho:  # Há sobreposição
            # Normalização
            if distancia > 0:
                dx /= distancia
                dy /= distancia
            
            # Empurra a entidade para fora da parede
            repulsa = entidade.tamanho - distancia
            entidade.x += dx * repulsa
            entidade.y += dy * repulsa
            
            # Inverter direção da entidade (para parecer que bateu na parede)
            if hasattr(entidade, 'direcao'):
                # Calcular o vetor normal da colisão (perpendicular à superfície da parede)
                normal_x, normal_y = dx, dy
                
                # Refletir a direção em relação ao vetor normal
                if abs(normal_x) > abs(normal_y):  # Colisão predominantemente horizontal
                    entidade.direcao = 3.14159 - entidade.direcao  # Reflexão no eixo x
                else:  # Colisão predominantemente vertical
                    entidade.direcao = -entidade.direcao  # Reflexão no eixo y
    
    def desenhar(self, superficie):
        """Desenha a parede na superfície com detalhes visuais"""
        # Desenhar o retângulo principal da parede
        pygame.draw.rect(superficie, self.cor, self.rect)
        
        # Desenhar detalhes decorativos
        for dec in self.decoracoes:
            pos_x = self.rect.x + int(dec['x_rel'] * self.rect.width)
            pos_y = self.rect.y + int(dec['y_rel'] * self.rect.height)
            tamanho = int(dec['tamanho'])
            
            if dec['tipo'] == 1:  # Rachadura (linha)
                angulo = random.uniform(0, 6.28)  # Ângulo aleatório (0-2π)
                end_x = pos_x + int(math.cos(angulo) * tamanho)
                end_y = pos_y + int(math.sin(angulo) * tamanho)
                pygame.draw.line(superficie, dec['cor'], (pos_x, pos_y), (end_x, end_y), max(1, int(tamanho/5)))
            elif dec['tipo'] == 2:  # Mancha (círculo)
                pygame.draw.circle(superficie, dec['cor'], (pos_x, pos_y), tamanho//2)
            else:  # Buraco (pequeno retângulo ou círculo)
                if random.random() < 0.5:  # 50% chance de ser retângulo
                    mini_rect = pygame.Rect(
                        pos_x - tamanho//2, 
                        pos_y - tamanho//2, 
                        tamanho, 
                        tamanho
                    )
                    pygame.draw.rect(superficie, dec['cor'], mini_rect)
                else:  # 50% chance de ser círculo
                    pygame.draw.circle(superficie, dec['cor'], (pos_x, pos_y), tamanho//2)
        
        # Adicionar contorno para destacar a parede
        pygame.draw.rect(superficie, self._escurecer_cor(self.cor, 30), self.rect, 2)

# Importação para usar math.cos e math.sin
import math