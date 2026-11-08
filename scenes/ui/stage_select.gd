extends Control
## Seleção de fases: as oito Bestas-Simbionte em volta da caçadora (3 × 3).
## Setas escolhem, Pular / Enter entra na fase. Bestas vencidas ficam
## apagadas, mas a fase pode ser jogada de novo (para buscar itens).

const CELL := Vector2(150, 96)
const ORIGIN := Vector2(95, 40)
## Posição de cada Besta na grade (o meio é a caçadora).
const SLOTS := [Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 0), Vector2i(2, 1),
		Vector2i(2, 2), Vector2i(1, 2), Vector2i(0, 2), Vector2i(0, 1)]

var _index := 0
var _time := 0.0
var _message := ""
var _message_time := 0.0
var _hero: Texture2D
var _wasp: Texture2D


func _ready() -> void:
	_hero = load("res://art/sprites/hero.png")
	_wasp = load("res://art/sprites/wasp.png")


func _process(delta: float) -> void:
	_time += delta
	_message_time -= delta
	queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
	var slot: Vector2i = SLOTS[_index]
	var move := Vector2i.ZERO
	if event.is_action_pressed("move_left"):
		move = Vector2i.LEFT
	elif event.is_action_pressed("move_right"):
		move = Vector2i.RIGHT
	elif event.is_action_pressed("move_up"):
		move = Vector2i.UP
	elif event.is_action_pressed("move_down"):
		move = Vector2i.DOWN
	if move != Vector2i.ZERO:
		var target := slot + move
		if target == Vector2i(1, 1):
			target += move  # pula o meio (a caçadora)
		var found := SLOTS.find(target)
		if found >= 0:
			_index = found
			Sfx.play(&"menu_move")
	elif event.is_action_pressed("confirm") or event.is_action_pressed("jump"):
		var boss: Dictionary = Game.BOSSES[_index]
		if boss["level"] == "":
			_message = "%s: fase em construção" % boss["stage"]
			_message_time = 2.0
			Sfx.play(&"no_damage")
		else:
			Sfx.play(&"menu_select")
			Game.start_level(boss["level"], boss["id"])
	elif event.is_action_pressed("pause"):
		Game.go_to_title()


func _draw() -> void:
	draw_rect(Rect2(0, 0, 640, 360), Color(0.03, 0.03, 0.06))
	var font := ThemeDB.fallback_font
	draw_string(font, Vector2(0, 26), "ESCOLHA UMA BESTA", HORIZONTAL_ALIGNMENT_CENTER, 640, 18, Color(0.48, 1.0, 0.88))
	for i in SLOTS.size():
		_draw_slot(i, ORIGIN + Vector2(SLOTS[i]) * CELL, font)
	# A caçadora no meio.
	var center := ORIGIN + CELL
	draw_rect(Rect2(center, CELL - Vector2(12, 12)), Color(0.07, 0.12, 0.14))
	if _hero:
		draw_texture_rect_region(_hero, Rect2(center + Vector2(37, 6), Vector2(64, 64)), Rect2(0, 0, 64, 64))
	draw_string(font, center + Vector2(0, 80), "VEX-9", HORIZONTAL_ALIGNMENT_CENTER, CELL.x - 12, 12, Color.WHITE)
	var boss: Dictionary = Game.BOSSES[_index]
	draw_string(font, Vector2(0, 340), "%s  —  %s" % [boss["name"], boss["stage"]], HORIZONTAL_ALIGNMENT_CENTER, 640, 14, boss["color"])
	if _message_time > 0.0:
		draw_string(font, Vector2(0, 356), _message, HORIZONTAL_ALIGNMENT_CENTER, 640, 11, Color(1, 0.8, 0.6))


func _draw_slot(i: int, at: Vector2, font: Font) -> void:
	var boss: Dictionary = Game.BOSSES[i]
	var size := CELL - Vector2(12, 12)
	var done: bool = boss["id"] in Game.defeated
	var color: Color = boss["color"]
	var selected := i == _index
	draw_rect(Rect2(at, size), Color(0.08, 0.07, 0.1))
	draw_rect(Rect2(at, size), color if selected and fmod(_time, 0.5) < 0.35 else Color(color, 0.35), false, 2.0)
	var portrait := Rect2(at + Vector2(size.x / 2 - 30, 6), Vector2(60, 52))
	if boss["id"] == &"wasp" and _wasp:
		draw_texture_rect_region(_wasp, Rect2(portrait.position - Vector2(18, 26), Vector2(96, 96)), Rect2(0, 0, 96, 96),
				Color(0.35, 0.35, 0.35) if done else Color.WHITE)
	else:
		# Silhueta da Besta ainda desconhecida: olhos na cor dela.
		draw_circle(portrait.get_center(), 20, Color(color.darkened(0.7), 1.0))
		for side: float in [-1.0, 1.0]:
			draw_rect(Rect2(portrait.get_center() + Vector2(side * 8 - 3, -4), Vector2(6, 4)), color if not done else Color(0.3, 0.3, 0.3))
	if done:
		draw_line(portrait.position, portrait.end, Color(1, 0.3, 0.3), 2.0)
		draw_line(Vector2(portrait.end.x, portrait.position.y), Vector2(portrait.position.x, portrait.end.y), Color(1, 0.3, 0.3), 2.0)
	draw_string(font, at + Vector2(0, size.y - 8), boss["name"], HORIZONTAL_ALIGNMENT_CENTER, size.x, 10,
			Color.WHITE if selected else Color(0.65, 0.65, 0.7))
