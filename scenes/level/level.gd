extends Node2D
## Uma fase, montada a partir de um mapa em texto (levels/*.gd, constante
## MAP). Cada caractere é um bloco de 16 × 16:
##   #  bloco sólido            =  plataforma vazada (sobe por baixo)
##   ^  espinhos (morte na hora) P  início da sentinela
##   C  checkpoint (renasce aqui) G  fim da fase (fases sem chefe)
##   c  Rastejante   f  Zumbidor   t  Bulbo
##   h  vida pequena H  vida grande e  energia pequena E energia grande
##   L  Semente da Vida             A  relicário (relíquia em ARMOR)
##   D  porta do chefe (coluna)    B  onde o chefe aparece
## Cair abaixo do mapa também mata. A câmera fica presa dentro do mapa e, na
## arena do chefe, presa à arena.

const T := 16
const PLAYER_SCENE := preload("res://scenes/player/player.tscn")
const ENEMIES := {
	"c": preload("res://scenes/enemies/crawler.tscn"),
	"f": preload("res://scenes/enemies/flyer.tscn"),
	"t": preload("res://scenes/enemies/turret.tscn"),
}
const BOSS_SCENES := {
	&"wasp": preload("res://scenes/bosses/wasp.tscn"),
}
const PICKUP_SCENE := preload("res://scenes/level/pickup.tscn")
const ITEMS := {"h": "health_small", "H": "health_big", "e": "energy_small", "E": "energy_big"}

var grid: Array[String] = []
var width := 0
var height := 0
var biome := "ruins"
var level_name := ""

var player: Player
var boss: Boss
var _start := Vector2.ZERO
var _checkpoints: Array[Vector2] = []
var _goal_x := -1.0
var _door_cells: Array[Vector2i] = []
var _door_body: StaticBody2D
var _door_open := 0.0
var _door_state := 0  # 0 fechada, 1 abrindo (entrando), 2 trancada atrás
var _boss_cell := Vector2i(-1, -1)
var _finished := false

@onready var _world: Node2D = $World
@onready var _tiles: Node2D = $Tiles
@onready var _hud: CanvasLayer = $HUD


func _ready() -> void:
	var data := load(Game.current_level) as GDScript
	var constants := data.get_script_constant_map()
	level_name = constants.get("NAME", "Fase")
	biome = constants.get("BIOME", "ruins")
	var lines: PackedStringArray = String(constants["MAP"]).strip_edges(false, true).split("\n")
	while lines.size() > 0 and lines[0].strip_edges() == "":
		lines.remove_at(0)
	for line in lines:
		width = maxi(width, line.length())
	for line in lines:
		grid.append(line.rpad(width))
	height = grid.size()
	_tiles.set("level", self)
	_build_collision()
	_spawn_entities(constants)
	_spawn_player()
	$BackgroundLayer/Background.set("biome", biome)
	_hud.call("show_title", level_name)


# --- Mapa -----------------------------------------------------------------------

func cell(x: int, y: int) -> String:
	if y < 0 or y >= height or x < 0 or x >= width:
		return "#" if y >= 0 and (x < 0 or x >= width) else " "
	return grid[y][x]


func is_solid(x: int, y: int) -> bool:
	return cell(x, y) == "#"


func _build_collision() -> void:
	var solid := StaticBody2D.new()
	solid.name = "Solid"
	var one_way := StaticBody2D.new()
	one_way.name = "OneWay"
	var spikes := Area2D.new()
	spikes.name = "Spikes"
	spikes.collision_layer = 0
	spikes.collision_mask = 2
	spikes.body_entered.connect(func(body: Node) -> void:
		if body is Player:
			(body as Player).die())
	# Blocos sólidos: faixas horizontais, unidas na vertical quando iguais.
	var open_rects := {}  # Vector2i(x1, x2) -> linha inicial
	for y in height + 1:
		var runs := _runs(y, "#") if y < height else []
		var keep := {}
		for run: Vector2i in runs:
			keep[run] = true
			if not open_rects.has(run):
				open_rects[run] = y
		for run: Vector2i in open_rects.keys():
			if not keep.has(run):
				_add_rect(solid, Rect2(run.x * T, open_rects[run] * T, (run.y - run.x) * T, (y - open_rects[run]) * T))
				open_rects.erase(run)
	for y in height:
		for run: Vector2i in _runs(y, "="):
			var shape := _add_rect(one_way, Rect2(run.x * T, y * T, (run.y - run.x) * T, 6))
			shape.one_way_collision = true
		for run: Vector2i in _runs(y, "^"):
			_add_rect(spikes, Rect2(run.x * T + 2, y * T + 8, (run.y - run.x) * T - 4, 8))
	add_child(solid)
	add_child(one_way)
	add_child(spikes)


func _runs(y: int, kind: String) -> Array:
	var result := []
	var x := 0
	while x < width:
		if grid[y][x] == kind:
			var start := x
			while x < width and grid[y][x] == kind:
				x += 1
			result.append(Vector2i(start, x))
		else:
			x += 1
	return result


func _add_rect(body: CollisionObject2D, rect: Rect2) -> CollisionShape2D:
	var shape := CollisionShape2D.new()
	var box := RectangleShape2D.new()
	box.size = rect.size
	shape.shape = box
	shape.position = rect.get_center()
	body.add_child(shape)
	return shape


func _cell_bottom(x: int, y: int) -> Vector2:
	return Vector2(x * T + T / 2.0, (y + 1) * T)


func _spawn_entities(constants: Dictionary) -> void:
	var heart_index := 0
	for y in height:
		for x in width:
			var c := grid[y][x]
			var at := _cell_bottom(x, y)
			match c:
				"P":
					_start = at
				"C":
					_checkpoints.append(at)
				"G":
					_goal_x = at.x
				"D":
					_door_cells.append(Vector2i(x, y))
				"B":
					_boss_cell = Vector2i(x, y)
				"L":
					heart_index += 1
					_pickup("heart", at, "%s:heart%d" % [Game.current_level, heart_index])
				"A":
					var pickup := _pickup("capsule", at, "%s:armor" % Game.current_level)
					pickup.armor_part = constants.get("ARMOR", &"legs")
				_:
					if ENEMIES.has(c):
						var enemy := ENEMIES[c].instantiate() as Node2D
						_world.add_child(enemy)
						enemy.global_position = at
					elif ITEMS.has(c):
						_pickup(ITEMS[c], at, "")
	if not _door_cells.is_empty():
		_door_body = StaticBody2D.new()
		for door in _door_cells:
			_add_rect(_door_body, Rect2(door.x * T, door.y * T, T, T))
		add_child(_door_body)
	if _boss_cell.x >= 0 and BOSS_SCENES.has(Game.current_boss) and Game.current_boss not in Game.defeated:
		boss = BOSS_SCENES[Game.current_boss].instantiate() as Boss
		_world.add_child(boss)
		boss.global_position = _cell_bottom(_boss_cell.x, _boss_cell.y)
		boss.visible = false
		boss.arena = _arena_rect()
		boss.defeated.connect(_on_boss_defeated)


func _pickup(kind: String, at: Vector2, id: String) -> Pickup:
	var pickup := PICKUP_SCENE.instantiate() as Pickup
	pickup.kind = kind
	pickup.item_id = id
	_world.add_child(pickup)
	pickup.global_position = at
	return pickup


func _arena_rect() -> Rect2:
	var left := (_door_cells[0].x + 1) * T if not _door_cells.is_empty() else 0
	return Rect2(left, 0, width * T - left, height * T - 3 * T)


# --- Sentinela, câmera e morte --------------------------------------------------------

func _spawn_player() -> void:
	player = PLAYER_SCENE.instantiate() as Player
	_world.add_child(player)
	var spawn := Game.checkpoint if Game.checkpoint != Vector2.ZERO else _start
	player.global_position = spawn
	player.died.connect(_on_player_died)
	var camera := player.get_node("Camera2D") as Camera2D
	camera.limit_left = 0
	camera.limit_top = 0
	camera.limit_right = width * T
	camera.limit_bottom = height * T
	camera.reset_smoothing()
	Game.set_health(Game.max_health())


func _physics_process(delta: float) -> void:
	if player == null or player.is_dead() or _finished:
		return
	var p := player.global_position
	# Abismo.
	if p.y > height * T + 40.0:
		player.die()
		return
	# Checkpoints: o mais à direita já alcançado.
	for point in _checkpoints:
		if p.x >= point.x and point.x > Game.checkpoint.x:
			Game.checkpoint = point
	# Fim da fase (sem chefe).
	if _goal_x > 0.0 and p.x >= _goal_x:
		_finish_stage()
	_update_door(delta)


func _update_door(delta: float) -> void:
	if _door_cells.is_empty():
		return
	var door_x := _door_cells[0].x * T
	match _door_state:
		0:
			if player.global_position.x > door_x - 14 and player.is_on_floor():
				_door_state = 1
				Sfx.play(&"door")
				player.controls_enabled = false
				player.auto_walk = 1.0
				for shape in _door_body.get_children():
					(shape as CollisionShape2D).set_deferred("disabled", true)
		1:
			_door_open = minf(_door_open + delta * 3.0, 1.0)
			if player.global_position.x > door_x + T + 28:
				_door_state = 2
				player.auto_walk = 0.0
				for shape in _door_body.get_children():
					(shape as CollisionShape2D).set_deferred("disabled", false)
				Sfx.play(&"door", 0.8)
				var camera := player.get_node("Camera2D") as Camera2D
				camera.limit_left = door_x + T
				Game.checkpoint = Vector2(door_x - 40, _door_cells[-1].y * T + T)
				_start_boss()
		2:
			_door_open = maxf(_door_open - delta * 3.0, 0.0)
	_tiles.queue_redraw()


func door_open_amount() -> float:
	return _door_open


func _start_boss() -> void:
	if boss == null:
		await get_tree().create_timer(0.6).timeout
		_finish_stage()
		return
	# O Guardião desce do alto da arena.
	var landing := boss.global_position
	boss.global_position = Vector2(landing.x, _arena_rect().position.y - 60.0)
	boss.visible = true
	var tween := create_tween()
	tween.tween_property(boss, "global_position", landing, 1.0).set_ease(Tween.EASE_OUT)
	await tween.finished
	_hud.call("boss_intro", Game.boss_info(boss.boss_id).get("name", "Guardião"))
	await get_tree().create_timer(1.4).timeout
	boss.start()
	player.controls_enabled = true


func _on_boss_defeated() -> void:
	_finished = true
	player.controls_enabled = false
	var info := Game.boss_info(boss.boss_id)
	Game.defeat_boss(boss.boss_id)
	var weapon: StringName = info.get("weapon", &"")
	Sfx.play(&"weapon_get")
	_hud.call("weapon_get", Game.WEAPONS.get(weapon, {}).get("name", "Arma"), Game.weapon_color(weapon))
	await Signal(_hud, "weapon_get_closed")
	_exit_stage()


func _finish_stage() -> void:
	if _finished:
		return
	_finished = true
	player.controls_enabled = false
	if Game.current_boss == &"":
		Game.intro_cleared = true
		Game.save_game()
	Sfx.play(&"weapon_get")
	_hud.call("announce", "FASE CONCLUÍDA", "")
	await get_tree().create_timer(2.5).timeout
	_exit_stage()


func _exit_stage() -> void:
	Game.checkpoint = Vector2.ZERO
	Game.go_to_stage_select()


func _on_player_died() -> void:
	Game.boss_fight_ended.emit()
	await get_tree().create_timer(2.4).timeout
	# Recomeça a fase do último checkpoint (com a vida cheia).
	get_tree().reload_current_scene()
