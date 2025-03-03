import pygame
import random
import math
from criatura_base import CriaturaBase
from predador import Predador

class Canibal(CriaturaBase):
    """Classe para predadores evoluídos que podem caçar outros predadores"""
    
    def __init__(self, x=None, y=None, velocidade=None, stamina=None, tamanho=None, campo=None, velocidade_nado=None, pai=None, WIDTH=800, HEIGHT=600):
        # Inicializar a classe base primeiro
        super().__init__(x, y, velocidade, stamina, None, tamanho, velocidade_nado, pai, WIDTH, HEIGHT)
        
        # Atributos específicos para canibais
        if pai and isinstance(pai, Canibal):
            # Herança de atributos já aconteceu no construtor da classe base
            self.energia = self.stamina
            pass  # As mutações já foram aplicadas na classe base
        else:
            # Atributos para canibais novos
            self.velocidade = velocidade if velocidade is not None else random.uniform(3, 5)
            self.stamina = stamina if stamina is not None else random.uniform(120 *self.tamanho, 210* self.tamanho)
            self.tamanho = tamanho if tamanho is not None else random.uniform(9, 14)
            self.campo_visao = campo if campo is not None else random.uniform(self.tamanho *10, self.tamanho*15)   # Campo de visão maior que presas

            self.energia = self.stamina

            # Canibais vivem mais
            self.longevidade = random.uniform(300, 600) 
            
            # Canibais são mais adaptáveis à água
            if velocidade_nado is None:
                # Canibais são mais adaptáveis, maior chance de habilidade de nado
                self.velocidade_nado = 0
                if random.random() < 0.25:  # 25% de chance
                    self.velocidade_nado = random.uniform(0.5, 1.2)
        
        # Status dinâmicos específicos de canibais
        self.tempo_cacar = 0
        self.alvo = None
        
        # Inverso da relação entre velocidade terrestre e aquática
        # (quanto mais adaptado à água, menos adaptado ao terreno seco)
        if self.velocidade_nado > 0:
            # Penalidade na velocidade terrestre proporcional à adaptação aquática
            # Canibais são mais adaptáveis, então a penalidade é menor
            self.velocidade *= max(0.4, 1 - (self.velocidade_nado * 0.4))
        
        # Consumo de energia (mais eficiente que predadores normais devido à dieta variada)
        self.consumo_energia = 0.015 + (self.velocidade / 12) + (self.tamanho/50) + (self.campo_visao / 1000) 
        
        # Calcular cor baseada nos atributos
        self._calcular_cor()
    
    def _calcular_cor(self):
        """Define a cor baseada nos atributos do canibal"""
        # Cálculo da cor baseada nos atributos (vermelho mais forte para canibais)
        r = 255  # Vermelho máximo para canibais
        # Componente azul baseado na velocidade
        b = min(255, int(self.velocidade * 30))
        # Componente verde baseado na stamina
        g = min(80, int(self.stamina / 6))
        
        # Adiciona mais azul para canibais com alta velocidade de nado
        if self.velocidade_nado > 0:
            b = min(255, b + int(self.velocidade_nado * 60))
            # Reduz levemente o vermelho para dar aparência mais aquática
            r = max(200, r - int(self.velocidade_nado * 30))
        
        self.cor = (r, g, b)
    
    def atualizar(self, criaturas, predadores, mapa=None):
        # Chamar o método base primeiro para verificações de vida e energia
        if not super().atualizar(mapa=mapa):
            return False  # Morreu de velhice ou fome
        
        # Se não estiver com direção bloqueada pelo terreno
        if not self.direção_bloqueada:
            # Se já está caçando um alvo
            if self.alvo:
                # Verificar se o alvo ainda existe
                alvo_existe = False
                
                # O alvo pode ser uma criatura ou outro predador
                if hasattr(self.alvo, 'id'):  # Se o alvo tem um ID
                    # Verificar se é uma criatura
                    for criatura in criaturas:
                        if criatura.id == self.alvo.id:
                            self.alvo = criatura  # Atualizar referência
                            alvo_existe = True
                            break
                    
                    # Se não encontrou nas criaturas, procurar nos predadores
                    if not alvo_existe and predadores and self.energia< 0.5 *self.stamina:
                        for predador in predadores:
                            if predador.id == self.alvo.id and predador.id != self.id:  # Não perseguir a si mesmo
                                self.alvo = predador  # Atualizar referência
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
                # Decidir se vai caçar predadores ou criaturas (60% de chance de escolher predadores)
                if predadores and random.random() < 0.6 and self.energia < 0.3*self.stamina:
                    presa = self._encontrar_predador_alvo(predadores)
                    if presa:
                        self.alvo = presa
                        self.tempo_cacar = 200
                    else:
                        # Se não encontrou predador, procurar criatura
                        presa = self._encontrar_presa(criaturas)
                        if presa:
                            self.alvo = presa
                            self.tempo_cacar = 200
                        else:
                            self._movimento_aleatorio()
                else:
                    # Procurar criatura primeiro
                    presa = self._encontrar_presa(criaturas)
                    if presa:
                        self.alvo = presa
                        self.tempo_cacar = 200  # Caçar por 200 frames (≈3.3 segundos a 60 FPS)
                    else:
                        # Se não encontrou criatura e houver predadores, tentar caçar predador
                        if predadores and self.energia < self.stamina*0.3:
                            presa = self._encontrar_predador_alvo(predadores)
                            if presa:
                                self.alvo = presa
                                self.tempo_cacar = 200
                            else:
                                self._movimento_aleatorio()
                        else:
                            self._movimento_aleatorio()
        
        # Aplicar efeitos do terreno se houver mapa
        if mapa:
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
        self.direção_bloqueada = False
        
        # Tentar comer alguma criatura ou predador
        if self._cacar(criaturas, predadores):
            # Se conseguiu caçar, tenta reproduzir
            self._reproduzir(predadores)
        
        return True  # Continua vivo
    
    def _encontrar_presa(self, criaturas):
        """Encontra uma presa potencial dentro do campo de visão"""
        if not criaturas:
            return None
        
        # Filtrar criaturas que estão dentro do campo de visão
        presas_proximas = [c for c in criaturas if self._calcular_distancia(c) < self.campo_visao]
        
        if not presas_proximas:
            return None
        
        # Escolher uma presa aleatória entre as próximas
        return random.choice(presas_proximas)
    
    def _encontrar_predador_alvo(self, predadores):
        """Encontra um predador para caçar dentro do campo de visão"""
        if not predadores:
            return None
        
        # Filtrar predadores que estão dentro do campo de visão e não incluir a si mesmo
        predadores_proximos = [p for p in predadores if p.id != self.id and self._calcular_distancia(p) < self.campo_visao]
        
        if not predadores_proximos:
            return None
        
            # Escolher um predador aleatório para caçar
        return random.choice(predadores_proximos)
    def _perseguir_alvo(self):
        """Direciona o canibal em direção ao alvo"""
        dx = self.alvo.x - self.x
        dy = self.alvo.y - self.y
        self.direcao = math.atan2(dy, dx)
    
    def _movimento_aleatorio(self):
        """Faz o canibal se mover aleatoriamente"""
        if random.random() < 0.03:  # 3% de chance de mudar de direção
            self.direcao = random.uniform(0, 2 * math.pi)
    
    def _cacar(self, criaturas, predadores):
        """Tenta capturar e comer uma presa ou outro predador"""
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
        
        # Tentar comer outros predadores
        if predadores and self.energia < self.stamina*0.3:
            for i, predador in enumerate(predadores):
                if predador.id != self.id and self._calcular_distancia(predador) < self.tamanho + predador.tamanho:
                    # Ganhar energia proporcional ao tamanho do predador (bônus por ser predador)
                    ganho_energia = predador.tamanho * 8 + predador.energia * 0.7
                    self.energia += ganho_energia
                    self.energia = min(self.energia, self.stamina)  # Limitar à stamina máxima
                    
                    # Remover o predador comido
                    predadores.pop(i)
                    
                    # Resetar alvo
                    self.alvo = None
                    self.tempo_cacar = 0
                    return True
        
        return False
        
    def _reproduzir(self, predadores):
        """Tenta reproduzir se tiver energia suficiente"""
        # Só reproduz se tiver energia suficiente
        custo_reproducao = self.stamina * 0.15  
        
        if self.energia > custo_reproducao and self.idade > 50:
            if random.random() < 0.01 * self.tamanho:  # 0.4% de chance de reproduzir a cada frame (mais raro)
                # Gastar energia para reproduzir
                self.energia -= custo_reproducao
                self.filhos += 1
                
                # Criar filho próximo ao pai
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
                
                filho = Canibal(
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
        """Desenha o corpo do canibal com características distintas"""
        # Desenhar corpo do canibal
        pygame.draw.circle(superficie, cor_ajustada, (pos_x, pos_y), int(self.tamanho))
        
        # Desenhar contorno (vermelho mais intenso para canibais)
        cor_contorno = (255, 0, 0)
        pygame.draw.circle(superficie, cor_contorno, (pos_x, pos_y), int(self.tamanho), 1)
        
        # Desenhar "olhos" na direção do movimento (canibais têm olhos mais brilhantes)
        olho_x = pos_x + math.cos(self.direcao) * (self.tamanho * 0.6)
        olho_y = pos_y + math.sin(self.direcao) * (self.tamanho * 0.6)
        cor_olho = (255, 255, 0)  # Olhos amarelos brilhantes
        pygame.draw.circle(superficie, cor_olho, (int(olho_x), int(olho_y)), max(2, int(self.tamanho / 2.5)))
    
    def desenhar(self, superficie):
        """Sobrescreve o método de desenho para incluir o campo de visão específico do canibal"""
        # Desenhar campo de visão como um círculo transparente
        s = pygame.Surface((self.campo_visao*2, self.campo_visao*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 0, 0, 15), (self.campo_visao, self.campo_visao), self.campo_visao)
        superficie.blit(s, (int(self.x - self.campo_visao), int(self.y - self.campo_visao)))
        
        # Ajustar cor baseada na idade (fica mais clara conforme envelhece)
        idade_rel = min(1.0, self.idade / self.longevidade)
        cor_ajustada = (
            min(255, self.cor[0]),
            min(255, self.cor[1] + int(40 * idade_rel)),
            min(255, self.cor[2] + int(40 * idade_rel))
        )
        
        # Desenhar corpo do canibal
        self._desenhar_corpo(superficie, int(self.x), int(self.y), cor_ajustada)
        
        # Desenhar barra de energia
        max_barra = 20
        comprimento_barra = max(1, int((self.energia / self.stamina) * max_barra))
        pygame.draw.rect(superficie, (255, 255, 255), (int(self.x) - max_barra//2, int(self.y) - int(self.tamanho) - 5, max_barra, 3))
        cor_barra = (255, 0, 0)  # Barra de energia vermelha mais intensa
        pygame.draw.rect(superficie, cor_barra, (int(self.x) - max_barra//2, int(self.y) - int(self.tamanho) - 5, comprimento_barra, 3))
    
    def _obter_cor_barra_energia(self):
        """Retorna a cor da barra de energia"""
        return (255, 0, 0)  # Vermelho intenso para canibais
