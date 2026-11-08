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
	# Noite na floresta élfica: céu, lua, silhuetas de árvores, vagalumes e folhas caindo.
	for i in 18:
		var t := float(i) / 17.0
		draw_rect(Rect2(0, i * 20, 640, 20), Color(0.02, 0.05 + t * 0.05, 0.08 + t * 0.03).lerp(Color(0.03, 0.08, 0.06), t))
	draw_circle(Vector2(470, 70), 46, Color(0.75, 0.95, 0.85, 0.08))
	draw_circle(Vector2(470, 70), 30, Color(0.9, 0.97, 0.88, 0.9))
	draw_circle(Vector2(480, 64), 26, Color(0.82, 0.92, 0.84, 0.6))
	for i in 9:
		var x := i * 80.0 - 20.0 + fmod(i * 37.0, 30.0)
		var w := 14.0 + fmod(i * 13.0, 10.0)
		var shade := Color(0.01, 0.03, 0.03) if i % 2 else Color(0.02, 0.05, 0.05)
		draw_rect(Rect2(x, 0, w, 360), shade)
		draw_circle(Vector2(x + w * 0.5, 40 + fmod(i * 29.0, 40.0)), 50.0, shade)
	for i in 24:
		var phase := _time * 0.7 + i * 1.7
		var pos := Vector2(fmod(i * 97.0 + sin(phase) * 20.0, 640.0), 200.0 + fmod(i * 53.0, 150.0) + cos(phase * 1.3) * 10.0)
		var glow := 0.4 + 0.4 * sin(_time * 3.0 + i)
		draw_circle(pos, 3.0, Color(0.7, 1.0, 0.5, glow * 0.25))
		draw_circle(pos, 1.0, Color(0.9, 1.0, 0.7, glow))
	for i in 16:
		var y := fmod(i * 41.0 + _time * (18.0 + i % 4 * 6.0), 380.0) - 10.0
		var x := fmod(i * 71.0, 640.0) + sin(_time * 1.5 + i) * 14.0
		var leaf := Transform2D(_time * 2.0 + i, Vector2(x, y))
		draw_set_transform_matrix(leaf)
		draw_colored_polygon(PackedVector2Array([Vector2(-4, 0), Vector2(0, -2), Vector2(4, 0), Vector2(0, 2)]),
				Color(0.85, 0.65, 0.2, 0.8) if i % 3 == 0 else Color(0.4, 0.75, 0.35, 0.8))
	draw_set_transform_matrix(Transform2D.IDENTITY)
	var font := ThemeDB.fallback_font
	draw_string(font, Vector2(0, 122), "SYLVARIA", HORIZONTAL_ALIGNMENT_CENTER, 640, 48, Color(0.06, 0.1, 0.06))
	draw_string(font, Vector2(0, 120), "SYLVARIA", HORIZONTAL_ALIGNMENT_CENTER, 640, 48, Color(0.95, 0.82, 0.45))
	draw_string(font, Vector2(0, 150), "a purificação dos oito Guardiões", HORIZONTAL_ALIGNMENT_CENTER, 640, 14, Color(0.7, 0.9, 0.75))
	for i in _options.size():
		var selected := i == _index
		var text := ("▶ " if selected else "  ") + _options[i]
		draw_string(font, Vector2(0, 230 + i * 24), text, HORIZONTAL_ALIGNMENT_CENTER, 640, 16,
				Color.WHITE if selected else Color(0.55, 0.65, 0.6))
	draw_string(font, Vector2(0, 345), "Setas: mover   J: atirar   Espaço: pular   Shift: dash   Q/E: poderes   Esc: pausa",
			HORIZONTAL_ALIGNMENT_CENTER, 640, 10, Color(0.5, 0.6, 0.55))
