import pygame
import random
from terreno import Grama, Lama, Gelo, Agua, Deserto, Montanha, Floresta, Pantano
from parede import Parede

class Mapa:
    """Gerencia o mapa do jogo, incluindo terrenos e paredes"""
    def __init__(self, largura, altura, tamanho_celula=20):
        self.largura = largura
        self.altura = altura
        self.tamanho_celula = tamanho_celula
        
        # Calcula o número de células na grade
        self.celulas_x = largura // tamanho_celula
        self.celulas_y = altura // tamanho_celula
        
        # Inicializa a grade de terrenos com grama (padrão)
        self.terrenos = [[Grama() for _ in range(self.celulas_y)] for _ in range(self.celulas_x)]
        
        # Lista de paredes
        self.paredes = []
    
    def obter_terreno(self, x, y):
        """Retorna o terreno na posição (x, y)"""
        # Converte posição para índices da grade
        ix = min(max(0, int(x // self.tamanho_celula)), self.celulas_x - 1)
        iy = min(max(0, int(y // self.tamanho_celula)), self.celulas_y - 1)
        return self.terrenos[ix][iy]
    
    def definir_terreno(self, x, y, terreno):
        """Define o terreno na posição (x, y)"""
        ix = min(max(0, int(x // self.tamanho_celula)), self.celulas_x - 1)
        iy = min(max(0, int(y // self.tamanho_celula)), self.celulas_y - 1)
        self.terrenos[ix][iy] = terreno
    
    def criar_terreno_aleatorio(self, probabilidades=None):
        """Cria um mapa com terrenos aleatórios baseado nas probabilidades fornecidas"""
        if probabilidades is None:
            # Probabilidades padrão para cada tipo de terreno
            probabilidades = {
                Grama: 0.4,
                Lama: 0.1,
                Gelo: 0.1,
                Agua: 0.1,
                Deserto: 0.1,
                Montanha: 0.05,
                Floresta: 0.1,
                Pantano: 0.05
            }
        
        tipos_terreno = list(probabilidades.keys())
        pesos = list(probabilidades.values())
        
        # Aplica terreno aleatório por célula com agrupamento natural
        self._gerar_terreno_perlin(tipos_terreno, pesos)
    
    def _gerar_terreno_perlin(self, tipos_terreno, pesos):
        """Gera terreno usando simplificação de ruído Perlin para criar regiões naturais"""
        # Cria uma grade grosseira primeiro (para gerar grandes regiões)
        escala = 8  # Quanto maior, mais suaves e maiores as regiões
        grade_grosseira = []
        
        for x in range((self.celulas_x // escala) + 1):
            linha = []
            for y in range((self.celulas_y // escala) + 1):
                tipo_terreno = random.choices(tipos_terreno, weights=pesos)[0]
                linha.append(tipo_terreno)
            grade_grosseira.append(linha)
        
        # Interpola para criar a grade completa
        for x in range(self.celulas_x):
            for y in range(self.celulas_y):
                # Encontra as células da grade grosseira que envolvem este ponto
                gx = x / escala
                gy = y / escala
                
                # Índices da grade grosseira
                gx0 = int(gx)
                gy0 = int(gy)
                gx1 = min(gx0 + 1, len(grade_grosseira) - 1)
                gy1 = min(gy0 + 1, len(grade_grosseira[0]) - 1)
                
                # Pesos de interpolação
                wx = gx - gx0
                wy = gy - gy0
                
                # Determina o tipo de terreno com base na maior influência dos vizinhos
                # e uma chance aleatória para criar transições mais naturais
                vizinhos = [
                    grade_grosseira[gx0][gy0],
                    grade_grosseira[gx0][gy1],
                    grade_grosseira[gx1][gy0],
                    grade_grosseira[gx1][gy1]
                ]
                
                # Seleciona aleatoriamente entre os vizinhos, com maior chance para o mais próximo
                pesos_vizinhos = [
                    (1 - wx) * (1 - wy) * 4,  # gx0, gy0
                    (1 - wx) * wy * 4,       # gx0, gy1
                    wx * (1 - wy) * 4,       # gx1, gy0
                    wx * wy * 4              # gx1, gy1
                ]
                
                # Adiciona aleatoriedade
                if random.random() < 0.15:  # 15% de chance de selecionar um tipo aleatório
                    self.terrenos[x][y] = random.choices(tipos_terreno, weights=pesos)[0]()
                else:
                    terreno_escolhido = random.choices(vizinhos, weights=pesos_vizinhos)[0]
                    self.terrenos[x][y] = terreno_escolhido()
    
    def adicionar_parede(self, x, y, largura, altura):
        """Adiciona uma parede ao mapa"""
        self.paredes.append(Parede(x, y, largura, altura))
    
    def verificar_colisao_paredes(self, entidade):
        """Verifica e resolve colisões da entidade com todas as paredes"""
        for parede in self.paredes:
            if parede.colidir(entidade.x, entidade.y, entidade.tamanho):
                parede.resolver_colisao(entidade)
                return True
        return False
    
    def aplicar_efeitos_terreno(self, entidade):
        """Aplica os efeitos do terreno atual na entidade"""
        terreno = self.obter_terreno(entidade.x, entidade.y)
        
        # Aplica modificador de velocidade
        entidade.velocidade_atual = entidade.velocidade * terreno.efeito_movimento(entidade)
        
        # Aplica efeito na energia
        entidade.energia += terreno.efeito_energia(entidade)
    
    def desenhar(self, superficie):
        """Desenha o mapa na superfície"""
        # Desenha os terrenos
        for x in range(self.celulas_x):
            for y in range(self.celulas_y):
                rect = pygame.Rect(
                    x * self.tamanho_celula,
                    y * self.tamanho_celula,
                    self.tamanho_celula,
                    self.tamanho_celula
                )
                
                # Verificar se o renderizador está disponível
                if hasattr(self, 'renderer') and self.renderer is not None:
                    # Usa o renderizador para desenhar texturas melhoradas
                    self.renderer.desenhar_terreno(superficie, self.terrenos[x][y], rect, self.tamanho_celula)
                else:
                    # Fallback para desenho direto se o renderizador não estiver disponível
                    self.terrenos[x][y].desenhar(superficie, rect)
        
        # Desenha as paredes
        for parede in self.paredes:
            parede.desenhar(superficie)
    
    def criar_mapa_predefinido(self, tipo, percentuais_personalizados=None):
        """Cria um mapa predefinido com base no tipo escolhido"""
        if tipo == "planicie":
            self._criar_mapa_planicie()
        elif tipo == "ilha":
            self._criar_mapa_ilha()
        elif tipo == "labirinto":
            self._criar_mapa_labirinto()
        elif tipo == "montanhoso":
            self._criar_mapa_montanhoso()
        elif tipo == "diversificado":
            self._criar_mapa_diversificado()
        elif tipo == "personalizado" and percentuais_personalizados:
            self.criar_terreno_personalizado(percentuais_personalizados)
        else:
            # Mapa aleatório padrão
            self.criar_terreno_aleatorio()
    
    def _criar_mapa_planicie(self):
        """Cria um mapa de planície com algumas áreas específicas"""
        # Reinicia o mapa com grama
        self.terrenos = [[Grama() for _ in range(self.celulas_y)] for _ in range(self.celulas_x)]
        
        # Adiciona algumas áreas de floresta
        self._criar_area_circular(self.largura//4, self.altura//4, 100, Floresta)
        self._criar_area_circular(self.largura*3//4, self.altura*3//4, 80, Floresta)
        
        # Adiciona um rio
        largura_rio = 40
        for y in range(self.celulas_y):
            centro_x = self.celulas_x // 2 + int(10 * math.sin(y / 10))
            for x in range(max(0, centro_x - largura_rio//self.tamanho_celula), 
                          min(self.celulas_x, centro_x + largura_rio//self.tamanho_celula)):
                self.terrenos[x][y] = Agua()
        
        # Adiciona algumas paredes como rochas
        for _ in range(10):
            x = random.randint(0, self.largura - 30)
            y = random.randint(0, self.altura - 30)
            tamanho = random.randint(15, 40)
            self.adicionar_parede(x, y, tamanho, tamanho)
    
    def _criar_mapa_ilha(self):
        """Cria um mapa de ilha cercada por água"""
        # Preenche tudo com água primeiro
        self.terrenos = [[Agua() for _ in range(self.celulas_y)] for _ in range(self.celulas_x)]
        
        # Cria uma ilha central
        centro_x = self.largura // 2
        centro_y = self.altura // 2
        raio_ilha = min(self.largura, self.altura) * 0.4
        
        # Cria a ilha com terrenos variados
        self._criar_area_circular(centro_x, centro_y, raio_ilha, Grama)
        self._criar_area_circular(centro_x - raio_ilha//3, centro_y - raio_ilha//3, raio_ilha//3, Floresta)
        self._criar_area_circular(centro_x + raio_ilha//2, centro_y, raio_ilha//4, Montanha)
        self._criar_area_circular(centro_x, centro_y + raio_ilha//2, raio_ilha//5, Pantano)
        
        # Adiciona algumas paredes como pedras na água
        for _ in range(15):
            angulo = random.uniform(0, 2 * math.pi)
            distancia = random.uniform(raio_ilha * 1.1, raio_ilha * 1.5)
            x = centro_x + int(math.cos(angulo) * distancia)
            y = centro_y + int(math.sin(angulo) * distancia)
            
            if 0 <= x < self.largura - 20 and 0 <= y < self.altura - 20:
                tamanho = random.randint(15, 30)
                self.adicionar_parede(x, y, tamanho, tamanho)
    
    def _criar_mapa_labirinto(self):
        """Cria um mapa de labirinto com paredes"""
        # Reinicia o mapa com grama
        self.terrenos = [[Grama() for _ in range(self.celulas_y)] for _ in range(self.celulas_x)]
        
        # Cria paredes do labirinto
        espessura_parede = 10
        espacamento = 100
        
        # Paredes horizontais
        for y in range(espacamento, self.altura, espacamento):
            abertura = random.randint(0, self.largura - espacamento)
            self.adicionar_parede(0, y, abertura, espessura_parede)
            self.adicionar_parede(abertura + espacamento, y, 
                                self.largura - abertura - espacamento, espessura_parede)
        
        # Paredes verticais
        for x in range(espacamento, self.largura, espacamento):
            abertura = random.randint(0, self.altura - espacamento)
            self.adicionar_parede(x, 0, espessura_parede, abertura)
            self.adicionar_parede(x, abertura + espacamento, 
                                espessura_parede, self.altura - abertura - espacamento)
        
        # Adiciona áreas de diferentes terrenos
        num_areas = random.randint(5, 10)
        for _ in range(num_areas):
            x = random.randint(50, self.largura - 50)
            y = random.randint(50, self.altura - 50)
            raio = random.randint(30, 60)
            terreno = random.choice([Lama, Gelo, Pantano, Deserto])
            self._criar_area_circular(x, y, raio, terreno)
    
    def _criar_mapa_montanhoso(self):
        """Cria um mapa montanhoso com muitos obstáculos e terrenos variados"""
        # Base de montanhas
        self.terrenos = [[Montanha() for _ in range(self.celulas_y)] for _ in range(self.celulas_x)]
        
        # Cria vários vales (áreas de grama)
        num_vales = random.randint(3, 6)
        for _ in range(num_vales):
            x = random.randint(50, self.largura - 50)
            y = random.randint(50, self.altura - 50)
            raio = random.randint(60, 120)
            self._criar_area_circular(x, y, raio, Grama)
        
        # Adiciona lagos
        num_lagos = random.randint(2, 4)
        for _ in range(num_lagos):
            x = random.randint(50, self.largura - 50)
            y = random.randint(50, self.altura - 50)
            raio = random.randint(30, 70)
            self._criar_area_circular(x, y, raio, Agua)
        
        # Adiciona desertos
        num_desertos = random.randint(1, 3)
        for _ in range(num_desertos):
            x = random.randint(50, self.largura - 50)
            y = random.randint(50, self.altura - 50)
            raio = random.randint(40, 80)
            self._criar_area_circular(x, y, raio, Deserto)
        
        # Adiciona muitas paredes como picos montanhosos
        num_picos = random.randint(20, 40)
        for _ in range(num_picos):
            x = random.randint(0, self.largura - 30)
            y = random.randint(0, self.altura - 30)
            largura = random.randint(10, 40)
            altura = random.randint(10, 40)
            self.adicionar_parede(x, y, largura, altura)
    
    def _criar_mapa_diversificado(self):
        """Cria um mapa altamente diversificado com todos os tipos de terreno"""
        # Cria um mapa completamente aleatório primeiro
        self.criar_terreno_aleatorio()
        
        # Garante que todos os tipos de terreno estejam presentes
        terrenos = [Grama(), Lama(), Gelo(), Agua(), Deserto(), Montanha(), Floresta(), Pantano()]
        
        # Cria áreas de cada tipo
        raio_base = min(self.largura, self.altura) / 8
        posicoes_x = [self.largura/4, self.largura*3/4, self.largura/4, self.largura*3/4,
                     self.largura/6, self.largura*5/6, self.largura/2, self.largura/2]
        posicoes_y = [self.altura/4, self.altura/4, self.altura*3/4, self.altura*3/4,
                     self.altura/2, self.altura/2, self.altura/6, self.altura*5/6]
        
        for i in range(len(terrenos)):
            tipo_terreno = type(terrenos[i])
            raio = int(raio_base * (0.7 + random.random() * 0.6))
            self._criar_area_circular(int(posicoes_x[i]), int(posicoes_y[i]), raio, tipo_terreno)
        
        # Adiciona algumas paredes espalhadas
        num_paredes = random.randint(10, 20)
        for _ in range(num_paredes):
            x = random.randint(0, self.largura - 30)
            y = random.randint(0, self.altura - 30)
            largura = random.randint(15, 50)
            altura = random.randint(15, 50)
            self.adicionar_parede(x, y, largura, altura)
    
    def _criar_area_circular(self, centro_x, centro_y, raio, tipo_terreno):
        """Cria uma área circular de um determinado tipo de terreno"""
        # Determina os limites da área a verificar
        x_min = max(0, (centro_x - raio) // self.tamanho_celula)
        x_max = min(self.celulas_x, (centro_x + raio) // self.tamanho_celula + 1)
        y_min = max(0, (centro_y - raio) // self.tamanho_celula)
        y_max = min(self.celulas_y, (centro_y + raio) // self.tamanho_celula + 1)
        
        # Para cada célula na região
        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                # Calcula o centro da célula
                cell_centro_x = (x * self.tamanho_celula) + (self.tamanho_celula / 2)
                cell_centro_y = (y * self.tamanho_celula) + (self.tamanho_celula / 2)
                
                # Calcula a distância ao centro da área
                dx = cell_centro_x - centro_x
                dy = cell_centro_y - centro_y
                distancia = (dx**2 + dy**2)**0.5
                
                # Se a distância for menor que o raio, define o terreno
                if distancia < raio:
                    # Borda suave (mistura com terrenos existentes perto da borda)
                    if distancia > raio * 0.8 and random.random() < 0.5:
                        continue
                    
                    self.terrenos[x][y] = tipo_terreno()

# Adicionando a importação de math que estava faltando
import math