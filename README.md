# Simbionte

Ação e plataforma **frenética** em pixel art 32 bits, feita em **Godot 4**, no gênero dos run-and-gun com seleção de chefes: escolha a fase, vença a Besta, absorva a arma dela e use-a contra a Besta que é fraca a ela. (O nome é provisório.)

**Premissa:** no planeta Ossária, as oito **Bestas-Simbionte**, criaturas bio-mecânicas que guardavam o ecossistema, enlouqueceram. **VEX-9**, caçadora de armadura simbionte, vai atrás de cada uma. Sua armadura absorve a arma de cada Besta vencida, e peças dela e Corações Simbiontes estão escondidos pelas fases.

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

- **Caçadora:** corrida, pulo variável, dash, dash-pulo, parede, tiro com **carga em 2 níveis** (até 3 tiros curtos na tela; a rajada carregada atravessa quem derruba), rastro no dash, dano com empurrão e invencibilidade, morte com explosão de energia.
- **Armas e fraquezas:** as 8 armas e o ciclo de fraquezas estão definidos em `scripts/game.gd`. A arma certa fere uma Besta **4 vezes mais** e a faz cambalear. Já funcionando: **Ferrão de Plasma** (persegue o inimigo mais próximo).
- **Armadura simbionte** (casulos escondidos): **Pernas Saltadoras** (dash no ar), **Braços Condutores** (carga mais forte; armas das Bestas também carregam), **Carapaça Densa** (metade do dano) e **Elmo Sensorial** (a fazer). **Corações Simbiontes**: +2 de vida máxima.
- **Inimigos:** Rastejante (besouro que cospe ácido em arco), Zumbidor (inseto que mergulha), Bulbo (casulo que rebate tiros fechado e cospe esporos aberto).
- **Fases:**
  - **Ruínas da Nave-Semente** (abertura): ensina abismo, dash-pulo e parede; Coração no alto de uma coluna; casulo das **Pernas**.
  - **Colmeia de Plasma** (Vespa de Plasma): favos sobre espinhos, chaminé com Coração, túnel de Zumbidores, casulo dos **Braços**, porta e arena da Besta.
- **Chefe:** **Vespa de Plasma**: investida na sua altura, leque de ferrões, mergulho com estilhaços; fúria na metade da vida. Fraqueza: Martelo Sísmico. Ensina o Ferrão de Plasma.
- **Telas:** título, **seleção das 8 Bestas** (as fases ainda não feitas avisam "em construção"), barra de vida e de energia da arma, barra do chefe, "arma absorvida", pausa com troca de arma.
- **Checkpoints**, espinhos e abismos que matam na hora (recomeça do último checkpoint), salvamento automático (`user://save.json`).
- **Sons** sintetizados na hora (`scripts/sfx.gd`); para trocar por arquivos, ponha `res://audio/sfx/<nome>.ogg`.

## As oito Bestas

| Besta | Fase | Arma | Fraqueza |
|---|---|---|---|
| Vespa de Plasma ✅ | Colmeia de Plasma | Ferrão de Plasma | Martelo Sísmico |
| Escaravelho Tectônico | Falha Tectônica | Martelo Sísmico | Jato Abissal |
| Lula Abissal | Fossa Abissal | Jato Abissal | Descarga Voltaica |
| Raia Elétrica | Recife Voltaico | Descarga Voltaica | Nuvem de Esporos |
| Fungo Esporífero | Pântano de Esporos | Nuvem de Esporos | Casco de Magma |
| Caracol Vulcânico | Caldeira Vulcânica | Casco de Magma | Lâmina Glacial |
| Louva-a-deus Glacial | Geleira Fóssil | Lâmina Glacial | Pó Prismático |
| Mariposa de Cristal | Caverna Prismática | Pó Prismático | Ferrão de Plasma |

## VEX-9 em alta resolução (animação recortada)

A protagonista já usa **arte em alta resolução com animação recortada (cutout)**: peças vetoriais com volume, gradientes e luz de recorte (`tools/hd_parts.py` → `art/hd/vex_parts/`) presas num esqueleto em `scenes/player/hd_hero.gd`. Cada articulação vai **suavemente** de uma pose para a outra a cada quadro, então correr, parar, pular, pousar e virar fluem sem "pulos" entre quadros. Prévias em GIF fora do Godot: `python tools/hd_rig.py run saida.gif` (mesmas poses). Um artista pode repintar as peças mantendo tamanho e pivô.

## Arte HD (em preparação)

A direção de arte definitiva é **2D pintada em alta resolução** (no estilo de *Afterimage*). O jogo já está pronto para recebê-la: personagens (`art/hd/<nome>/`), blocos do mapa (`art/hd/tiles/<bioma>.png`) e fundos em camadas (`art/hd/backgrounds/<bioma>/`) **substituem sozinhos** a pixel art provisória quando os arquivos existem. Tudo o que o artista precisa (estilo, tamanhos, animações, nomes de arquivo, prioridades) está em **[docs/ARTE_HD.md](docs/ARTE_HD.md)**. Ao exportar o jogo, inclua `*.cfg` no filtro de arquivos não-recurso (para os `info.cfg`).

## Como o projeto é feito

```
project.godot            Configuração e controles
scripts/game.gd          Estado global (autoload "Game"): Bestas, armas, fraquezas, armadura, salvamento
scripts/sfx.gd           Efeitos sonoros sintetizados (autoload "Sfx")
scripts/effects.gd       Explosões, orbes e faíscas
scripts/sprite_data.gd   Dados das animações (gerado)
scenes/player/           Caçadora, sprite com braço-canhão e os tiros
scenes/enemies/          Inimigos (base em enemy.gd) e projéteis
scenes/bosses/           Bestas (base em boss.gd) — Vespa de Plasma
scenes/level/            Fase montada pelo mapa em texto, tiles, fundo, itens
scenes/ui/               Título, seleção de fases e HUD
levels/                  Mapas das fases (texto; legenda em scenes/level/level.gd)
art/                     Sprites e tiles em pixel art (gerados)
tools/                   Geradores: sprites, tiles e mapas das fases
```

- **Fases em texto:** cada fase é uma grade de caracteres (`#` bloco, `=` plataforma vazada, `^` espinhos, `c f t` inimigos, `L` Coração, `A` casulo, `D` porta do chefe...). `tools/build_levels.py` monta os mapas com retângulos e marcadores; dá para editar os `.gd` de `levels/` direto também.
- **Estilo de arte:** pixel art de console. A VEX-9 (paleta **Marfim**, proporções humanas, capacete anguloso com visor em fenda, cada segmento do corpo com contorno próprio) é montada por peças desenhadas à mão em `tools/suit.py`: peças rígidas (capacete, ombreiras, tronco, quadril, joelheiras, pés, braço-canhão) copiadas pixel a pixel do desenho aprovado e membros traçados em cada pose com sombreado em faixas. `tools/handmade.py` guarda os desenhos em grade de letras (uma letra = um pixel) e as três paletas.
- **Arte:** `tools/generate_sprites.py` (personagens) e `tools/generate_tiles.py` (cenário) geram a pixel art (`pip install pillow numpy`).

## Próximos passos

- [ ] As outras 7 Bestas, suas fases e armas
- [ ] Elmo Sensorial, Corações e casulos nas novas fases
- [ ] Fortaleza final
- [ ] Música
