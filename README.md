# Flavor Chef

Um jogo educativo em Python onde o jogador assume o papel de um chef que precisa atender clientes exigentes, interpretando palavras descritivas em inglês para escolher o prato correto e os ingredientes ideais.

---

## Sobre o Projeto

**Flavor Chef** é um jogo desenvolvido como trabalho escolar com o objetivo de ensinar vocabulário de descrições sensoriais em inglês (como *briny*, *gooey*, *flaky*, *earthy*, entre outras) de forma divertida e interativa.

Cada cliente chega com um pedido usando uma palavra-chave descritiva. O jogador deve:
1. **Escolher o prato correto** entre 4 opções (com imagens).
2. **Selecionar os ingredientes certos** para preparar o prato.

Acertos geram pontos e dinheiro. Erros mostram uma explicação didática sobre o significado da palavra.

---

## Como Jogar

1. Leia o pedido do cliente na tela.
2. Escolha uma das 4 opções de prato apresentadas.
3. Se acertar, monte o prato selecionando os ingredientes corretos.
4. Confirme a escolha e veja sua pontuação aumentar.
5. Ao final de todas as perguntas, veja seu **rank** e quantas **estrelas** você conquistou!

### Ranks

| Pontuação | Rank | Estrelas |
|-----------|------|----------|
| 5000+ | FOOD EXPERT | 5 estrelas |
| 4000+ | HEAD CHEF | 4 estrelas |
| 3000+ | SOUS CHEF | 3 estrelas |
| 2000+ | LINE COOK | 2 estrelas |
| Abaixo de 2000 | TRAINEE | 1 estrela |

---

## Estrutura do Projeto

```
projeto/
├── main.py                # Menu principal e inicialização
├── game.py                # Lógica principal do jogo (modo "Flavor Chef")
├── loading.py             # Tela de carregamento
├── questions.json         # Banco de perguntas com clientes, pratos e ingredientes
├── README.md
└── assets/
    ├── background.png
    ├── customer.png
    ├── what_do_you_serve.png
    ├── ingredients.png
    ├── correct.png
    ├── wrong.png
    ├── completed.png
    ├── money_score.png
    ├── food_vocabulary.png
    ├── tutorial.png
    ├── button_confirm.png
    ├── background.ogg
    ├── correct.ogg
    ├── wrong.ogg
    ├── Inter-VariableFont_opsz,wght.ttf
    ├── customers/      # Imagens dos clientes
    ├── dishes/         # Imagens dos pratos
    ├── ingredients/    # Imagens dos ingredientes
    └── stars/          # Imagens das estrelas (1_star.png ... 5_star.png)
```

---

## Vocabulário Abordado

O jogo ensina palavras descritivas em inglês relacionadas a sabor, textura e temperatura, como:

| Palavra | Significado |
|---------|-------------|
| **Briny** | Salgado, como o mar |
| **Gooey** | Pegajoso, cremoso |
| **Airy** | Leve, cheio de ar |
| **Smoky** | Defumado |
| **Tangy** | Ácido, refrescante |
| **Velvety** | Aveludado, suave |
| **Flaky** | Em camadas, quebradiço |
| **Earthy** | Terroso, profundo |
| **Crumbly** | Esfarelado |
| **Pungent** | Pungente, forte |
| **Crispy** | Crocante |
| **Fluffy** | Fofo, macio |
| **Creamy** | Cremoso |
| **Fizzy** | Efervescente |
| **Herbal** | Herbal, calmante |
| **Chilled** | Gelado |
| **Frozen** | Congelado |
| **Spicy** | Picante |
| **Plain** | Simples, sem sabor forte |
| **Watery** | Aguado, refrescante |
| **Chocolatey** | Achocolatado |
| **Hearty** | Substancial, reconfortante |
| **Dry** | Seco |
| **Buttery** | Amanteigado |
| **Thick** | Espesso |

---

## Tecnologias Utilizadas

- **Python 3**
- **Pygame**: renderização gráfica, sons e input
- **Pillow (PIL)**: manipulação de imagens (redimensionamento, cantos arredondados, máscaras)
- **JSON**: armazenamento das perguntas e dados do jogo

---

## Como Executar

### Pré-requisitos

```bash
pip install pygame pillow
```

### Execução

```bash
python main.py
```

O jogo abrirá em **tela cheia**. Use o mouse para navegar pelos menus e interagir com o jogo.

---

## Funcionalidades

- Sistema de pontuação e dinheiro
- Sistema de ranks e estrelas ao final da partida
- Música de fundo e efeitos sonoros (acerto/erro)
- Tela de tutorial e vocabulário
- Tela de carregamento animada
- Feedback visual para acertos e erros
- Explicação didática da palavra-chave em cada erro
- Embaralhamento aleatório de perguntas e alternativas a cada partida
- Interface adaptativa (escala conforme a resolução da tela)

---

## Integrantes do Grupo

- Erick
- Isabelly
- Victor A.
- Luiz
- Enzo
- Giovanni
- Samuel
- Thomas

---

## Objetivo Educacional

Este projeto foi desenvolvido como atividade escolar com o intuito de unir **programação** e **aprendizado de inglês**, tornando o estudo de vocabulário mais dinâmico e envolvente através da gamificação.