class_name Player
extends CharacterBody2D
## VEX-9, a caçadora de armadura simbionte. A origem do nó fica nos pés.
##
## Movimento (frenético, no estilo dos run-and-gun de 16/32 bits):
##   - corrida, pulo de altura variável (soltar o botão corta a subida);
##   - dash no chão (segurar mantém por um tempo); pular durante o dash vira
##     "dash-pulo": a velocidade alta continua no ar;
##   - deslizar na parede segurando contra ela; pular dela (com dash
##     segurado, o pulo sai rápido);
##   - com as Pernas Saltadoras: um dash no ar por pulo.
## Tiro: aperte para um disparo curto (até 3 na tela); segure para carregar
## (2 níveis; com os Braços Condutores a carga máxima fica mais forte e as
## armas das Bestas também carregam). Q / E trocam de arma.

signal died

const SHOT_SCENE := preload("res://scenes/player/shot.tscn")

@export var run_speed := 150.0
@export var dash_speed := 330.0
@export var dash_time := 0.36
@export var jump_speed := 455.0
@export var gravity := 1300.0
@export var max_fall := 480.0
@export var wall_slide_speed := 85.0
@export var wall_jump_push := 170.0
@export var wall_jump_lock := 0.14
@export var coyote_time := 0.08
@export var jump_buffer := 0.1
@export var charge_mid := 0.35
@export var charge_full := 1.1
@export var hurt_time := 0.4
@export var invincible_time := 1.3

var controls_enabled := true
## Andar sozinho para a direita (portas de chefe, cenas).
var auto_walk := 0.0

var _facing := 1.0
var _dash_timer := 0.0
var _air_dash_used := false
var _dash_jump := false
var _wall_dir := 0
var _wall_lock := 0.0
var _coyote := 0.0
var _buffer := 0.0
var _charge := 0.0
var _charge_sound := 0
var _shoot_pose := 0.0
var _hurt_timer := 0.0
var _invincible := 0.0
var _ghost_timer := 0.0
var _was_on_floor := true
## Pulo em cambalhota (pulou correndo); acaba ao atirar, na parede ou no chão.
var _spinning := false
var _dead := false

## Sprite da caçadora: HDHero (arte HD recortada) ou HeroSprite (pixel art).
@onready var sprite = $Sprite


func _ready() -> void:
	add_to_group("player")
	Game.set_health(Game.health)


func is_dead() -> bool:
	return _dead


func is_invincible() -> bool:
	return _invincible > 0.0 or _dead


func facing() -> float:
	return _facing


func _physics_process(delta: float) -> void:
	if _dead:
		return
	var direction := 0.0
	var jump_pressed := false
	var jump_held := false
	var dash_pressed := false
	var dash_held := false
	var shoot_pressed := false
	var shoot_held := false
	var shoot_released := false
	if controls_enabled and _hurt_timer <= 0.0:
		direction = Input.get_axis("move_left", "move_right")
		jump_pressed = Input.is_action_just_pressed("jump")
		jump_held = Input.is_action_pressed("jump")
		dash_pressed = Input.is_action_just_pressed("dash")
		dash_held = Input.is_action_pressed("dash")
		shoot_pressed = Input.is_action_just_pressed("shoot")
		shoot_held = Input.is_action_pressed("shoot")
		shoot_released = Input.is_action_just_released("shoot")
		if Input.is_action_just_pressed("weapon_next"):
			_switch_weapon(1)
		elif Input.is_action_just_pressed("weapon_prev"):
			_switch_weapon(-1)
	elif auto_walk != 0.0:
		direction = auto_walk

	_hurt_timer -= delta
	_invincible -= delta
	_wall_lock -= delta
	_shoot_pose -= delta
	var on_floor := is_on_floor()

	# Pouso e "coyote time".
	if on_floor:
		_coyote = coyote_time
		_air_dash_used = false
		if not _was_on_floor:
			_dash_jump = false
			_spinning = false
			Sfx.play(&"land", 1.0, -6.0)
	else:
		_coyote -= delta
	_was_on_floor = on_floor
	_buffer = jump_buffer if jump_pressed else _buffer - delta

	if _hurt_timer > 0.0:
		velocity.y = minf(velocity.y + gravity * delta, max_fall)
		velocity.x = move_toward(velocity.x, 0.0, 300.0 * delta)
		move_and_slide()
		_update_sprite(on_floor)
		return

	if direction != 0.0 and _wall_lock <= 0.0:
		_facing = signf(direction)

	# Dash (no chão; no ar só com as Pernas Saltadoras).
	if dash_pressed and _dash_timer <= 0.0:
		if on_floor:
			_start_dash()
		elif Game.has_armor(&"legs") and not _air_dash_used:
			_air_dash_used = true
			_start_dash()
	if _dash_timer > 0.0:
		_dash_timer -= delta
		var cancel := (on_floor and not dash_held) or (direction != 0.0 and signf(direction) != _facing)
		if cancel:
			_dash_timer = 0.0

	# Parede: deslizar (caindo e segurando contra ela).
	_wall_dir = 0
	if not on_floor:
		for side: int in [1, -1]:
			if test_move(global_transform, Vector2(side * 2.0, 0.0)):
				_wall_dir = side
	var sliding := _wall_dir != 0 and direction != 0.0 and signf(direction) == _wall_dir and velocity.y >= 0.0

	# Pulos.
	if _buffer > 0.0:
		if _coyote > 0.0:
			velocity.y = -jump_speed
			_dash_jump = _dash_timer > 0.0 or dash_held
			_spinning = absf(velocity.x) > 40.0 or direction != 0.0
			_dash_timer = 0.0
			_coyote = 0.0
			_buffer = 0.0
			Sfx.play(&"jump", 1.0, -4.0)
		elif _wall_dir != 0 and not on_floor:
			velocity.y = -jump_speed * 0.95
			_dash_jump = dash_held
			velocity.x = -_wall_dir * (dash_speed if dash_held else wall_jump_push)
			_wall_lock = wall_jump_lock
			_facing = -_wall_dir
			_spinning = true
			_buffer = 0.0
			Sfx.play(&"jump", 1.1, -4.0)
	if not jump_held and velocity.y < 0.0 and not on_floor:
		velocity.y = maxf(velocity.y, -60.0)  # soltou o pulo: corta a subida

	# Velocidade horizontal.
	if _dash_timer > 0.0:
		velocity.x = _facing * dash_speed
		if not on_floor:
			velocity.y = 0.0  # dash no ar é reto
		_ghost_timer -= delta
		if _ghost_timer <= 0.0:
			_ghost_timer = 0.05
			_spawn_ghost()
	elif _wall_lock <= 0.0:
		var speed := dash_speed if (_dash_jump and not on_floor) else run_speed
		velocity.x = direction * speed
		if _dash_jump and not on_floor and direction != 0.0:
			_ghost_timer -= delta
			if _ghost_timer <= 0.0:
				_ghost_timer = 0.07
				_spawn_ghost()

	# Gravidade e parede.
	if not on_floor and not (_dash_timer > 0.0):
		velocity.y = minf(velocity.y + gravity * delta, max_fall)
		if sliding:
			velocity.y = minf(velocity.y, wall_slide_speed)
			_facing = -_wall_dir  # de costas para a parede: atira para fora

	# Tiro e carga.
	if shoot_pressed:
		_spinning = false
		_fire(0)
	if shoot_held:
		_charge += delta
		var level := _charge_level()
		if level > _charge_sound:
			_charge_sound = level
			Sfx.play(&"charge" if level == 1 else &"charged", 1.0, -6.0)
	if shoot_released:
		var level := _charge_level()
		if level > 0:
			_fire(level)
		_charge = 0.0
		_charge_sound = 0

	move_and_slide()
	_update_sprite(is_on_floor(), sliding)


func _start_dash() -> void:
	_dash_timer = dash_time
	_ghost_timer = 0.0
	Sfx.play(&"dash", 1.0, -6.0)


func _charge_level() -> int:
	if Game.current_weapon != Game.BUSTER and not Game.has_armor(&"arms"):
		return 0
	if _charge >= charge_full:
		return 2
	return 1 if _charge >= charge_mid else 0


func _switch_weapon(step: int) -> void:
	if Game.weapons.size() <= 1:
		return
	Game.cycle_weapon(step)
	_charge = 0.0
	_charge_sound = 0
	Sfx.play(&"menu_move")


func _fire(level: int) -> void:
	var weapon := Game.current_weapon
	if weapon == Game.BUSTER and level == 0:
		if get_tree().get_nodes_in_group("small_shots").size() >= 3:
			return
	else:
		var cost: int = Game.WEAPONS[weapon]["cost"] * (2 if level > 0 else 1)
		if not Game.spend_energy(cost):
			Sfx.play(&"no_damage")
			return
	var shot := SHOT_SCENE.instantiate() as Shot
	shot.weapon = weapon
	shot.level = level
	shot.direction = _facing
	shot.super_charge = level == 2 and Game.has_armor(&"arms")
	get_parent().add_child(shot)
	var muzzle := sprite.muzzle()
	shot.global_position = global_position + Vector2(muzzle.x * _facing, muzzle.y)
	_shoot_pose = 0.3
	sprite.cannon = true
	Sfx.play([&"shot", &"shot_mid", &"shot_full"][level], 1.0 if weapon == Game.BUSTER else 0.8)


func _spawn_ghost() -> void:
	var ghost: Node2D
	if sprite.has_method("make_ghost"):
		ghost = sprite.make_ghost()
		ghost.modulate = Color(Game.weapon_color(), 0.5)
	else:
		var sheet := SheetSprite.new()
		sheet.sheet = "hero"
		sheet.anim = sprite.anim
		sheet.speed = 0.0
		sheet.tint = Color(Game.weapon_color(), 0.5)
		ghost = sheet
	ghost.scale = sprite.scale
	get_parent().add_child(ghost)
	ghost.global_position = global_position
	ghost.z_index = -1
	var tween := ghost.create_tween()
	tween.tween_property(ghost, "modulate:a", 0.0, 0.22)
	tween.tween_callback(ghost.queue_free)


func _update_sprite(on_floor: bool, sliding := false) -> void:
	sprite.scale.x = _facing
	if _hurt_timer > 0.0:
		sprite.play("hurt")
	elif sliding:
		_spinning = false
		sprite.play("wall")
	elif _spinning and not on_floor:
		sprite.play("spin")
	elif _dash_timer > 0.0 and on_floor:
		sprite.play("dash")
	elif not on_floor:
		sprite.play("jump" if velocity.y < 0.0 else "fall")
	elif absf(velocity.x) > 10.0:
		sprite.play("run")
	else:
		sprite.play("idle")
	# Correndo, o canhão vai apontado para a frente (e logo depois de atirar).
	sprite.cannon = _shoot_pose > 0.0 or sprite.anim == "run" or sprite.anim == "dash"
	sprite.charge_level = _charge_level() if Input.is_action_pressed("shoot") and controls_enabled else 0
	sprite.weapon_color = Game.weapon_color()
	sprite.visible = _invincible <= 0.0 or fmod(_invincible, 0.1) > 0.05


# --- Dano e morte ---------------------------------------------------------------

func take_damage(amount: int, from_x: float) -> void:
	if is_invincible():
		return
	if Game.has_armor(&"body"):
		amount = ceili(amount / 2.0)
	Game.set_health(Game.health - amount)
	Sfx.play(&"hurt")
	if Game.health <= 0:
		die()
		return
	_hurt_timer = hurt_time
	_invincible = invincible_time
	_dash_timer = 0.0
	_charge = 0.0
	var away := signf(global_position.x - from_x)
	if away == 0.0:
		away = -_facing
	velocity = Vector2(away * 110.0, -160.0)
	sprite.flash = 1.0
	create_tween().tween_property(sprite, "flash", 0.0, 0.25)


## Espinhos e abismos: morte na hora.
func die() -> void:
	if _dead:
		return
	_dead = true
	Game.set_health(0)
	velocity = Vector2.ZERO
	sprite.visible = false
	Sfx.play(&"death")
	for i in 12:
		var orb := Effects.orb(get_parent(), global_position + Vector2(0, -20), Game.weapon_color())
		orb.set("velocity", Vector2.from_angle(TAU * i / 12.0) * (90.0 if i % 2 else 150.0))
	died.emit()


func heal(amount: int) -> void:
	Game.set_health(Game.health + amount)
	Sfx.play(&"heal")
