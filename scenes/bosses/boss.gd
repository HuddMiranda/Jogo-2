class_name Boss
extends CharacterBody2D
## Base dos chefes (Guardiões corrompidos): barra de vida, invencibilidade curta
## depois de cada golpe, fraqueza (a arma certa fere 4 vezes mais e faz a
## Guardião cambalear), dano ao encostar e a explosão final. A fase chama
## start() quando a luta começa e escuta `defeated`.

signal defeated

@export var boss_id: StringName = &"wasp"
@export var max_health := 32
@export var contact_damage := 3
## Tempo invencível depois de levar um golpe.
@export var hit_invincibility := 0.45

var health := 0
var facing := -1.0
var fighting := false
## Área da arena (em coordenadas globais), dada pela fase.
var arena := Rect2()

var _invincible := 0.0
var _stagger := 0.0
var _dying := false
var _contact: Area2D

@onready var sprite: SheetSprite = $Sprite


func _ready() -> void:
	add_to_group("enemies")
	collision_layer = 4
	collision_mask = 1
	health = max_health
	_contact = Area2D.new()
	_contact.collision_layer = 0
	_contact.collision_mask = 2
	for child in get_children():
		if child is CollisionShape2D:
			var copy := CollisionShape2D.new()
			copy.shape = child.shape
			copy.position = child.position
			_contact.add_child(copy)
	add_child(_contact)


func start() -> void:
	fighting = true
	Game.boss_fight_started.emit(Game.boss_info(boss_id).get("name", "Guardião"))
	Game.boss_health_changed.emit(health, max_health)
	Sfx.play(&"boss_roar")


func get_player() -> Player:
	return get_tree().get_first_node_in_group("player") as Player


func _physics_process(delta: float) -> void:
	_invincible -= delta
	if _dying:
		return
	if fighting:
		if _stagger > 0.0:
			_stagger -= delta
			velocity = velocity.move_toward(Vector2.ZERO, 600.0 * delta)
		else:
			_ai(delta)
		move_and_slide()
		for body in _contact.get_overlapping_bodies():
			if body is Player:
				(body as Player).take_damage(contact_damage, global_position.x)
	sprite.scale.x = facing
	sprite.visible = _invincible <= 0.0 or fmod(_invincible, 0.08) > 0.04


func _ai(_delta: float) -> void:
	pass


func hit(amount: int, weapon: StringName, _shot: Node) -> String:
	if not fighting or _dying or _invincible > 0.0:
		return "hit"
	var multiplier := Game.damage_against(boss_id, weapon)
	var damage := int(round(amount * multiplier))
	health = maxi(health - damage, 0)
	_invincible = hit_invincibility
	Game.boss_health_changed.emit(health, max_health)
	sprite.flash = 1.0
	create_tween().tween_property(sprite, "flash", 0.0, 0.15)
	Sfx.play(&"enemy_hit", 0.8)
	if multiplier > 1.0:
		_stagger = 0.6  # fraqueza: cambaleia
		_on_weakness_hit()
	if health <= 0:
		_die()
		return "killed"
	return "hit"


func _on_weakness_hit() -> void:
	pass


func shoot(at: Vector2, projectile_velocity: Vector2, color: Color, damage := 2, projectile_gravity := 0.0) -> void:
	var projectile = Enemy.SHOT_SCENE.instantiate()
	projectile.velocity = projectile_velocity
	projectile.fall_gravity = projectile_gravity
	projectile.color = color
	projectile.damage = damage
	projectile.radius = 5.0
	get_parent().add_child(projectile)
	projectile.global_position = at
	Sfx.play(&"enemy_shot", 0.8, -6.0)


func _die() -> void:
	_dying = true
	fighting = false
	Game.boss_fight_ended.emit()
	Sfx.play(&"boss_explode")
	for i in 10:
		var offset := Vector2(randf_range(-30, 30), randf_range(-60, 0))
		get_tree().create_timer(i * 0.15).timeout.connect(func() -> void:
			if is_inside_tree():
				Effects.explosion(get_parent(), global_position + offset, Game.boss_info(boss_id).get("color", Color.WHITE), 22.0))
	await get_tree().create_timer(1.8).timeout
	for i in 16:
		var orb := Effects.orb(get_parent(), global_position + Vector2(0, -30), Game.boss_info(boss_id).get("color", Color.WHITE))
		orb.velocity = Vector2.from_angle(TAU * i / 16.0) * 160.0
	visible = false
	await get_tree().create_timer(1.0).timeout
	defeated.emit()
