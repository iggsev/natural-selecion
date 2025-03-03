import pygame
import random
from criatura import Criatura
from predador import Predador
from canibal import Canibal
from alimento import Alimento
from mapa import Mapa

class Simulacao:
    def __init__(self, WIDTH=800, HEIGHT=600):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.criaturas = []
        self.predadores = []
        self.alimentos = []
        self.estatisticas = {
            'geracao': 1,
            'populacao': 0,
            'populacao_pico': 0,
            'idade_media': 0,
            'velocidade_media': 0,
            'stamina_media': 0,
            'tamanho_medio': 0,
            'total_criaturas': 0,
            'predadores_ativos': 0,
            'canibais_ativos': 0
        }
        self.tempo = 0
        self.fonte = pygame.font.SysFont("Arial", 16)
        self.fonte_titulo = pygame.font.SysFont("Arial", 24)
        self.pausa = False
        self.aceleracao = 1
        self.mapa = None
        self.taxa_alimento = 0.05  # Taxa padrão de geração de alimentos
    
    def inicializar(self, configuracoes=None):
        # Configurações padrão se não fornecidas
        if configuracoes is None:
            configuracoes = {
                'mapa': 'aleatorio',
                'n_presas': 20,
                'n_predadores': 3,
                'n_canibais': 1,
                'n_alimentos': 40,
                'taxa_alimento': 0.05
            }
        
        # Criar e inicializar o mapa
        self.mapa = Mapa(self.WIDTH, self.HEIGHT)
        self.mapa.criar_mapa_predefinido(configuracoes['mapa'])
        
        # Armazenar taxa de geração de alimentos
        self.taxa_alimento = configuracoes['taxa_alimento']
        
        # Criar criaturas iniciais
        self.criaturas = []
        for _ in range(configuracoes['n_presas']):
            # Tentar colocar a criatura em uma posição válida (sem paredes)
            criatura = self._criar_entidade_em_posicao_valida(Criatura)
            self.criaturas.append(criatura)
        
        # Criar predadores iniciais
        self.predadores = []
        for _ in range(configuracoes['n_predadores']):
            predador = self._criar_entidade_em_posicao_valida(Predador)
            self.predadores.append(predador)
        
        # Adicionar alguns canibais
        for _ in range(configuracoes['n_canibais']):
            canibal = self._criar_entidade_em_posicao_valida(Canibal)
            self.predadores.append(canibal)
        
        # Criar alimentos iniciais
        self.alimentos = []
        for _ in range(configuracoes['n_alimentos']):
            alimento = self._criar_alimento_em_posicao_valida()
            if alimento:
                self.alimentos.append(alimento)
        
        # Definir estatísticas iniciais
        self.estatisticas['populacao'] = len(self.criaturas)
        self.estatisticas['populacao_pico'] = len(self.criaturas)
        self.estatisticas['total_criaturas'] = len(self.criaturas)
        self.estatisticas['predadores_ativos'] = sum(1 for p in self.predadores if not isinstance(p, Canibal))
        self.estatisticas['canibais_ativos'] = sum(1 for p in self.predadores if isinstance(p, Canibal))
        
        # Resetar tempo
        self.tempo = 0
    
    def _criar_entidade_em_posicao_valida(self, classe_entidade):
        """Cria uma nova entidade em uma posição válida (sem colisão com paredes)"""
        max_tentativas = 50
        tentativas = 0
        
        while tentativas < max_tentativas:
            # Cria a entidade com posição aleatória
            entidade = classe_entidade(WIDTH=self.WIDTH, HEIGHT=self.HEIGHT)
            
            # Verifica se colide com alguma parede
            if not self.mapa.verificar_colisao_paredes(entidade):
                return entidade
            
            tentativas += 1
        
        # Se não conseguir após muitas tentativas, cria em uma posição fixa segura
        # (centro da tela)
        entidade = classe_entidade(x=self.WIDTH/2, y=self.HEIGHT/2, WIDTH=self.WIDTH, HEIGHT=self.HEIGHT)
        return entidade
    
    def _criar_alimento_em_posicao_valida(self):
        """Cria um novo alimento em uma posição válida (sem colisão com paredes)"""
        max_tentativas = 20
        tentativas = 0
        
        while tentativas < max_tentativas:
            # Cria o alimento com posição aleatória
            alimento = Alimento(WIDTH=self.WIDTH, HEIGHT=self.HEIGHT)
            
            # Verifica se colide com alguma parede (alimentos são menores que criaturas)
            colide = False
            for parede in self.mapa.paredes:
                if parede.colidir(alimento.x, alimento.y, alimento.tamanho):
                    colide = True
                    break
            
            if not colide:
                return alimento
            
            tentativas += 1
        
        # Se não conseguir após muitas tentativas, retorna None
        return None
    
    def atualizar(self):
        if self.pausa:
            return
        
        self.tempo += 1
        
        # Executar múltiplas atualizações se a aceleração for maior que 1
        for _ in range(self.aceleracao):
            # Atualizar criaturas
            i = 0
            while i < len(self.criaturas):
                if self.criaturas[i].atualizar(self.alimentos, self.criaturas, self.predadores, self.mapa):
                    i += 1
                else:
                    # Criatura morreu
                    self.criaturas.pop(i)
            
            # Atualizar predadores
            i = 0
            while i < len(self.predadores):
                # Verificar se é um canibal
                if isinstance(self.predadores[i], Canibal):
                    if self.predadores[i].atualizar(self.criaturas, self.predadores, self.mapa):
                        i += 1
                    else:
                        # Predador morreu
                        self.predadores.pop(i)
                else:
                    # Predador normal
                    if self.predadores[i].atualizar(self.criaturas, self.predadores, self.mapa):
                        i += 1
                    else:
                        # Predador morreu
                        self.predadores.pop(i)
            
            # Adicionar alimento com base na taxa configurada
            # (convertida de porcentagem por segundo para chance por frame)
            chance_por_frame = self.taxa_alimento / 60  # 60 frames por segundo
            
            if random.random() < chance_por_frame and len(self.alimentos) < 100:
                novo_alimento = self._criar_alimento_em_posicao_valida()
                if novo_alimento:
                    self.alimentos.append(novo_alimento)
            
            # Adicionar predador ocasionalmente se a população estiver alta
            if (len(self.criaturas) > 30 and len(self.predadores) < 8 and 
                random.random() < 0.0005):  # Chance menor para equilíbrio
                if random.random() < 0.2:  # 20% de chance de ser canibal
                    predador = self._criar_entidade_em_posicao_valida(Canibal)
                    self.predadores.append(predador)
                else:
                    predador = self._criar_entidade_em_posicao_valida(Predador)
                    self.predadores.append(predador)
        
        # Atualizar estatísticas
        self._atualizar_estatisticas()
    
    def _atualizar_estatisticas(self):
        # Atualizar população atual
        self.estatisticas['populacao'] = len(self.criaturas)
        
        # Atualizar população máxima
        if len(self.criaturas) > self.estatisticas['populacao_pico']:
            self.estatisticas['populacao_pico'] = len(self.criaturas)
        
        # Atualizar número de predadores e canibais ativos
        self.estatisticas['predadores_ativos'] = sum(1 for p in self.predadores if not isinstance(p, Canibal))
        self.estatisticas['canibais_ativos'] = sum(1 for p in self.predadores if isinstance(p, Canibal))
        
        # Calcular médias
        if len(self.criaturas) > 0:
            self.estatisticas['idade_media'] = sum(c.idade for c in self.criaturas) / len(self.criaturas)
            self.estatisticas['velocidade_media'] = sum(c.velocidade for c in self.criaturas) / len(self.criaturas)
            self.estatisticas['stamina_media'] = sum(c.stamina for c in self.criaturas) / len(self.criaturas)
            self.estatisticas['tamanho_medio'] = sum(c.tamanho for c in self.criaturas) / len(self.criaturas)
        
        # Incrementar geração se a população diminuiu significativamente e depois se recuperou
        if (self.estatisticas['populacao'] > 20 and 
            self.estatisticas['populacao'] > self.estatisticas['populacao_pico'] * 0.75):
            self.estatisticas['geracao'] += 1
            self.estatisticas['populacao_pico'] = self.estatisticas['populacao']
        
        # Contar total de criaturas que já existiram
        self.estatisticas['total_criaturas'] = Criatura.contador_id
    
    def desenhar(self, superficie):
        # Desenhar mapa (terrenos e paredes)
        if self.mapa:
            self.mapa.desenhar(superficie)
        else:
            # Fundo padrão se não houver mapa
            superficie.fill((50, 50, 50))  # Cinza escuro
        
        # Desenhar alimentos
        for alimento in self.alimentos:
            alimento.desenhar(superficie)
        
        # Desenhar criaturas
        for criatura in self.criaturas:
            criatura.desenhar(superficie)
        
        # Desenhar predadores
        for predador in self.predadores:
            predador.desenhar(superficie)
        
        # Desenhar estatísticas
        self._desenhar_estatisticas(superficie)
        
        # Desenhar controles
        self._desenhar_controles(superficie)
    
    def _desenhar_estatisticas(self, superficie):
        # Fundo semi-transparente para as estatísticas
        s = pygame.Surface((250, 200))  # Aumentado para incluir informação de canibais
        s.set_alpha(180)
        s.fill((30, 30, 30))
        superficie.blit(s, (10, 10))
        
        # Título
        texto_titulo = self.fonte_titulo.render("Estatísticas", True, (255, 255, 255))
        superficie.blit(texto_titulo, (15, 15))
        
        # Informações principais
        estatisticas_texto = [
            f"Geração: {self.estatisticas['geracao']}",
            f"População: {self.estatisticas['populacao']} (Pico: {self.estatisticas['populacao_pico']})",
            f"Total de criaturas: {self.estatisticas['total_criaturas']}",
            f"Predadores: {self.estatisticas['predadores_ativos']}",
            f"Canibais: {self.estatisticas['canibais_ativos']}",
            f"Alimentos: {len(self.alimentos)}",
            f"Idade média: {self.estatisticas['idade_media']:.1f}",
            f"Velocidade média: {self.estatisticas['velocidade_media']:.2f}",
            f"Stamina média: {self.estatisticas['stamina_media']:.1f}",
            f"Tamanho médio: {self.estatisticas['tamanho_medio']:.2f}"
        ]
        
        for i, texto in enumerate(estatisticas_texto):
            superficie.blit(self.fonte.render(texto, True, (255, 255, 255)), (15, 50 + i * 20))
    
    def _desenhar_controles(self, superficie):
        # Fundo semi-transparente para os controles
        s = pygame.Surface((250, 100))
        s.set_alpha(180)
        s.fill((30, 30, 30))
        superficie.blit(s, (10, self.HEIGHT - 110))
        
        # Título
        texto_titulo = self.fonte_titulo.render("Controles", True, (255, 255, 255))
        superficie.blit(texto_titulo, (15, self.HEIGHT - 105))
        
        # Instruções
        controles_texto = [
            "P: Pausar/Continuar",
            "R: Reiniciar simulação",
            "+/-: Aumentar/Diminuir velocidade",
            "A: Adicionar alimento"
        ]
        
        for i, texto in enumerate(controles_texto):
            superficie.blit(self.fonte.render(texto, True, (255, 255, 255)), (15, self.HEIGHT - 80 + i * 20))
    
    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_p:
                # Pausar/Continuar
                self.pausa = not self.pausa
            elif evento.key == pygame.K_r:
                # Reiniciar
                self.inicializar()
            elif evento.key == pygame.K_EQUALS or evento.key == pygame.K_PLUS:
                # Aumentar velocidade
                self.aceleracao = min(10, self.aceleracao + 1)
            elif evento.key == pygame.K_MINUS:
                # Diminuir velocidade
                self.aceleracao = max(1, self.aceleracao - 1)
            elif evento.key == pygame.K_a:
                # Adicionar alimento
                alimento = self._criar_alimento_em_posicao_valida()
                if alimento:
                    self.alimentos.append(alimento)
