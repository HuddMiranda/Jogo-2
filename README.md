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

Pular durante o dash = **dash-pulo** (velocidade alta no ar). Caindo encostada numa parede, segure em direção a ela para **deslizar**; pule para **saltar da parede** (com o dash segurado, o salto sai rápido).

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
- **Estilo de arte:** volumes arredondados no estilo dos jogos de ação 16/32 bits: esferas e cilindros sombreados em faixas (luz de cima à esquerda, brilho especular, borda escura), cabeça/capacete grandes, ombreiras, antebraços e botas grossas, cintura e coxas finas. As primitivas ficam em `tools/pixel.py` (`ellipse` = esfera, `limb` = cilindro, `rounded` = placa).
- **Arte:** `tools/generate_sprites.py` (personagens) e `tools/generate_tiles.py` (cenário) geram a pixel art (`pip install pillow numpy`).

## Próximos passos

- [ ] As outras 7 Bestas, suas fases e armas
- [ ] Elmo Sensorial, Corações e casulos nas novas fases
- [ ] Fortaleza final
- [ ] Música
