import pygame

class Parede:
    """Classe que representa obstáculos intransponíveis no mapa"""
    def __init__(self, x, y, largura, altura, cor=(50, 50, 50)):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor = cor
    
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
    
    def desenhar(self, superficie):
        """Desenha a parede na superfície"""
        pygame.draw.rect(superficie, self.cor, self.rect)
