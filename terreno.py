import pygame
import random

class Terreno:
    """Classe base para todos os tipos de terreno"""
    def __init__(self, cor=(100, 100, 100), modificador_velocidade=1.0, nome="Terreno Base"):
        self.cor = cor
        self.modificador_velocidade = modificador_velocidade
        self.nome = nome
    
    def efeito_movimento(self, criatura):
        """Aplica o efeito do terreno no movimento da criatura"""
        return self.modificador_velocidade
    
    def efeito_energia(self, criatura):
        """Aplica o efeito do terreno na energia da criatura"""
        return 0  # Sem efeito na energia por padrão
    
    def desenhar(self, superficie, rect):
        """Desenha o terreno na superfície"""
        pygame.draw.rect(superficie, self.cor, rect)


class Grama(Terreno):
    """Terreno padrão - sem modificadores"""
    def __init__(self):
        super().__init__(cor=(100, 180, 100), modificador_velocidade=1.0, nome="Grama")


class Lama(Terreno):
    """Terreno que diminui a velocidade"""
    def __init__(self):
        super().__init__(cor=(139, 69, 19), modificador_velocidade=0.6, nome="Lama")
    
    def efeito_energia(self, criatura):
        # A lama consome mais energia para se mover
        return -0.05


class Gelo(Terreno):
    """Terreno escorregadio que aumenta a velocidade mas reduz o controle"""
    def __init__(self):
        super().__init__(cor=(200, 220, 255), modificador_velocidade=1.4, nome="Gelo")
    
    def efeito_movimento(self, criatura):
        # No gelo, as criaturas têm 30% de chance de manter a direção atual
        if random.random() < 0.3:
            # Mantém a direção atual (não permite mudar)
            criatura.direção_bloqueada = True
        else:
            criatura.direção_bloqueada = False
        
        return self.modificador_velocidade


class Agua(Terreno):
    """Terreno aquático que exige capacidade de natação"""
    def __init__(self):
        super().__init__(cor=(64, 164, 223), modificador_velocidade=0.0, nome="Água")
    
    def efeito_movimento(self, criatura):
        # Se a criatura não tiver velocidade de nado, não consegue se mover na água
        if not hasattr(criatura, "velocidade_nado") or criatura.velocidade_nado <= 0:
            return 0.05  # Quase imóvel, "afundando"
        
        # Usa a velocidade de nado como modificador principal
        return criatura.velocidade_nado
    
    def efeito_energia(self, criatura):
        # Criaturas sem velocidade de nado perdem muita energia (afogamento)
        if not hasattr(criatura, "velocidade_nado") or criatura.velocidade_nado <= 0:
            return -0.5  # Perda rápida de energia
        
        # Criaturas com baixa velocidade de nado ainda perdem energia
        if criatura.velocidade_nado < 0.5:
            return -0.2
        
        # Criaturas adaptadas gastam energia normal
        return -0.05


class Deserto(Terreno):
    """Terreno com pouca comida e alto gasto de energia"""
    def __init__(self):
        super().__init__(cor=(237, 201, 175), modificador_velocidade=0.9, nome="Deserto")
    
    def efeito_energia(self, criatura):
        # O deserto consome mais energia devido ao calor
        return -0.15


class Montanha(Terreno):
    """Terreno difícil de atravessar"""
    def __init__(self):
        super().__init__(cor=(120, 120, 120), modificador_velocidade=0.5, nome="Montanha")
    
    def efeito_energia(self, criatura):
        # Montanhas consomem muita energia para escalar
        return -0.2


class Floresta(Terreno):
    """Terreno com muitos recursos mas movimento reduzido"""
    def __init__(self):
        super().__init__(cor=(34, 139, 34), modificador_velocidade=0.8, nome="Floresta")
    
    def efeito_energia(self, criatura):
        # Florestas têm mais comida, então recuperam um pouco de energia
        return 0.05


class Pantano(Terreno):
    """Terreno tóxico que drena energia"""
    def __init__(self):
        super().__init__(cor=(75, 110, 68), modificador_velocidade=0.7, nome="Pântano")
    
    def efeito_energia(self, criatura):
        # Pântanos são tóxicos e drenam energia
        return -0.3