import pygame
import random

class Alimento:
    def __init__(self, x=None, y=None, valor_nutricional=None, WIDTH=800, HEIGHT=600):
        self.x = x if x is not None else random.randint(20, WIDTH - 20)
        self.y = y if y is not None else random.randint(20, HEIGHT - 20)
        self.valor_nutricional = valor_nutricional if valor_nutricional is not None else random.randint(100, 300)
        self.tamanho = max(2, int(self.valor_nutricional / 50))
        self.cor = (
            min(255, 100 + self.valor_nutricional * 5),
            min(255, 200 + self.valor_nutricional * 2),
            0
        )
    
    def desenhar(self, superficie):
        pygame.draw.circle(superficie, self.cor, (int(self.x), int(self.y)), self.tamanho)
