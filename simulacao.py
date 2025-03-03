import pygame
import random
from criatura import Criatura
from predador import Predador
from canibal import Canibal
from alimento import Alimento
from mapa import Mapa
from efeito_visual import EfeitoVisual

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
        self.fonte_grande = pygame.font.SysFont("Arial", 32)
        self.pausa = False
        self.aceleracao = 1
        self.mapa = None
        self.taxa_alimento = 0.5  # Taxa padrão de geração de alimentos
        
        # Sistema de efeitos visuais
        self.efeitos = EfeitoVisual()
        
        # Sistema de fim de jogo e estatísticas
        self.jogo_finalizado = False
        self.vencedor = None  # "presas" ou "predadores"
        self.estatisticas_finais = {
            'criatura_media': {},
            'criatura_mais_forte': None,
            'predador_medio': {},
            'predador_mais_forte': None,
            'tempo_total': 0,
            'geracoes': 0
        }
    
    def inicializar(self, configuracoes=None):
        # Configurações padrão se não fornecidas
        if configuracoes is None:
            configuracoes = {
                'mapa': 'aleatorio',
                'n_presas': 20,
                'n_predadores': 3,
                'n_canibais': 1,
                'n_alimentos': 40,
                'taxa_alimento': 10, 
                'modo_atributos': 'aleatorio',  # 'padrao' ou 'aleatorio'
                
                # Porcentagens de terrenos (total deve ser 100%)
                'terrenos': {
                    'grama': 40,
                    'agua': 20,
                    'lama': 10,
                    'gelo': 5,
                    'deserto': 10,
                    'montanha': 5,
                    'floresta': 5,
                    'pantano': 5
                }
            }
        
        # Limpar efeitos visuais
        self.efeitos.limpar()
        
        # Criar e inicializar o mapa
        self.mapa = Mapa(self.WIDTH, self.HEIGHT)
        
        # Compartilhar referência para a simulação com o mapa
        # (permite que o mapa acesse o sistema de efeitos para feedback visual)
        self.mapa.simulacao = self
        
        # Inicializar mapa com base no tipo escolhido
        if configuracoes['mapa'] == 'personalizado':
            self.mapa.criar_mapa_predefinido(configuracoes['mapa'], configuracoes['terrenos'])
        else:
            self.mapa.criar_mapa_predefinido(configuracoes['mapa'])
        
        # Armazenar taxa de geração de alimentos
        self.taxa_alimento = configuracoes['taxa_alimento']
        
        # Modo de atributos (padrão ou aleatório)
        modo_atributos = configuracoes.get('modo_atributos', 'aleatorio')
        
        # Valores padrão para atributos
        atributos_padrao = {
            'velocidade': 2.0,
            'stamina': 150.0,
            'longevidade': 700.0,
            'tamanho': 6.0,
            'comunicacao': 3.0,
            'velocidade_nado': 0.0
        }
        
        # Criar criaturas iniciais
        self.criaturas = []
        for _ in range(configuracoes['n_presas']):
            # Se modo padrão, usar valores padrão para todos
            if modo_atributos == 'padrao':
                criatura = Criatura(
                    velocidade=atributos_padrao['velocidade'],
                    stamina=atributos_padrao['stamina'],
                    longevidade=atributos_padrao['longevidade'],
                    tamanho=atributos_padrao['tamanho'],
                    comunicacao=atributos_padrao['comunicacao'],
                    velocidade_nado=atributos_padrao['velocidade_nado'],
                    WIDTH=self.WIDTH,
                    HEIGHT=self.HEIGHT
                )
                # Tentar colocar em posição válida
                for _ in range(10):  # Tentar algumas vezes
                    if not self.mapa.verificar_colisao_paredes(criatura):
                        break
                    criatura.x = random.randint(50, self.WIDTH - 50)
                    criatura.y = random.randint(50, self.HEIGHT - 50)
            else:
                # Modo aleatório: criar entidade em posição válida
                criatura = self._criar_entidade_em_posicao_valida(Criatura)
                
            self.criaturas.append(criatura)
        
        # Criar predadores iniciais
        self.predadores = []
        for _ in range(configuracoes['n_predadores']):
            if modo_atributos == 'padrao':
                predador = Predador(
                    velocidade=atributos_padrao['velocidade'] * 1.2,
                    stamina=atributos_padrao['stamina'] * 1.2,
                    tamanho=atributos_padrao['tamanho'] * 1.2,
                    velocidade_nado=atributos_padrao['velocidade_nado'],
                    WIDTH=self.WIDTH,
                    HEIGHT=self.HEIGHT
                )
                # Tentar colocar em posição válida
                for _ in range(10):  # Tentar algumas vezes
                    if not self.mapa.verificar_colisao_paredes(predador):
                        break
                    predador.x = random.randint(50, self.WIDTH - 50)
                    predador.y = random.randint(50, self.HEIGHT - 50)
            else:
                predador = self._criar_entidade_em_posicao_valida(Predador)
                
            self.predadores.append(predador)
        
        # Adicionar canibais
        for _ in range(configuracoes['n_canibais']):
            if modo_atributos == 'padrao':
                canibal = Canibal(
                    velocidade=atributos_padrao['velocidade'] * 1.5,
                    stamina=atributos_padrao['stamina'] * 1.3,
                    tamanho=atributos_padrao['tamanho'] * 1.3,
                    velocidade_nado=atributos_padrao['velocidade_nado'],
                    WIDTH=self.WIDTH,
                    HEIGHT=self.HEIGHT
                )
                # Tentar colocar em posição válida
                for _ in range(10):  # Tentar algumas vezes
                    if not self.mapa.verificar_colisao_paredes(canibal):
                        break
                    canibal.x = random.randint(50, self.WIDTH - 50)
                    canibal.y = random.randint(50, self.HEIGHT - 50)
            else:
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
        
        # Resetar tempo e efeitos
        self.tempo = 0
        
        # Resetar sistema de fim de jogo
        self.jogo_finalizado = False
        self.vencedor = None
    
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
        if self.pausa or self.jogo_finalizado:
            return
        
        self.tempo += 1
        
        # Atualizar efeitos visuais
        self.efeitos.atualizar()
        
        # Executar múltiplas atualizações se a aceleração for maior que 1
        for _ in range(self.aceleracao):
            # Atualizar criaturas
            i = 0
            while i < len(self.criaturas):
                criatura_antiga = self.criaturas[i].copy() if hasattr(self.criaturas[i], 'copy') else None
                
                if self.criaturas[i].atualizar(self.alimentos, self.criaturas, self.predadores, self.mapa):
                    # Verificar se a criatura foi alertada por outra (para efeito visual)
                    if criatura_antiga and not criatura_antiga.alertada and self.criaturas[i].alertada:
                        self.efeitos.adicionar_onda(
                            self.criaturas[i].x, 
                            self.criaturas[i].y, 
                            (255, 255, 0, 50),  # Amarelo translúcido
                            raio_max=self.criaturas[i].campo_visao
                        )
                    
                    i += 1
                else:
                    # Criatura morreu
                    # Adicionar efeito de partículas na morte
                    self.efeitos.adicionar_particulas(
                        self.criaturas[i].x,
                        self.criaturas[i].y,
                        (150, 150, 150, 200),  # Cinza translúcido
                        num_particulas=15
                    )
                    
                    self.criaturas.pop(i)
            
            # Atualizar predadores
            i = 0
            while i < len(self.predadores):
                predador_antigo = self.predadores[i].copy() if hasattr(self.predadores[i], 'copy') else None
                
                # Verificar se é um canibal
                if isinstance(self.predadores[i], Canibal):
                    if self.predadores[i].atualizar(self.criaturas, self.predadores, self.mapa):
                        # Verificar se capturou presa (para efeito visual)
                        if predador_antigo and self.predadores[i].alvo != predador_antigo.alvo:
                            self.efeitos.adicionar_flash(
                                self.predadores[i].x,
                                self.predadores[i].y,
                                (255, 0, 0, 100)  # Vermelho translúcido
                            )
                        
                        i += 1
                    else:
                        # Predador morreu
                        self.efeitos.adicionar_particulas(
                            self.predadores[i].x,
                            self.predadores[i].y,
                            (200, 0, 0, 200),  # Vermelho translúcido
                            num_particulas=20
                        )
                        
                        self.predadores.pop(i)
                else:
                    # Predador normal
                    if self.predadores[i].atualizar(self.criaturas, self.predadores, self.mapa):
                        i += 1
                    else:
                        # Predador morreu
                        self.efeitos.adicionar_particulas(
                            self.predadores[i].x,
                            self.predadores[i].y,
                            (180, 0, 0, 180),  # Vermelho translúcido
                            num_particulas=15
                        )
                        
                        self.predadores.pop(i)
            
            # Adicionar alimento com base na taxa configurada
            # (convertida de porcentagem por segundo para chance por frame)
            # Aumentada em 5x para ter muito mais alimentos
            chance_por_frame = self.taxa_alimento 
            
            # Aumentar também o limite máximo de alimentos
            if random.random() < chance_por_frame and len(self.alimentos) < 300:
                novo_alimento = self._criar_alimento_em_posicao_valida()
                if novo_alimento:
                    self.alimentos.append(novo_alimento)
                    
                    # Efeito visual para novo alimento
                    self.efeitos.adicionar_particulas(
                        novo_alimento.x,
                        novo_alimento.y,
                        (100, 255, 100, 150),  # Verde claro translúcido
                        num_particulas=5,
                        velocidade=0.8,
                        tamanho=1.5
                    )
            
            # Verificar condições de fim de jogo
            self._verificar_fim_de_jogo()
        
        # Atualizar estatísticas
        self._atualizar_estatisticas()
    
    def _verificar_fim_de_jogo(self):
        """Verifica se a simulação terminou e coleta estatísticas finais"""
        # Se o jogo já estiver finalizado, não fazer nada
        if self.jogo_finalizado:
            return
            
        # Verificar condições de fim de jogo
        if len(self.criaturas) == 0 or len(self.predadores) == 0:
            # Jogo terminou!
            self.jogo_finalizado = True
            
            # Definir vencedor
            if len(self.criaturas) == 0:
                self.vencedor = "predadores"
            else:
                self.vencedor = "presas"
            
            # Coletar estatísticas finais
            self._coletar_estatisticas_finais()
            
            # Adicionar efeito visual para indicar o fim do jogo
            centro_x = self.WIDTH // 2
            centro_y = self.HEIGHT // 2
            
            self.efeitos.adicionar_onda(
                centro_x, centro_y,
                (255, 255, 255, 100),
                raio_max=200,
                vida_max=40
            )
            
            # Texto de fim de jogo
            texto = f"Vitória das {self.vencedor.capitalize()}!"
            self.efeitos.adicionar_texto_flutuante(
                centro_x - 100, centro_y - 100,
                texto,
                (255, 255, 0),
                vida_max=120,
                tamanho_fonte=28
            )
    
    def _coletar_estatisticas_finais(self):
        """Coleta estatísticas detalhadas sobre as criaturas/predadores sobreviventes"""
        self.estatisticas_finais['tempo_total'] = self.tempo
        self.estatisticas_finais['geracoes'] = self.estatisticas['geracao']
        
        # Estatísticas das criaturas sobreviventes
        if len(self.criaturas) > 0:
            # Encontrar a criatura mais forte (combinação de atributos)
            criaturas_ordenadas = sorted(self.criaturas, 
                                       key=lambda c: c.velocidade * 0.3 + c.stamina * 0.3 + c.tamanho * 0.2 + (c.velocidade_nado or 0) * 0.2,
                                       reverse=True)
            
            self.estatisticas_finais['criatura_mais_forte'] = criaturas_ordenadas[0]
            
            # Calcular médias
            self.estatisticas_finais['criatura_media'] = {
                'velocidade': sum(c.velocidade for c in self.criaturas) / len(self.criaturas),
                'stamina': sum(c.stamina for c in self.criaturas) / len(self.criaturas),
                'tamanho': sum(c.tamanho for c in self.criaturas) / len(self.criaturas),
                'velocidade_nado': sum(getattr(c, 'velocidade_nado', 0) for c in self.criaturas) / len(self.criaturas),
                'comunicacao': sum(getattr(c, 'comunicacao', 0) for c in self.criaturas) / len(self.criaturas),
                'idade_media': sum(c.idade for c in self.criaturas) / len(self.criaturas),
                'filhos_media': sum(c.filhos for c in self.criaturas) / len(self.criaturas)
            }
        
        # Estatísticas dos predadores sobreviventes
        if len(self.predadores) > 0:
            # Encontrar o predador mais forte (combinação de atributos)
            predadores_ordenados = sorted(self.predadores, 
                                       key=lambda p: p.velocidade * 0.3 + p.stamina * 0.3 + p.tamanho * 0.3 + (p.velocidade_nado or 0) * 0.1,
                                       reverse=True)
            
            self.estatisticas_finais['predador_mais_forte'] = predadores_ordenados[0]
            
            # Calcular médias
            self.estatisticas_finais['predador_medio'] = {
                'velocidade': sum(p.velocidade for p in self.predadores) / len(self.predadores),
                'stamina': sum(p.stamina for p in self.predadores) / len(self.predadores),
                'tamanho': sum(p.tamanho for p in self.predadores) / len(self.predadores),
                'velocidade_nado': sum(getattr(p, 'velocidade_nado', 0) for p in self.predadores) / len(self.predadores),
                'idade_media': sum(p.idade for p in self.predadores) / len(self.predadores),
                'filhos_media': sum(p.filhos for p in self.predadores) / len(self.predadores),
                'canibais_percentual': (sum(1 for p in self.predadores if isinstance(p, Canibal)) / len(self.predadores)) * 100
            }
    
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
        
        # Desenhar efeitos visuais
        self.efeitos.desenhar(superficie)
        
        if self.jogo_finalizado:
            # Se o jogo terminou, desenhar tela de estatísticas finais
            self._desenhar_estatisticas_finais(superficie)
        else:
            # Desenhar estatísticas normais durante o jogo
            self._desenhar_estatisticas(superficie)
            
            # Desenhar controles
            self._desenhar_controles(superficie)
    
    def _desenhar_estatisticas_finais(self, superficie):
        """Desenha a tela de estatísticas finais quando o jogo termina"""
        # Criar uma superfície semi-transparente para o fundo
        s = pygame.Surface((self.WIDTH, self.HEIGHT))
        s.set_alpha(220)
        s.fill((20, 20, 40))  # Azul escuro para fundo
        superficie.blit(s, (0, 0))
        
        # Título principal
        texto_titulo = self.fonte_grande.render(f"Simulação finalizada - Vitória das {self.vencedor.capitalize()}!", True, (255, 255, 0))
        superficie.blit(texto_titulo, (self.WIDTH//2 - texto_titulo.get_width()//2, 40))
        
        # Informações gerais
        info_geral = [
            f"Tempo total: {self.estatisticas_finais['tempo_total']} frames",
            f"Gerações: {self.estatisticas_finais['geracoes']}",
            f"Presas sobreviventes: {len(self.criaturas)}",
            f"Predadores sobreviventes: {len(self.predadores)} (Canibais: {sum(1 for p in self.predadores if isinstance(p, Canibal))})"
        ]
        
        for i, texto in enumerate(info_geral):
            superficie.blit(self.fonte_titulo.render(texto, True, (220, 220, 220)), (self.WIDTH//2 - 200, 100 + i * 35))
        
        # Desenhar informações das criaturas se houver sobreviventes
        y_pos = 250
        if len(self.criaturas) > 0:
            # Título da seção
            texto_secao = self.fonte_titulo.render("Estatísticas das Presas", True, (100, 200, 100))
            superficie.blit(texto_secao, (self.WIDTH//4 - texto_secao.get_width()//2, y_pos))
            
            # Estatísticas da criatura média
            media = self.estatisticas_finais['criatura_media']
            textos_media = [
                f"Velocidade média: {media['velocidade']:.2f}",
                f"Stamina média: {media['stamina']:.1f}",
                f"Tamanho médio: {media['tamanho']:.2f}",
                f"Velocidade de nado média: {media['velocidade_nado']:.2f}",
                f"Comunicação média: {media['comunicacao']:.2f}",
                f"Idade média: {media['idade_media']:.1f}",
                f"Descendentes por indivíduo: {media['filhos_media']:.1f}"
            ]
            
            for i, texto in enumerate(textos_media):
                superficie.blit(self.fonte.render(texto, True, (180, 230, 180)), (100, y_pos + 40 + i * 25))
            
            # Informações sobre a criatura mais forte
            mais_forte = self.estatisticas_finais['criatura_mais_forte']
            y_pos_forte = y_pos + 40
            
            titulo_forte = self.fonte.render("CRIATURA MAIS FORTE:", True, (100, 255, 100))
            superficie.blit(titulo_forte, (self.WIDTH//2 + 50, y_pos_forte))
            
            textos_forte = [
                f"Velocidade: {mais_forte.velocidade:.2f}",
                f"Stamina: {mais_forte.stamina:.1f}",
                f"Tamanho: {mais_forte.tamanho:.2f}",
                f"Velocidade nado: {getattr(mais_forte, 'velocidade_nado', 0):.2f}",
                f"Comunicação: {getattr(mais_forte, 'comunicacao', 0):.2f}",
                f"Idade: {mais_forte.idade}",
                f"Filhos: {mais_forte.filhos}"
            ]
            
            for i, texto in enumerate(textos_forte):
                superficie.blit(self.fonte.render(texto, True, (150, 255, 150)), (self.WIDTH//2 + 50, y_pos_forte + 25 + i * 25))
        
        # Desenhar informações dos predadores se houver sobreviventes
        y_pos = 450
        if len(self.predadores) > 0:
            # Título da seção
            texto_secao = self.fonte_titulo.render("Estatísticas dos Predadores", True, (200, 100, 100))
            superficie.blit(texto_secao, (self.WIDTH//4 - texto_secao.get_width()//2, y_pos))
            
            # Estatísticas do predador médio
            media = self.estatisticas_finais['predador_medio']
            textos_media = [
                f"Velocidade média: {media['velocidade']:.2f}",
                f"Stamina média: {media['stamina']:.1f}",
                f"Tamanho médio: {media['tamanho']:.2f}",
                f"Velocidade de nado média: {media['velocidade_nado']:.2f}",
                f"Idade média: {media['idade_media']:.1f}",
                f"Descendentes por indivíduo: {media['filhos_media']:.1f}",
                f"Percentual de canibais: {media['canibais_percentual']:.1f}%"
            ]
            
            for i, texto in enumerate(textos_media):
                superficie.blit(self.fonte.render(texto, True, (230, 180, 180)), (100, y_pos + 40 + i * 25))
            
            # Informações sobre o predador mais forte
            mais_forte = self.estatisticas_finais['predador_mais_forte']
            y_pos_forte = y_pos + 40
            
            # Determinar tipo de predador mais forte
            tipo_mais_forte = "CANIBAL" if isinstance(mais_forte, Canibal) else "PREDADOR"
            titulo_forte = self.fonte.render(f"{tipo_mais_forte} MAIS FORTE:", True, (255, 100, 100))
            superficie.blit(titulo_forte, (self.WIDTH//2 + 50, y_pos_forte))
            
            textos_forte = [
                f"Velocidade: {mais_forte.velocidade:.2f}",
                f"Stamina: {mais_forte.stamina:.1f}",
                f"Tamanho: {mais_forte.tamanho:.2f}",
                f"Velocidade nado: {getattr(mais_forte, 'velocidade_nado', 0):.2f}",
                f"Idade: {mais_forte.idade}",
                f"Filhos: {mais_forte.filhos}"
            ]
            
            # Adicionar forma para canibais
            if isinstance(mais_forte, Canibal) and hasattr(mais_forte, 'forma'):
                textos_forte.append(f"Forma: {mais_forte.forma.capitalize()}")
            
            for i, texto in enumerate(textos_forte):
                superficie.blit(self.fonte.render(texto, True, (255, 150, 150)), (self.WIDTH//2 + 50, y_pos_forte + 25 + i * 25))
        
        # Desenhar instruções
        texto_instrucao = self.fonte_titulo.render("Pressione SPACE para voltar ao menu ou R para reiniciar", True, (255, 255, 255))
        superficie.blit(texto_instrucao, (self.WIDTH//2 - texto_instrucao.get_width()//2, self.HEIGHT - 80))
    
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
            # Se o jogo terminou, aceitar apenas os comandos de reinício/menu
            if self.jogo_finalizado:
                if evento.key == pygame.K_r:
                    # Reiniciar a simulação
                    self.jogo_finalizado = False
                    self.inicializar()
                    return None
                elif evento.key == pygame.K_SPACE:
                    # Voltar ao menu
                    return "voltar_menu"
            else:
                # Comandos disponíveis durante o jogo
                if evento.key == pygame.K_p:
                    # Pausar/Continuar
                    self.pausa = not self.pausa
                elif evento.key == pygame.K_r:
                    # Sinalizar para voltar ao menu
                    # Não inicializamos aqui, pois main.py precisa voltar ao menu
                    return "voltar_menu"
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
        
        return None