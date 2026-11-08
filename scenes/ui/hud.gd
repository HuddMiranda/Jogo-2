extends CanvasLayer
## Interface da fase: barra de vida vertical (com a energia da arma ao lado,
## na cor dela), barra do chefe à direita, nome da arma ao trocar, avisos no
## centro (título da fase, chegada do chefe, itens), a tela de "arma
## absorvida" e o menu de pausa (escolher arma, ver as relíquias, sair).

signal weapon_get_closed

const FRAME := Color(0.05, 0.05, 0.08)
const LIFE := Color(0.55, 1.0, 0.7)
const SEGMENT := 3.0

var _boss_health := 0
var _boss_max := 0
var _boss_visible := false
var _weapon_label: Label
var _weapon_tween: Tween
var _center: Label
var _sub: Label
var _center_tween: Tween
var _bars: Control
var _pause: Control
var _pause_list: VBoxContainer
var _pause_index := 0
var _waiting_weapon := false


func _ready() -> void:
	layer = 10
	process_mode = Node.PROCESS_MODE_ALWAYS
	add_to_group("hud")
	_bars = Control.new()
	_bars.set_anchors_preset(Control.PRESET_FULL_RECT)
	_bars.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_bars.draw.connect(_draw_bars)
	add_child(_bars)
	_weapon_label = _label(14, HORIZONTAL_ALIGNMENT_LEFT)
	_weapon_label.position = Vector2(48, 14)
	_weapon_label.modulate.a = 0.0
	_center = _label(24, HORIZONTAL_ALIGNMENT_CENTER)
	_center.position = Vector2(0, 130)
	_center.size = Vector2(640, 40)
	_center.modulate.a = 0.0
	_sub = _label(12, HORIZONTAL_ALIGNMENT_CENTER)
	_sub.position = Vector2(0, 168)
	_sub.size = Vector2(640, 24)
	_sub.modulate.a = 0.0
	_build_pause()
	Game.health_changed.connect(func(_c: int, _m: int) -> void: _bars.queue_redraw())
	Game.energy_changed.connect(func(_w: StringName, _c: int, _m: int) -> void: _bars.queue_redraw())
	Game.weapon_changed.connect(_on_weapon_changed)
	Game.boss_fight_started.connect(func(_name: String) -> void:
		_boss_visible = true
		_bars.queue_redraw())
	Game.boss_fight_ended.connect(func() -> void:
		_boss_visible = false
		_bars.queue_redraw())
	Game.boss_health_changed.connect(func(current: int, maximum: int) -> void:
		_boss_health = current
		_boss_max = maximum
		_bars.queue_redraw())


func _label(font_size: int, align: HorizontalAlignment) -> Label:
	var label := Label.new()
	label.horizontal_alignment = align
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_outline_color", Color.BLACK)
	label.add_theme_constant_override("outline_size", 4)
	add_child(label)
	return label


# --- Barras -----------------------------------------------------------------------

func _draw_bars() -> void:
	var maximum := Game.max_health()
	_bar(Vector2(16, 40), Game.health, maximum, LIFE, "V")
	if Game.current_weapon != Game.BUSTER:
		_bar(Vector2(30, 40), Game.weapon_energy(Game.current_weapon), Game.MAX_ENERGY, Game.weapon_color(), "")
	if _boss_visible and _boss_max > 0:
		_bar(Vector2(612, 40), _boss_health, _boss_max, Color(1.0, 0.45, 0.35), "")


func _bar(at: Vector2, value: int, maximum: int, color: Color, tag: String) -> void:
	var height := maximum * SEGMENT
	var frame := Rect2(at, Vector2(12, height + 4))
	_bars.draw_rect(frame.grow(2), FRAME)
	_bars.draw_rect(frame, Color(0.12, 0.12, 0.16))
	for i in value:
		var y := at.y + height - (i + 1) * SEGMENT + 2
		_bars.draw_rect(Rect2(at.x + 2, y, 8, SEGMENT - 1), color)
		_bars.draw_rect(Rect2(at.x + 2, y, 2, SEGMENT - 1), color.lightened(0.5))
	if tag != "":
		_bars.draw_rect(Rect2(at.x - 2, at.y + height + 8, 16, 12), FRAME)
		_bars.draw_string(ThemeDB.fallback_font, Vector2(at.x + 1, at.y + height + 18), tag,
				HORIZONTAL_ALIGNMENT_LEFT, -1, 10, color)


func _on_weapon_changed(weapon: StringName) -> void:
	_weapon_label.text = Game.WEAPONS[weapon]["name"]
	_weapon_label.add_theme_color_override("font_color", Game.weapon_color(weapon))
	if _weapon_tween:
		_weapon_tween.kill()
	_weapon_label.modulate.a = 1.0
	_weapon_tween = create_tween()
	_weapon_tween.tween_interval(1.2)
	_weapon_tween.tween_property(_weapon_label, "modulate:a", 0.0, 0.4)
	_bars.queue_redraw()


# --- Avisos -------------------------------------------------------------------------

func announce(title: String, text: String, seconds := 2.5) -> void:
	_center.text = title
	_sub.text = text
	if _center_tween:
		_center_tween.kill()
	_center.modulate.a = 1.0
	_sub.modulate.a = 1.0
	_center_tween = create_tween()
	_center_tween.tween_interval(seconds)
	_center_tween.tween_property(_center, "modulate:a", 0.0, 0.4)
	_center_tween.parallel().tween_property(_sub, "modulate:a", 0.0, 0.4)


func show_title(level_name: String) -> void:
	announce(level_name.to_upper(), "PRONTA!", 1.8)


func boss_intro(boss_name: String) -> void:
	announce(boss_name.to_upper(), "", 1.4)


func weapon_get(weapon_name: String, color: Color) -> void:
	_center.add_theme_color_override("font_color", color)
	_center.text = "ARMA ABSORVIDA"
	_sub.text = weapon_name + "     (aperte Pular para continuar)"
	if _center_tween:
		_center_tween.kill()
	_center.modulate.a = 1.0
	_sub.modulate.a = 1.0
	await get_tree().create_timer(1.0).timeout
	_waiting_weapon = true


# --- Pausa ---------------------------------------------------------------------------

func _build_pause() -> void:
	_pause = Control.new()
	_pause.set_anchors_preset(Control.PRESET_FULL_RECT)
	_pause.visible = false
	add_child(_pause)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.75)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	_pause.add_child(dim)
	_pause_list = VBoxContainer.new()
	_pause_list.position = Vector2(200, 60)
	_pause_list.size = Vector2(240, 240)
	_pause_list.add_theme_constant_override("separation", 4)
	_pause.add_child(_pause_list)


func _unhandled_input(event: InputEvent) -> void:
	if _waiting_weapon and (event.is_action_pressed("jump") or event.is_action_pressed("confirm")):
		_waiting_weapon = false
		weapon_get_closed.emit()
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("pause"):
		_toggle_pause()
		get_viewport().set_input_as_handled()
	elif _pause.visible:
		var options := Game.weapons.size() + 1
		if event.is_action_pressed("move_down"):
			_pause_index = (_pause_index + 1) % options
			Sfx.play(&"menu_move")
			_refresh_pause()
		elif event.is_action_pressed("move_up"):
			_pause_index = posmod(_pause_index - 1, options)
			Sfx.play(&"menu_move")
			_refresh_pause()
		elif event.is_action_pressed("confirm") or event.is_action_pressed("shoot"):
			Sfx.play(&"menu_select")
			if _pause_index < Game.weapons.size():
				Game.select_weapon(Game.weapons[_pause_index])
				_toggle_pause()
			else:
				Game.checkpoint = Vector2.ZERO
				Game.go_to_stage_select()
		get_viewport().set_input_as_handled()


func _toggle_pause() -> void:
	_pause.visible = not _pause.visible
	get_tree().paused = _pause.visible
	Sfx.play(&"menu_select" if _pause.visible else &"menu_move")
	if _pause.visible:
		_pause_index = maxi(Game.weapons.find(Game.current_weapon), 0)
		_refresh_pause()


func _refresh_pause() -> void:
	for child in _pause_list.get_children():
		child.queue_free()
	var title := Label.new()
	title.text = "ARMAS"
	title.add_theme_font_size_override("font_size", 16)
	_pause_list.add_child(title)
	for i in Game.weapons.size():
		var weapon: StringName = Game.weapons[i]
		var row := Label.new()
		var energy := "" if weapon == Game.BUSTER else "   %d/%d" % [Game.weapon_energy(weapon), Game.MAX_ENERGY]
		row.text = ("▶ " if i == _pause_index else "   ") + Game.WEAPONS[weapon]["name"] + energy
		row.add_theme_color_override("font_color", Game.weapon_color(weapon) if i == _pause_index else Color(0.7, 0.7, 0.75))
		_pause_list.add_child(row)
	var leave := Label.new()
	leave.text = ("▶ " if _pause_index == Game.weapons.size() else "   ") + "Sair para a seleção de fases"
	_pause_list.add_child(leave)
	var armor := Label.new()
	var parts: Array[String] = []
	for part: StringName in Game.armor:
		parts.append(Game.ARMOR[part]["name"])
	armor.text = "\nARMADURA: " + (", ".join(parts) if not parts.is_empty() else "nenhuma peça ainda") \
			+ "\nCORAÇÕES: %d" % Game.hearts.size()
	armor.add_theme_font_size_override("font_size", 11)
	armor.add_theme_color_override("font_color", Color(0.6, 0.65, 0.7))
	_pause_list.add_child(armor)
