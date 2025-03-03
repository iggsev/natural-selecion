import random
import math
import pygame
from criatura_base import CriaturaBase

class Criatura(CriaturaBase):
    """Classe para criaturas herbívoras (presas)"""
    
    def __init__(self, x=None, y=None, velocidade=None, stamina=None, longevidade=None, 
                tamanho=None, velocidade_nado=None, comunicacao=None, 
                tipo_comunicacao=None, forma=None, pai=None, WIDTH=800, HEIGHT=600):
        # Inicializar a classe base primeiro
        super().__init__(x, y, velocidade, stamina, longevidade, tamanho, velocidade_nado, pai, WIDTH, HEIGHT)
        
        # Atributos específicos das presas
        if pai and isinstance(pai, Criatura):
            # Taxa de mutação (porcentagem de variação)
            mutacao = 0.2
            
            # Herda comunicação com mutação
            self.comunicacao = max(1, pai.comunicacao * random.uniform(1 - mutacao, 1 + mutacao))

            self.tipo_comunicacao = pai.tipo_comunicacao
            self.forma = pai.forma
            
            # 10% de chance de mutar o tipo de comunicação na reprodução
            if random.random() < 0.1:
                if self.comunicacao > 3:  # Se tiver comunicação alta
                    self.tipo_comunicacao = random.choice(["egoista", "altruista"])
                    # Forma baseada no tipo de comunicação
                    self.forma = "quadrado" if self.tipo_comunicacao == "egoista" else "triangulo"
                else:
                    self.tipo_comunicacao = "nenhuma"
                    self.forma = "circulo"
        else:
            # Atributos iniciais para criaturas novas
            self.comunicacao = comunicacao if comunicacao is not None else random.uniform(1.0, 5.0)
            
            # Tipo de comunicação e forma
            if tipo_comunicacao is not None:
                self.tipo_comunicacao = tipo_comunicacao
            elif self.comunicacao > 3:  # Se tiver comunicação alta
                self.tipo_comunicacao = random.choice(["egoista", "altruista"])
            else:
                self.tipo_comunicacao = "nenhuma"
            
            # Forma baseada no tipo de comunicação
            if forma is not None:
                self.forma = forma
            elif self.tipo_comunicacao == "egoista":
                self.forma = "quadrado"
            elif self.tipo_comunicacao == "altruista":
                self.forma = "triangulo"
            else:
                self.forma = "circulo"
        
        # Status específicos de criaturas
        self.tempo_descanso = 0
        self.ultimo_alimento = 0
        self.campo_visao = self.tamanho * 10 + self.comunicacao * 5  # Campo de visão baseado no tamanho e comunicação
        self.predadores_detectados = []  # Lista de predadores que esta criatura detectou
        self.alertada = False  # Indica se foi alertada por outras criaturas
        self.tempo_alerta = 0  # Duração do alerta
        self.direcao_fuga = None  # Direção de fuga compartilhada
        
        # Penalidades baseadas nos atributos
        self.consumo_energia = 0.15 + (self.velocidade / 15) + (self.tamanho / 200) + (self.comunicacao / 50)
        self.custo_reproducao = self.stamina * 0.25  # 25% da stamina para reproduzir
        
        # Calcular cor baseada nos atributos
        self._calcular_cor()
    
    def _calcular_cor(self):
        # Componente vermelho é baixo para presas
        r = 100
        # Componente verde baseado na stamina
        g = min(255, int(self.stamina / 1.2))
        # Componente azul baseado na velocidade
        b = min(255, int(self.velocidade * 70))
        
        # Adiciona mais azul para criaturas com alta velocidade de nado
        if self.velocidade_nado > 0:
            b = min(255, b + int(self.velocidade_nado * 100))
            # Reduz vermelho para dar aparência mais aquática
            r = max(50, r - int(self.velocidade_nado * 50))
        
        self.cor = (r, g, b)
    
    def atualizar(self, alimentos, criaturas, predadores, mapa=None):
        # Chamar o método base primeiro para verificações de vida e energia
        if not super().atualizar(mapa=mapa):
            return False  # Morreu de velhice ou fome
            
        # Se estiver descansando, diminuir o tempo de descanso
        if self.tempo_descanso > 0:
            self.tempo_descanso -= 1
            self.energia += self.stamina * 0.01  # Recupera energia ao descansar
            self.energia = min(self.energia, self.stamina)  # Limitar à stamina máxima
            return True
        
        # Diminuir tempo de alerta
        if self.tempo_alerta > 0:
            self.tempo_alerta -= 1
            if self.tempo_alerta == 0:
                self.alertada = False
                self.direcao_fuga = None
        
        # Detectar predadores no campo de visão
        self.predadores_detectados = []
        for predador in predadores:
            if self._calcular_distancia(predador) < self.campo_visao:
                self.predadores_detectados.append(predador)
                
        # Comunicar alerta a outras presas se tiver capacidade de comunicação
        if self.comunicacao > 3 and len(self.predadores_detectados) > 0:
            self._alertar_outras_presas(criaturas)
            
        # Decidir próxima ação (se não estiver com direção bloqueada pelo terreno)
        if not self.direção_bloqueada:
            # Verificar se está perto de uma parede e evitar se necessário
            if mapa and self._esta_perto_de_parede(mapa):
                self._evitar_parede(mapa)
            # Verificar se está em água e não sabe nadar
            elif mapa and self.esta_nadando and self.velocidade_nado <= 0:
                # Prioridade máxima: sair da água a qualquer custo
                # Encontrar a terra mais próxima
                self._buscar_saida_agua(mapa)
            elif self.alertada and self.direcao_fuga is not None:
                # Se foi alertada, usar a direção de fuga compartilhada
                self.direcao = self.direcao_fuga
            elif len(self.predadores_detectados) > 0:
                # Fugir do predador mais próximo
                predador_proximo = min(self.predadores_detectados, key=lambda p: self._calcular_distancia(p))
                self._fugir_de_predador(predador_proximo)
                # Esta criatura agora está em alerta
                self.alertada = True
                self.tempo_alerta = 60  # 1 segundo de alerta (60 frames)
            else:
                # Se não há predadores, procurar comida
                alimento_proximo = self._alimento_mais_proximo(alimentos, mapa)
                if alimento_proximo:
                    self._buscar_alimento(alimento_proximo)
                else:
                    # Movimento aleatório se não houver alimento
                    if random.random() < 0.05:  # 5% de chance de mudar de direção
                        self.direcao = random.uniform(0, 2 * math.pi)
        
        # Aplicar efeitos do terreno se houver mapa
        if mapa:
            mapa.aplicar_efeitos_terreno(self)
        
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
        
        # Verificar se pode comer algum alimento
        self._comer(alimentos)
        
        # Tentar reproduzir
        self._reproduzir(criaturas)
    
        return True  # Continua vivo
    
    def _buscar_saida_agua(self, mapa):
        """Tenta encontrar e se mover em direção à terra mais próxima"""
        # Verificar em várias direções para encontrar terra
        direcoes_teste = 12  # Número de direções a verificar
        melhor_direcao = None
        menor_distancia = float('inf')
        
        for i in range(direcoes_teste):
            angulo = (2 * math.pi / direcoes_teste) * i
            distancia_teste = 5  # Começa próximo
            max_distancia = 200  # Limite de busca
            
            # Continua verificando na direção até encontrar terra ou atingir o limite
            while distancia_teste < max_distancia:
                pos_x = self.x + math.cos(angulo) * distancia_teste
                pos_y = self.y + math.sin(angulo) * distancia_teste
                
                # Verificar se está dentro dos limites e se é terra
                if (0 <= pos_x < self.WIDTH and 0 <= pos_y < self.HEIGHT):
                    terreno = mapa.obter_terreno(pos_x, pos_y)
                    if terreno.nome != "Água":
                        # Encontrou terra, verificar se é a mais próxima
                        if distancia_teste < menor_distancia:
                            menor_distancia = distancia_teste
                            melhor_direcao = angulo
                        break
                
                distancia_teste += 20  # Incrementa a distância de busca
        
        # Se encontrou terra, move-se nessa direção
        if melhor_direcao is not None:
            self.direcao = melhor_direcao
        else:
            # Se não encontrou terra, move-se em uma direção aleatória
            self.direcao = random.uniform(0, 2 * math.pi)

    def _alimento_mais_proximo(self, alimentos, mapa=None):
        if not alimentos:
            return None
        
        # Filtrar alimentos para considerar apenas os que não têm água no caminho
        # e estão longe de paredes
        alimentos_seguros = []
        for alimento in alimentos:
            distancia = self._calcular_distancia(alimento)
            # Só considera comida num raio de 250px
            if distancia < 250:
                seguro = True
                
                # Verificar se há água no caminho se a criatura não sabe nadar
                if mapa and self.velocidade_nado <= 0:
                    if self._ha_agua_no_caminho(alimento.x, alimento.y, mapa):
                        seguro = False
                
                # Verificar se o alimento está perto demais de uma parede
                if mapa and seguro:
                    if self._ha_parede_no_caminho(alimento.x, alimento.y, mapa):
                        seguro = False
                
                if seguro:
                    alimentos_seguros.append(alimento)
        
        if not alimentos_seguros:
            return None
            
        # Retorna o alimento mais próximo dentre os seguros
        return min(alimentos_seguros, key=lambda a: self._calcular_distancia(a))
    
    def _buscar_alimento(self, alimento):
        # Calcular ângulo de direção para o alimento
        dx = alimento.x - self.x
        dy = alimento.y - self.y
        self.direcao = math.atan2(dy, dx)
    
    def _fugir_de_predador(self, predador):
        # Calcular ângulo na direção oposta ao predador
        dx = self.x - predador.x
        dy = self.y - predador.y
        self.direcao = math.atan2(dy, dx)
        
        # Salvar direção de fuga para comunicar a outras presas
        self.direcao_fuga = self.direcao
        
        # Gastar mais energia ao fugir (adrenalina)
        self.energia -= self.consumo_energia * 1.25
        
    def _alertar_outras_presas(self, criaturas):
        # Se não tiver direção de fuga, não pode alertar
        if self.direcao_fuga is None:
            return
            
        # Comunicar alerta a outras presas no campo de visão
        for criatura in criaturas:
            if criatura.id != self.id and self._calcular_distancia(criatura) < self.campo_visao:
                # Se for egoísta, só alerta criaturas da mesma forma
                if self.tipo_comunicacao == "egoista" and criatura.forma != self.forma:
                    continue
                    
                # Alerta a criatura e compartilha direção de fuga
                criatura.alertada = True
                criatura.tempo_alerta = 60  # 1 segundo de alerta
                criatura.direcao_fuga = self.direcao_fuga
    
    def _comer(self, alimentos):
        for i, alimento in enumerate(alimentos):
            if self._calcular_distancia(alimento) < self.tamanho + alimento.tamanho:
                # Ganhar energia proporcional ao valor nutricional
                self.energia += alimento.valor_nutricional
                self.energia = min(self.energia, self.stamina)  # Limitar à stamina máxima
                self.ultimo_alimento = 0
                
                # Remover o alimento consumido
                alimentos.pop(i)
                return True
        
        self.ultimo_alimento += 1
        return False
    
    def _reproduzir(self, criaturas):
        # Só reproduz se tiver energia suficiente e for "adulto"
        if self.energia > self.custo_reproducao and self.idade > 100 and self.ultimo_alimento < 60:
            if random.random() < 0.01 * self.tamanho: 
                # Gastar energia para reproduzir
                self.energia -= self.custo_reproducao
                self.filhos += 1
                
                # Criar filho próximo ao pai
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
                
                if random.random() < 0.99:
                    filho = Criatura(
                        x=self.x + offset_x,
                        y=self.y + offset_y,
                        pai=self,  # Aqui é onde ocorre a herança de atributos com mutação
                        WIDTH=self.WIDTH,
                        HEIGHT=self.HEIGHT
                    )
                
                    criaturas.append(filho)
                else:
                    from predador import Predador
                    novo_predador = Predador(x=self.x, y=self.y, velocidade=self.velocidade, 
                            stamina=self.stamina, tamanho=self.tamanho, 
                            velocidade_nado=self.velocidade_nado,  # Herda a velocidade de nado
                            WIDTH=self.WIDTH, HEIGHT=self.HEIGHT)
                    return False  # A criatura se transforma e "morre" como presa

                # Descansar após reproduzir
                self.tempo_descanso = 60  # 1 segundo de descanso (60 frames a 60 FPS)
                return True
        
        return False
    
    def _desenhar_corpo(self, superficie, pos_x, pos_y, cor_ajustada):
        """Desenha o corpo da criatura baseado no seu tipo de comunicação"""
        # Determinar a cor do contorno
        if self.alertada:
            cor_contorno = (255, 255, 0)  # Amarelo para alertada
        else:
            cor_contorno = (255, 255, 255)  # Branco normal
            
        # Desenhar forma baseada no tipo de comunicação
        if self.forma == "quadrado":
            # Quadrado para comunicação egoísta
            tamanho_rect = self.tamanho * 1.8
            rect = pygame.Rect(
                pos_x - tamanho_rect/2,
                pos_y - tamanho_rect/2,
                tamanho_rect,
                tamanho_rect
            )
            pygame.draw.rect(superficie, cor_ajustada, rect)
            pygame.draw.rect(superficie, cor_contorno, rect, 1)
        elif self.forma == "triangulo":
            # Triângulo para comunicação altruísta
            tamanho_tri = self.tamanho * 2
            pontos = [
                (pos_x, pos_y - tamanho_tri),
                (pos_x - tamanho_tri * 0.866, pos_y + tamanho_tri * 0.5),
                (pos_x + tamanho_tri * 0.866, pos_y + tamanho_tri * 0.5)
            ]
            pygame.draw.polygon(superficie, cor_ajustada, pontos)
            pygame.draw.polygon(superficie, cor_contorno, pontos, 1)
        else:
            # Círculo para sem comunicação
            pygame.draw.circle(superficie, cor_ajustada, (pos_x, pos_y), int(self.tamanho))
            pygame.draw.circle(superficie, cor_contorno, (pos_x, pos_y), int(self.tamanho), 1)
        
        # Desenhar "olhos" na direção do movimento
        olho_x = pos_x + math.cos(self.direcao) * (self.tamanho * 0.6)
        olho_y = pos_y + math.sin(self.direcao) * (self.tamanho * 0.6)
        
        # Ajuste nos olhos para criaturas aquáticas
        if self.velocidade_nado > 0.5:
            # Olhos maiores para criaturas aquáticas
            tamanho_olho = max(1, int(self.tamanho / 2.5))
            cor_olho = (0, 0, 0) if not self.esta_nadando else (0, 150, 200)
            pygame.draw.circle(superficie, cor_olho, (int(olho_x), int(olho_y)), tamanho_olho)
        else:
            # Olhos normais
            pygame.draw.circle(superficie, (0, 0, 0), (int(olho_x), int(olho_y)), max(1, int(self.tamanho / 3)))
        
        # Indicador visual de velocidade de nado para criaturas aquáticas
        if self.velocidade_nado > 0:
            # Desenhar pequenas barbatanas ou indicação de adaptação aquática
            # Barbatanas laterais
            barbatana_x1 = pos_x + math.cos(self.direcao + math.pi/2) * self.tamanho
            barbatana_y1 = pos_y + math.sin(self.direcao + math.pi/2) * self.tamanho
            barbatana_x2 = pos_x + math.cos(self.direcao - math.pi/2) * self.tamanho
            barbatana_y2 = pos_y + math.sin(self.direcao - math.pi/2) * self.tamanho
            
            tamanho_barbatana = self.tamanho * self.velocidade_nado * 0.7
            
            # Pontos das barbatanas
            ponta_x1 = barbatana_x1 + math.cos(self.direcao + math.pi/2) * tamanho_barbatana
            ponta_y1 = barbatana_y1 + math.sin(self.direcao + math.pi/2) * tamanho_barbatana
            ponta_x2 = barbatana_x2 + math.cos(self.direcao - math.pi/2) * tamanho_barbatana
            ponta_y2 = barbatana_y2 + math.sin(self.direcao - math.pi/2) * tamanho_barbatana
            
            # Desenhar barbatanas
            pygame.draw.line(superficie, (0, 150, 220), (barbatana_x1, barbatana_y1), (ponta_x1, ponta_y1), max(1, int(self.tamanho/4)))
            pygame.draw.line(superficie, (0, 150, 220), (barbatana_x2, barbatana_y2), (ponta_x2, ponta_y2), max(1, int(self.tamanho/4)))
    
    def desenhar(self, superficie):
        """Sobrescreve o método da classe base para campo de visão específico"""
        # Desenhar campo de visão como um círculo transparente
        if self.comunicacao > 1:
            s = pygame.Surface((self.campo_visao*2, self.campo_visao*2), pygame.SRCALPHA)
            
            # Cor do campo de visão baseada no tipo de comunicação
            if self.tipo_comunicacao == "egoista":
                cor_campo = (180, 180, 0, 10)  # Amarelo para egoísta
            elif self.tipo_comunicacao == "altruista":
                cor_campo = (0, 200, 200, 10)  # Ciano para altruísta
            else:
                cor_campo = (100, 100, 100, 5)  # Cinza para sem comunicação
                
            pygame.draw.circle(s, cor_campo, (self.campo_visao, self.campo_visao), self.campo_visao)
            superficie.blit(s, (int(self.x - self.campo_visao), int(self.y - self.campo_visao)))
        
        # Chamar o método de desenho base para os elementos comuns
        super()._desenhar_corpo(superficie, int(self.x), int(self.y), self.cor)
        
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
        
        # Desenhar corpo específico para criaturas
        self._desenhar_corpo(superficie, pos_x, pos_y, cor_ajustada)
        
        # Desenhar barra de energia
        max_barra = 20
        comprimento_barra = max(1, int((self.energia / self.stamina) * max_barra))
        pygame.draw.rect(superficie, (255, 255, 255), (pos_x - max_barra//2, pos_y - int(self.tamanho) - 5, max_barra, 3))
        pygame.draw.rect(superficie, (0, 255, 0), (pos_x - max_barra//2, pos_y - int(self.tamanho) - 5, comprimento_barra, 3))
    
    def _obter_cor_barra_energia(self):
        """Retorna a cor da barra de energia"""
        return (0, 255, 0)  # Verde para presas