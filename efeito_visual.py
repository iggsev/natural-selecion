import pygame
import random
import math

class EfeitoVisual:
    """Classe para gerenciar efeitos visuais temporários na simulação"""
    def __init__(self):
        self.efeitos = []
    
    def adicionar_particulas(self, x, y, cor, num_particulas=10, vida_max=30, velocidade=1.5, tamanho=2):
        """Adiciona um efeito de partículas"""
        for _ in range(num_particulas):
            angulo = random.uniform(0, 2 * math.pi)
            velocidade_rand = random.uniform(0.5, velocidade)
            vx = math.cos(angulo) * velocidade_rand
            vy = math.sin(angulo) * velocidade_rand
            vida = random.randint(vida_max // 2, vida_max)
            tamanho_rand = random.uniform(tamanho * 0.7, tamanho * 1.3)
            
            self.efeitos.append({
                'tipo': 'particula',
                'x': x,
                'y': y,
                'vx': vx,
                'vy': vy,
                'cor': cor,
                'vida': vida,
                'vida_max': vida,
                'tamanho': tamanho_rand
            })
    
    def adicionar_onda(self, x, y, cor, raio_max=50, espessura=2, vida_max=20):
        """Adiciona um efeito de onda circular que se expande"""
        self.efeitos.append({
            'tipo': 'onda',
            'x': x,
            'y': y,
            'cor': cor,
            'raio': 5,
            'raio_max': raio_max,
            'espessura': espessura,
            'vida': vida_max,
            'vida_max': vida_max
        })
    
    def adicionar_texto_flutuante(self, x, y, texto, cor, vida_max=40, tamanho_fonte=14):
        """Adiciona um texto flutuante que sobe e desaparece"""
        fonte = pygame.font.SysFont("Arial", tamanho_fonte)
        texto_renderizado = fonte.render(texto, True, cor)
        
        self.efeitos.append({
            'tipo': 'texto',
            'x': x,
            'y': y,
            'vy': -0.7,  # Velocidade para cima
            'texto': texto_renderizado,
            'vida': vida_max,
            'vida_max': vida_max
        })
    
    def adicionar_flash(self, x, y, cor, raio_max=30, vida_max=10):
        """Adiciona um flash de luz que aparece e desaparece rapidamente"""
        self.efeitos.append({
            'tipo': 'flash',
            'x': x,
            'y': y,
            'cor': cor,
            'raio': raio_max,
            'vida': vida_max,
            'vida_max': vida_max
        })
    
    def atualizar(self):
        """Atualiza todos os efeitos ativos"""
        # Filtrar e atualizar efeitos
        novos_efeitos = []
        
        for efeito in self.efeitos:
            # Reduzir vida
            efeito['vida'] -= 1
            
            # Pular efeitos que terminaram
            if efeito['vida'] <= 0:
                continue
            
            # Atualizar baseado no tipo
            if efeito['tipo'] == 'particula':
                # Atualizar posição
                efeito['x'] += efeito['vx']
                efeito['y'] += efeito['vy']
                
                # Adicionar gravidade para algumas partículas
                if random.random() < 0.3:
                    efeito['vy'] += 0.05
                
            elif efeito['tipo'] == 'onda':
                # Expandir raio
                efeito['raio'] += (efeito['raio_max'] - 5) / efeito['vida_max']
                
            elif efeito['tipo'] == 'texto':
                # Mover texto para cima
                efeito['y'] += efeito['vy']
                
            # Adicionar à nova lista
            novos_efeitos.append(efeito)
        
        # Atualizar lista de efeitos
        self.efeitos = novos_efeitos
    
    def desenhar(self, superficie):
        """Desenha todos os efeitos ativos"""
        for efeito in self.efeitos:
            # Calcular transparência baseada na vida restante
            alpha = int(255 * (efeito['vida'] / efeito['vida_max']))
            
            if efeito['tipo'] == 'particula':
                # Desenhar partícula com transparência
                cor = list(efeito['cor'])
                if len(cor) == 3:
                    cor.append(alpha)  # Adicionar canal alpha
                else:
                    cor[3] = alpha  # Atualizar canal alpha
                
                # Criar superfície para a partícula
                tamanho = int(efeito['tamanho'])
                part_surf = pygame.Surface((tamanho*2, tamanho*2), pygame.SRCALPHA)
                pygame.draw.circle(part_surf, tuple(cor), (tamanho, tamanho), tamanho)
                superficie.blit(part_surf, (int(efeito['x'] - tamanho), int(efeito['y'] - tamanho)))
                
            elif efeito['tipo'] == 'onda':
                # Desenhar onda com transparência
                cor = list(efeito['cor'])
                if len(cor) == 3:
                    cor.append(alpha)
                else:
                    cor[3] = alpha
                
                # Criar superfície para a onda
                tamanho = int(efeito['raio'] * 2)
                wave_surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
                pygame.draw.circle(
                    wave_surf, 
                    tuple(cor), 
                    (int(tamanho/2), int(tamanho/2)), 
                    int(efeito['raio']), 
                    int(efeito['espessura'])
                )
                superficie.blit(wave_surf, (int(efeito['x'] - efeito['raio']), int(efeito['y'] - efeito['raio'])))
                
            elif efeito['tipo'] == 'texto':
                # Aplicar transparência ao texto
                texto_surf = efeito['texto'].copy()
                texto_surf.set_alpha(alpha)
                superficie.blit(texto_surf, (int(efeito['x']), int(efeito['y'])))
                
            elif efeito['tipo'] == 'flash':
                # Desenhar flash com transparência
                cor = list(efeito['cor'])
                if len(cor) == 3:
                    cor.append(alpha)
                else:
                    cor[3] = alpha
                
                # Calcular raio baseado na vida (cresce e diminui)
                progresso = efeito['vida'] / efeito['vida_max']
                raio = efeito['raio'] * (1 - abs(2 * progresso - 1))
                
                # Criar superfície para o flash
                tamanho = int(efeito['raio'] * 2)
                flash_surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
                pygame.draw.circle(
                    flash_surf, 
                    tuple(cor), 
                    (int(tamanho/2), int(tamanho/2)), 
                    int(raio)
                )
                superficie.blit(flash_surf, (int(efeito['x'] - efeito['raio']), int(efeito['y'] - efeito['raio'])))
    
    def limpar(self):
        """Remove todos os efeitos visuais"""
        self.efeitos = []
