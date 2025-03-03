# Simulador de Seleção Natural

Um simulador evolucionário interativo com presas, predadores, canibais e diversos tipos de terreno. Observe como as criaturas se adaptam e evoluem para sobreviver em diferentes ambientes!

## Características

- **Múltiplos tipos de criaturas**:
  - **Presas**: Criaturas que buscam alimento e fogem de predadores.
  - **Predadores**: Caçam presas e podem evoluir para canibais.
  - **Canibais**: Predadores evoluídos que podem caçar outros predadores.

- **Sistema de comunicação entre presas**:
  - **Altruístas** (triângulos): Alertam todas as criaturas sobre predadores.
  - **Egoístas** (quadrados): Alertam apenas outras criaturas do mesmo tipo.
  - **Campo de visão** representado por círculos transparentes.

- **Terrenos variados**:
  - **Grama**: Terreno padrão sem efeitos especiais.
  - **Lama**: Reduz a velocidade e consome mais energia.
  - **Gelo**: Aumenta a velocidade, mas reduz o controle.
  - **Água**: Vantagem para criaturas com adaptação aquática.
  - **Deserto**: Alto consumo de energia.
  - **Montanha**: Difícil de atravessar, alto consumo de energia.
  - **Floresta**: Reduz movimento, mas fornece energia.
  - **Pântano**: Tóxico, drena bastante energia.

- **Atributos das criaturas**:
  - **Velocidade**: Determina quão rápido as criaturas se movem (mais azul).
  - **Stamina**: Determina a energia máxima (mais verde).
  - **Longevidade**: Determina o tempo de vida.
  - **Comunicação**: Capacidade de alertar outras criaturas.
  - As criaturas mais velhas ficam mais claras visualmente.

- **Paredes e obstáculos** que as criaturas precisam contornar.

- **Interface de usuário**:
  - Menu de configuração para escolher tipo de mapa, número de criaturas, etc.
  - Estatísticas em tempo real.
  - Controles para pausar, acelerar e manipular a simulação.

## Mapas Predefinidos

- **Aleatório**: Terrenos gerados aleatoriamente.
- **Planície**: Grandes áreas de grama com um rio e algumas florestas.
- **Ilha**: Uma ilha central cercada por água.
- **Labirinto**: Um labirinto de paredes com diferentes terrenos.
- **Montanhoso**: Terreno difícil com muitos obstáculos e lagos.
- **Diversificado**: Mapa com todos os tipos de terreno em áreas definidas.

## Controles

- **P**: Pausar/Continuar a simulação
- **R**: Reiniciar a simulação
- **+/-**: Aumentar/Diminuir a velocidade da simulação
- **A**: Adicionar alimento
- **ESC**: Voltar ao menu principal

## Instalação

1. Certifique-se de ter Python 3.7 ou superior instalado.
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Execute o programa:
   ```
   python main.py
   ```

## Requisitos

- Python 3.7+
- Pygame 2.5.2+
- Pygame GUI 0.6.9+

## Como Funciona

- As criaturas começam com atributos aleatórios.
- Através da reprodução, os filhos herdam atributos dos pais com pequenas mutações.
- As presas precisam comer alimentos para sobreviver e fugir dos predadores.
- Os predadores caçam as presas. Canibais caçam tanto presas quanto outros predadores.
- Diferentes terrenos afetam a velocidade e o consumo de energia das criaturas.
- As criaturas que melhor se adaptam ao ambiente têm maior chance de sobreviver e se reproduzir.
- Observe a evolução natural ao longo de várias gerações!

## Observações sobre a Evolução

Durante a simulação, você poderá observar:
- Criaturas desenvolvendo maior velocidade para fugir ou caçar.
- Incremento na capacidade de comunicação para alertar sobre predadores.
- Adaptação aos diferentes tipos de terreno.
- Aumento na eficiência energética.
- Evolução de presas para predadores e predadores para canibais.
