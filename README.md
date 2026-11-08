# Sylvaria

Ação e plataforma **frenética** feita em **Godot 4**, no gênero dos run-and-gun com seleção de chefes, num **reino élfico**: escolha a fase, purifique o Guardião, absorva o poder dele e use-o contra o Guardião que é fraco a ele. (O nome é provisório.)

**Premissa:** em Sylvaria, a **Praga Cinzenta** corrompeu os oito **Guardiões**, espíritos-fera que protegiam a Árvore-Mãe e as florestas élficas. **Elyra**, sentinela élfica de **armadura rúnica** e **manopla arcana**, vai atrás de cada um. A armadura absorve o poder de cada Guardião purificado; peças dela (em relicários) e **Sementes da Vida** estão escondidas pelas fases.

## Como rodar

Abra a pasta no **Godot 4.7** (Importar → `project.godot`) e aperte **F5**.

## Controles

| Ação | Teclado | Controle |
|---|---|---|
| Andar | A/D ou ← → | Analógico / direcional |
| Pular (segure para ir mais alto) | Espaço ou K | A |
| Dash (segure para ir mais longe) | Shift ou L | B / RB |
| Atirar (segure para carregar) | J | X |
| Trocar de arma | Q / E | LB / RB (botões 9/10) |
| Pausa (escolher arma, sair da fase) | Esc ou P | Start |
| Tela cheia | F11 | |

Correndo, o canhão vai apontado para a frente. **Pular correndo** vira **cambalhota** (o corpo encolhe e gira no ar; atirar desfaz a cambalhota). Pular durante o dash = **dash-pulo** (velocidade alta no ar). Caindo encostada numa parede, segure em direção a ela para **deslizar**; pule para **saltar da parede** (com o dash segurado, o salto sai rápido).

## O que já existe

- **Sentinela:** corrida, pulo variável, dash, dash-pulo, parede, tiro com **carga em 2 níveis** (até 3 tiros curtos na tela; a rajada carregada atravessa quem derruba), rastro no dash, dano com empurrão e invencibilidade, morte com explosão de energia.
- **Poderes e fraquezas:** os 8 poderes e o ciclo de fraquezas estão em `scripts/game.gd`. O poder certo fere um Guardião **4 vezes mais** e o faz cambalear. Já funcionando: **Ferrão de Âmbar** (persegue o inimigo mais próximo).
- **Armadura rúnica** (relicários escondidos): **Botas do Vento** (dash no ar), **Braçadeiras Rúnicas** (carga mais forte; poderes dos Guardiões também carregam), **Peitoral de Prata-Lunar** (metade do dano) e **Elmo do Vidente** (a fazer). **Sementes da Vida**: +2 de vida máxima.
- **Inimigos:** Rastejante (besouro que cospe ácido em arco), Zumbidor (inseto que mergulha), Bulbo (flor fechada que rebate tiros e, aberta, cospe esporos). *Ainda com a arte antiga.*
- **Fases:**
  - **Ruínas de Aelindor** (abertura): cantaria élfica com musgo e entalhes dourados, galhos vivos como plataforma, floresta escura ao fundo. Ensina abismo, dash-pulo e parede; Semente no alto de uma coluna; relicário das **Botas**.
  - **Colmeia da Árvore-Mãe** (Vespa de Âmbar): favos de âmbar dentro do tronco gigante, chaminé com Semente, túnel de Zumbidores, relicário das **Braçadeiras**, porta e arena do Guardião.
- **Chefe:** **Vespa de Âmbar**: investida na sua altura, leque de ferrões, mergulho com estilhaços; fúria na metade da vida. Fraqueza: Martelo Rúnico. Ensina o Ferrão de Âmbar.
- **Telas:** título (noite na floresta, vaga-lumes e folhas caindo), **seleção dos 8 Guardiões** (as fases ainda não feitas avisam "em construção"), barras de vida e energia, barra do chefe, "arma absorvida", pausa com troca de poder.
- **Checkpoints**, espinhos e abismos que matam na hora (recomeça do último checkpoint), salvamento automático (`user://save.json`).
- **Sons** sintetizados na hora (`scripts/sfx.gd`); para trocar por arquivos, ponha `res://audio/sfx/<nome>.ogg`.

## Os oito Guardiões

| Guardião | Fase | Poder | Fraqueza |
|---|---|---|---|
| Vespa de Âmbar ✅ | Colmeia da Árvore-Mãe | Ferrão de Âmbar | Martelo Rúnico |
| Escaravelho Rúnico | Pedreira dos Ancestrais | Martelo Rúnico | Maré das Ninfeias |
| Serpente do Lago | Lago das Ninfeias | Maré das Ninfeias | Galhada Trovejante |
| Cervo Trovejante | Clareira das Tempestades | Galhada Trovejante | Nuvem de Esporos |
| Dríade Fúngica | Pântano dos Cogumelos | Nuvem de Esporos | Escama de Brasa |
| Salamandra de Brasa | Bosque Incendiado | Escama de Brasa | Lâmina de Geada |
| Louva-a-deus de Geada | Bosque Invernal | Lâmina de Geada | Pó Lunar |
| Mariposa Lunar | Gruta da Lua | Pó Lunar | Ferrão de Âmbar |

(Os nomes internos no código continuam os antigos — `wasp`, `plasma_sting`... — para não quebrar o salvamento.)

## Elyra em alta resolução (animação recortada)

A protagonista já usa **arte em alta resolução com animação recortada (cutout)**: peças vetoriais com volume, gradientes e luz de recorte (`tools/hd_parts.py` → `art/hd/vex_parts/`): elmo élfico com aletas de orelha, crista em folha, visor amendoado verde e cabelo prateado; armadura marfim e dourada; manopla com cristal de esmeralda, presas num esqueleto em `scenes/player/hd_hero.gd`. Cada articulação vai **suavemente** de uma pose para a outra a cada quadro, então correr, parar, pular, pousar e virar fluem sem "pulos" entre quadros. Prévias em GIF fora do Godot: `python tools/hd_rig.py run saida.gif` (mesmas poses). Um artista pode repintar as peças mantendo tamanho e pivô.

## Arte HD (em preparação)

A direção de arte definitiva é **2D pintada em alta resolução** (no estilo de *Afterimage*). O jogo já está pronto para recebê-la: personagens (`art/hd/<nome>/`), blocos do mapa (`art/hd/tiles/<bioma>.png`) e fundos em camadas (`art/hd/backgrounds/<bioma>/`) **substituem sozinhos** a pixel art provisória quando os arquivos existem. Tudo o que o artista precisa (estilo, tamanhos, animações, nomes de arquivo, prioridades) está em **[docs/ARTE_HD.md](docs/ARTE_HD.md)**. Ao exportar o jogo, inclua `*.cfg` no filtro de arquivos não-recurso (para os `info.cfg`).

## Como o projeto é feito

```
project.godot            Configuração e controles
scripts/game.gd          Estado global (autoload "Game"): Guardiões, poderes, fraquezas, armadura, salvamento
scripts/sfx.gd           Efeitos sonoros sintetizados (autoload "Sfx")
scripts/effects.gd       Explosões, orbes e faíscas
scripts/sprite_data.gd   Dados das animações (gerado)
scenes/player/           Sentinela, sprite com braço-canhão e os tiros
scenes/enemies/          Inimigos (base em enemy.gd) e projéteis
scenes/bosses/           Guardiões (base em boss.gd) — Vespa de Âmbar
scenes/level/            Fase montada pelo mapa em texto, tiles, fundo, itens
scenes/ui/               Título, seleção de fases e HUD
levels/                  Mapas das fases (texto; legenda em scenes/level/level.gd)
art/                     Sprites e tiles em pixel art (gerados)
tools/                   Geradores: sprites, tiles e mapas das fases
```

- **Fases em texto:** cada fase é uma grade de caracteres (`#` bloco, `=` plataforma vazada, `^` espinhos, `c f t` inimigos, `L` Semente da Vida, `A` relicário, `D` porta do chefe...). `tools/build_levels.py` monta os mapas com retângulos e marcadores; dá para editar os `.gd` de `levels/` direto também.
- **Estilo de arte:** protagonista em HD recortada (acima); cenário em pixel art gerada (`tools/generate_tiles.py`: pedra élfica, galhos, floresta, âmbar). Os desenhos antigos em pixel art ficam em `tools/suit.py` e `tools/handmade.py`.
- **Arte:** `tools/generate_sprites.py` (personagens) e `tools/generate_tiles.py` (cenário) geram a pixel art (`pip install pillow numpy`).

## Próximos passos

- [ ] Inimigos e Vespa no tema élfico (arte nova)
- [ ] Os outros 7 Guardiões, suas fases e poderes
- [ ] Elmo do Vidente, Sementes e relicários nas novas fases
- [ ] Fortaleza final
- [ ] Música
