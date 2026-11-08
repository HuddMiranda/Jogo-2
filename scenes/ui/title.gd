extends Control
## Tela de título: Novo jogo / Continuar. Um jogo novo (ou um salvamento que
## ainda não passou da abertura) começa pela fase de abertura; depois dela,
## vem a seleção de fases.

const INTRO_LEVEL := "res://levels/intro.gd"

var _options: Array[String] = []
var _index := 0
var _time := 0.0


func _ready() -> void:
	_options = ["Continuar", "Novo jogo"] if Game.has_save() else ["Novo jogo"]


func _process(delta: float) -> void:
	_time += delta
	queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("move_down") or event.is_action_pressed("move_up"):
		_index = (_index + 1) % _options.size()
		Sfx.play(&"menu_move")
	elif event.is_action_pressed("confirm") or event.is_action_pressed("jump"):
		Sfx.play(&"menu_select")
		if _options[_index] == "Novo jogo":
			Game.new_game()
		if Game.intro_cleared:
			Game.go_to_stage_select()
		else:
			Game.start_level(INTRO_LEVEL)


func _draw() -> void:
	draw_rect(Rect2(0, 0, 640, 360), Color(0.02, 0.02, 0.04))
	# Veios pulsando no fundo.
	for i in 14:
		var x := fmod(i * 53.0 + _time * 12.0, 680.0) - 20.0
		var glow := 0.15 + 0.1 * sin(_time * 2.0 + i)
		draw_line(Vector2(x, 0), Vector2(x - 80, 360), Color(0.48, 1.0, 0.88, glow), 2.0)
	var font := ThemeDB.fallback_font
	draw_string(font, Vector2(0, 120), "SIMBIONTE", HORIZONTAL_ALIGNMENT_CENTER, 640, 48, Color(0.48, 1.0, 0.88))
	draw_string(font, Vector2(0, 150), "a caçada das oito Bestas", HORIZONTAL_ALIGNMENT_CENTER, 640, 14, Color(0.75, 0.75, 0.8))
	for i in _options.size():
		var selected := i == _index
		var text := ("▶ " if selected else "  ") + _options[i]
		draw_string(font, Vector2(0, 230 + i * 24), text, HORIZONTAL_ALIGNMENT_CENTER, 640, 16,
				Color.WHITE if selected else Color(0.55, 0.55, 0.6))
	draw_string(font, Vector2(0, 345), "Setas: mover   J: atirar   Espaço: pular   Shift: dash   Q/E: armas   Esc: pausa",
			HORIZONTAL_ALIGNMENT_CENTER, 640, 10, Color(0.5, 0.5, 0.55))
