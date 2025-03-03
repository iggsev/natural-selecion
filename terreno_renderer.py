def _adicionar_detalhes(self, textura, terreno, tamanho_celula):
        """Adiciona detalhes à textura baseado no tipo de terreno"""
        nome_terreno = terreno.nome
        
        # Adicionar detalhes específicos para cada tipo
        if nome_terreno == "Grama":
            # Adiciona algumas linhas curtas para representar grama
            for _ in range(5):
                x = random.randint(2, tamanho_celula - 3)
                y = random.randint(2, tamanho_celula - 6)
                altura = random.randint(3, 6)
                cor = (50, 150, 50)  # Verde mais escuro para os fios de grama
                pygame.draw.line(textura, cor, (x, y + altura), (x, y), 1)
                
        elif nome_terreno == "Lama":
            # Adiciona algumas manchas mais escuras
            for _ in range(3):
                x = random.randint(2, tamanho_celula - 7)
                y = random.randint(2, tamanho_celula - 7)
                raio = random.randint(2, 4)
                cor = (100, 50, 10)  # Marrom mais escuro
                pygame.draw.circle(textura, cor, (x, y), raio)
                
        elif nome_terreno == "Gelo":
            # Adiciona linhas de rachaduras no gelo
            for _ in range(2):
                x1 = random.randint(0, tamanho_celula - 1)
                y1 = random.randint(0, tamanho_celula - 1)
                angulo = random.uniform(0, 2 * math.pi)
                comprimento = random.randint(5, 10)
                x2 = int(x1 + math.cos(angulo) * comprimento)
                y2 = int(y1 + math.sin(angulo) * comprimento)
                cor = (240, 248, 255)  # Branco azulado para rachaduras
                pygame.draw.line(textura, cor, (x1, y1), (x2, y2), 1)
                
        elif nome_terreno == "Água":
            # Adiciona pequenas ondas
            for i in range(2):
                y = int(tamanho_celula / 3) * (i + 1)
                pontos = []
                for x in range(0, tamanho_celula, 4):
                    pontos.append((x, y + random.randint(-1, 1)))
                
                if len(pontos) > 1:
                    cor = (80, 180, 250)  # Azul mais claro para ondas
                    pygame.draw.lines(textura, cor, False, pontos, 1)
                    
        elif nome_terreno == "Deserto":
            # Adiciona pequenos pontos para representar grãos de areia
            for _ in range(8):
                x = random.randint(0, tamanho_celula - 1)
                y = random.randint(0, tamanho_celula - 1)
                cor = (250, 220, 160)  # Bege mais claro
                pygame.draw.circle(textura, cor, (x, y), 1)
                
        elif nome_terreno == "Montanha":
            # Adiciona algumas linhas para representar contornos rochosos
            for _ in range(2):
                x1 = random.randint(0, tamanho_celula // 2)
                y1 = random.randint(tamanho_celula // 2, tamanho_celula - 1)
                x2 = random.randint(tamanho_celula // 2, tamanho_celula - 1)
                y2 = random.randint(0, tamanho_celula // 2)
                cor = (140, 140, 140)  # Cinza mais claro
                pygame.draw.line(textura, cor, (x1, y1), (x2, y2), 1)
                
        elif nome_terreno == "Floresta":
            # Adiciona pequenas árvores simplificadas
            for _ in range(1):
                x = random.randint(5, tamanho_celula - 6)
                y = random.randint(10, tamanho_celula - 5)
                # Tronco
                pygame.draw.line(textura, (80, 50, 20), (x, y), (x, y - 6), 1)
                # Copa
                cor_copa = (20, 100, 20)  # Verde escuro
                pygame.draw.circle(textura, cor_copa, (x, y - 8), 3)
                
        elif nome_terreno == "Pântano":
            # Adiciona manchas de líquido tóxico
            for _ in range(2):
                x = random.randint(3, tamanho_celula - 4)
                y = random.randint(3, tamanho_celula - 4)
                raio = random.randint(1, 3)
                cor = (120, 160, 40)  # Verde amarelado
                pygame.draw.circle(textura, cor, (x, y), raio)import pygame
import math
import random

class TerrenoRenderer:
    """
    Classe para renderizar terrenos com efeitos visuais adicionais 
    para tornar o mapa mais visualmente atraente
    """
    def __init__(self):
        # Cache de texturas para evitar recriá-las a cada frame
        self.texturas_cache = {}
        
    def desenhar_terreno(self, superficie, terreno, rect, tamanho_celula):
        """Desenha um terreno com textura na superfície do jogo"""
        # Verificar se a textura já existe no cache
        key = (terreno.nome, tamanho_celula)
        
        if key in self.texturas_cache:
            textura = self.texturas_cache[key]
        else:
            # Criar uma nova textura
            textura = pygame.Surface((tamanho_celula, tamanho_celula))
            
            # Preencher com a cor base
            textura.fill(terreno.cor)
            
            # Adicionar alguns detalhes com base no tipo
            self._adicionar_detalhes(textura, terreno, tamanho_celula)
            
            # Armazenar no cache
            self.texturas_cache[key] = textura
        
        # Desenhar a textura na posição especificada
        superficie.blit(textura, rect)
    
    def limpar_cache(self):
        """Limpa o cache de texturas para liberar memória"""
        self.texturas_cache.clear()

# Importação no final para evitar importação circular
import random