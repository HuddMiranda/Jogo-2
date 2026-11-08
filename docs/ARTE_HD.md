# Simbionte — Guia de arte HD

Guia para quem vai produzir a arte do jogo (artista, estúdio ou geração por IA). O jogo troca **sozinho** a pixel art provisória pela arte HD assim que os arquivos abaixo existirem, sem mexer em código.

## Direção de arte

- **Estilo:** 2D **pintado à mão em alta resolução**, na linha de *Afterimage*: pinceladas suaves, iluminação dramática com luz de recorte (rim light), atmosfera densa, cenários em várias camadas de profundidade. Não é pixel art.
- **Mundo:** o planeta **Ossária**, bio-mecânico e alienígena: ruínas de naves antigas tomadas por organismos vivos, favos, carapaças, veios que brilham.
- **Tom:** sombrio e misterioso, com pontos de cor fortes nas fontes de luz (energia, gemas, visores).
- **Protagonista — VEX-9:** caçadora em **armadura simbionte** fechada, proporções humanas (cerca de 7 cabeças), **paleta Marfim** (marfim, dourado, traje escuro, visor e gemas azuis):
  - capacete anguloso: crista central, aba pontuda sobre os olhos, **visor em fenda** azul, máscara com saídas de ar, aleta na nuca;
  - ombreiras grandes e arredondadas com filete dourado; peito com gema azul; cintura fina de traje escuro;
  - braço direito termina num **canhão** com anéis dourados;
  - coxa, joelheira, canela, tornozelo e pé como partes bem definidas.
  - Referência: o desenho em pixel art aprovado está em `art/handmade/vex_idle_ivory.png` (proporções e peças) e o conceito vetorial no canvas de design do projeto.

## Formato técnico (vale para tudo)

- **PNG com transparência**, sem bordas extras desnecessárias.
- O jogo mostra a tela em **1920 × 1080** (área lógica de 640 × 360, escala 3x). Desenhe pensando nisso.
- **Tudo virado para a direita** (o jogo espelha).
- Nada de sombra no chão desenhada no sprite (o jogo faz).

### Personagens e inimigos

```
art/hd/<nome>/info.cfg
art/hd/<nome>/<animação>/0001.png, 0002.png, ...
```

Todos os quadros de uma animação têm **o mesmo tamanho de tela** e o personagem na **mesma posição de pés**.

`info.cfg` (exemplo da VEX-9):

```ini
[sprite]
drawn_height=192          ; altura do personagem em pé no desenho, em px
game_height=48            ; altura no jogo (px lógicos) — não mude
pivot=Vector2(128, 250)   ; ponto entre os pés (no chão), em px do quadro

[fps]
idle=10
run=24
run_shoot=24
jump=12
fall=12
spin=30
dash=20
wall=8
hurt=12
idle_shoot=10

[muzzle]
; boca do canhão (onde nasce o tiro), em px do quadro, por animação
default=Vector2(230, 120)
run_shoot=Vector2(236, 126)
```

| Personagem (`<nome>`) | Tamanho em pé no desenho | Animações (quadros sugeridos) |
|---|---|---|
| `hero` (VEX-9) | ~192 px de altura | `idle` (8–12), `idle_shoot` (4), `run` (12–16), `run_shoot` (12–16, canhão à frente), `jump` (4), `jump_shoot` (2), `fall` (4), `fall_shoot` (2), `spin` (8–12, cambalhota), `dash` (4–6), `dash_shoot` (4), `wall` (4), `hurt` (3) |
| `crawler` (Rastejante, besouro que cospe ácido) | ~64 px | `walk` (8), `shoot` (4) |
| `flyer` (Zumbidor, inseto que mergulha) | ~56 px | `fly` (6) |
| `turret` (Bulbo, casulo que se abre) | ~64 px | `closed` (1), `opening` (3), `open` (4) |
| `wasp` (Vespa de Plasma, chefe) | ~300 px | `idle` (8–12), `dash` (4), `shoot` (6), `hurt` (2) |
| `items` | ~48 px cada | `health_small`, `health_big`, `energy_small`, `energy_big`, `heart`, `capsule` (4–6 cada) |

Animações `_shoot` são as mesmas poses com o canhão apontado para a frente; se não existirem, o jogo usa a animação normal.

### Blocos do mapa

```
art/hd/tiles/<bioma>.png      (biomas: ruins, hive)
```

Atlas de **8 × 4 blocos de 64 × 64 px** (512 × 256), na mesma ordem do atlas atual (`art/tiles/<bioma>.png`):

- linha 1: topo (4 variações), ponta esquerda, ponta direita, coluna estreita;
- linha 2: miolo (4 variações), borda esquerda, borda direita, coluna estreita;
- linha 3: miolo profundo (mais escuro), mesmas colunas;
- linha 4: plataforma vazada: ponta esquerda, meio (3), ponta direita, peça única.

Os blocos precisam **emendar sem costura** com os vizinhos.

### Fundos (paralaxe)

```
art/hd/backgrounds/<bioma>/1.png, 2.png, 3.png ...
```

Camadas de **1080 px de altura** (largura livre, de preferência 3840 px), que **repetem na horizontal sem emenda**. `1.png` é a mais distante (céu, horizonte) e anda mais devagar; as seguintes vêm para a frente. 3 a 5 camadas por bioma.

## Ordem de prioridade

1. **VEX-9:** `idle`, `run`, `run_shoot`, `jump`, `fall`, `spin` — o resto pode vir depois.
2. Blocos e fundo das **Ruínas da Nave-Semente** (`ruins`).
3. Inimigos (`crawler`, `flyer`, `turret`).
4. Blocos e fundo da **Colmeia de Plasma** (`hive`) e a **Vespa de Plasma**.
5. Itens.

## Como conseguir a arte

- **Artista contratado:** o caminho para um jogo comercial. Procure portfólios de *2D game art / animation* (ArtStation, Behance, Fiverr, Upwork, grupos de gamedev). Mande este guia; peça primeiro um teste com a VEX-9 parada.
- **IA de imagem:** dá bons quadros soltos, mas manter o **mesmo personagem idêntico** em dezenas de quadros de animação é difícil. Serve bem para **fundos** e **conceitos**; para animação, use como base e peça retoques.
- **Pacotes prontos** (itch.io, Unity Asset Store, GameDev Market): rápidos e baratos para cenários e efeitos; confira a licença para uso comercial na Steam.

Para testar algo: coloque os arquivos nas pastas acima, abra o projeto no Godot (ele importa os PNG) e aperte F5. Me envie o que tiver que eu ajusto pivô, escala, velocidade e encaixe.
