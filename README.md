# Snake MECATRÔNICA 🐍

Um jogo Snake modernizado e temático desenvolvido para o curso de Mecatrônica, onde o jogador deve coletar as letras da palavra "MECATRÔNICA" em ordem sequencial enquanto enfrenta desafios únicos.

## 🎮 Sobre o Jogo

Snake MECATRÔNICA é uma versão inovadora do clássico jogo Snake, desenvolvida com foco educacional e interativo. O jogador controla uma cobra que deve coletar letras específicas em ordem, enfrentando inimigos, coletando power-ups e progredindo através de três fases desafiadoras.

### ✨ Características Principais

- **Sistema de Letras**: Colete as letras de "MECATRÔNICA" em ordem sequencial
- **3 Fases Progressivas**: Cada fase aumenta a dificuldade e velocidade
- **Inimigos Inteligentes**: Aranhas que perseguem o jogador e criam obstáculos
- **Sistema de Tiros**: Elimine inimigos com projéteis limitados
- **Power-ups Estratégicos**:
  - ⚡ Velocidade aumentada
  - 🧊 Congelamento de inimigos
  - 🛡️ Escudo protetor
  - ⏰ Redução de tempo
  - 🎯 Munição extra
- **Múltiplos Temas Visuais**:
  - 🌊 CLEAN (Cobra d'água)
  - 🌆 NEON (Cobra coral)
  - 🟤 RETRO70 (Cascavel)
- **Sistema de Ranking**: Compete pelos melhores tempos
- **Fundos Personalizáveis**: Adicione suas próprias imagens de fundo

## 🕹️ Como Jogar

### Controles
- **Movimento**: Setas direcionais ou WASD
- **Atirar**: Barra de espaço
- **Pausar**: Tecla 0 (zero)

### Objetivo
1. Colete as letras de "MECATRÔNICA" na ordem correta
2. Evite colidir com paredes, seu próprio corpo, aranhas e pilares
3. Use tiros para eliminar aranhas e ganhar pontos
4. Complete as 3 fases no menor tempo possível

### Sistema de Pontuação
- **Tempo**: Quanto menor, melhor sua posição no ranking
- **Coleta de Letras**: Cada letra coletada corretamente aumenta sua velocidade
- **Eliminação de Inimigos**: Aranhas eliminadas contam para sua pontuação

## 🛠️ Instalação e Execução

### Pré-requisitos
- Python 3.7 ou superior
- Pygame 2.0 ou superior

### Instalação
```bash
# Clone o repositório
git clone https://github.com/[usuario]/Jogo_Cobra.git
cd Jogo_Cobra

# Instale as dependências
pip install pygame

# Execute o jogo
python run_game.py
```

### Estrutura do Projeto
```
Jogo_Cobra/
├── src/
│   ├── main.py              # Arquivo principal do jogo
│   ├── configs/
│   │   └── config.py        # Configurações do jogo
│   ├── utils/
│   │   └── utils.py         # Utilitários e helpers
│   ├── handlers/
│   │   └── managers.py      # Gerenciadores de tema e áudio
│   └── interfaces/
│       └── entities.py      # Classes das entidades do jogo
├── fonts/                   # Fontes personalizadas
├── music/                   # Trilhas sonoras (opcional)
├── sfx/                     # Efeitos sonoros (opcional)
└── run_game.py             # Script de execução
```

## 🎨 Recursos Técnicos

### Arquitetura Modular
- **Separação de Responsabilidades**: Código organizado em módulos específicos
- **Sistema de Estados**: Gerenciamento eficiente de diferentes telas do jogo
- **Gerenciamento de Recursos**: Carregamento dinâmico de temas e assets
- **Sistema de Partículas**: Efeitos visuais avançados

### Características Avançadas
- **Animação Suave da Cobra**: Movimento fluido com interpolação
- **Sistema de Temas Dinâmico**: Troca de temas em tempo real
- **Áudio Integrado**: Música temática e efeitos sonoros
- **Resolução Adaptável**: Suporte a múltiplas resoluções
- **Persistência de Dados**: Salvamento de configurações e ranking

## 👨‍💻 Equipe de Desenvolvimento

Este jogo foi desenvolvido por:

- **Aurelio dos Reis**
- **Bruno Henrique de Almeida**
- **Christian Machado do Nascimento**
- **Nicole Kaminski**

*Projeto desenvolvido para o curso de Engenharia Mecatrônica - 10° Período*

## 📋 Funcionalidades Implementadas

### ✅ Sistema de Jogo
- [x] Movimentação da cobra com física realista
- [x] Coleta sequencial de letras
- [x] Sistema de fases progressivas
- [x] Detecção de colisões precisas
- [x] Sistema de vidas/game over

### ✅ Inimigos e Obstáculos
- [x] Aranhas com IA de perseguição
- [x] Pilares temporários como obstáculos
- [x] Sistema de spawning dinâmico

### ✅ Sistema de Combate
- [x] Tiros direcionais
- [x] Eliminação de inimigos
- [x] Munição limitada e coletável

### ✅ Power-ups
- [x] 5 tipos diferentes de power-ups
- [x] Efeitos temporários
- [x] Spawning aleatório

### ✅ Interface e UX
- [x] Menus navegáveis por teclado
- [x] HUD informativo completo
- [x] Sistema de entrada de nome
- [x] Ranking de melhores tempos

### ✅ Personalização
- [x] 3 temas visuais distintos
- [x] Backgrounds customizáveis
- [x] Configurações de áudio
- [x] Múltiplas resoluções

## 🐛 Solução de Problemas

### Problemas Comuns
1. **Erro de Importação**: Certifique-se de que todas as dependências estão instaladas
2. **Áudio não Funciona**: Verifique se o pygame.mixer está funcionando corretamente
3. **Fontes não Carregam**: O jogo usa fontes de fallback automáticas do sistema

### Suporte
Para reportar bugs ou sugerir melhorias, entre em contato com a equipe de desenvolvimento.

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais como parte do curso de Engenharia Mecatrônica.

---

*Desenvolvido pela equipe de Engenharia Mecatrônica - 10° Período*
