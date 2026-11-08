class_name Enemy
extends CharacterBody2D
## Base dos inimigos: vida, dano ao encostar, piscar ao levar dano, morte em
## explosão (com chance de soltar vida ou energia) e "acordar" só quando
## aparecem na tela. Sobrescreva _ai(delta) e, se quiser, _is_blocking().
## A cena precisa de um "Sprite" (SheetSprite) e de uma colisão.

const PICKUP_SCENE := preload("res://scenes/level/pickup.tscn")
const SHOT_SCENE := preload("res://scenes/enemies/enemy_shot.tscn")

@export var max_health := 3
@export var contact_damage := 2
@export var gravity := 1200.0
@export var uses_gravity := true
## Chance (0 a 1) de soltar um item ao morrer.
@export_range(0.0, 1.0) var drop_chance := 0.3

var health := 0
var facing := -1.0
var active := false

@onready var sprite: SheetSprite = $Sprite
var _contact: Area2D


func _ready() -> void:
	add_to_group("enemies")
	collision_layer = 4
	collision_mask = 1
	health = max_health
	# Área de contato com o mesmo formato do corpo (fere a sentinela).
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


func get_player() -> Player:
	return get_tree().get_first_node_in_group("player") as Player


func _physics_process(delta: float) -> void:
	if not active:
		var camera := get_viewport().get_camera_2d()
		if camera and absf(camera.get_screen_center_position().x - global_position.x) < 380.0:
			active = true
		else:
			return
	if uses_gravity and not is_on_floor():
		velocity.y = minf(velocity.y + gravity * delta, 500.0)
	_ai(delta)
	move_and_slide()
	sprite.scale.x = facing
	for body in _contact.get_overlapping_bodies():
		if body is Player:
			(body as Player).take_damage(contact_damage, global_position.x)


func _ai(_delta: float) -> void:
	pass


## Se retornar true, o tiro é rebatido (escudo, casco fechado...).
func _is_blocking() -> bool:
	return false


## Chamado pelos tiros. Retorna "blocked", "hit" ou "killed".
func hit(amount: int, _weapon: StringName, _shot: Node) -> String:
	if health <= 0:
		return "hit"
	if _is_blocking():
		return "blocked"
	health -= amount
	Sfx.play(&"enemy_hit", 1.0, -4.0)
	sprite.flash = 1.0
	create_tween().tween_property(sprite, "flash", 0.0, 0.12)
	if health <= 0:
		_die()
		return "killed"
	return "hit"


func shoot(at: Vector2, projectile_velocity: Vector2, color := Color(0.7, 1.0, 0.3), projectile_gravity := 0.0) -> void:
	var projectile = SHOT_SCENE.instantiate()
	projectile.velocity = projectile_velocity
	projectile.fall_gravity = projectile_gravity
	projectile.color = color
	get_parent().add_child(projectile)
	projectile.global_position = at
	Sfx.play(&"enemy_shot", 1.0, -8.0)


func _die() -> void:
	Effects.explosion(get_parent(), global_position + Vector2(0, -8))
	if randf() < drop_chance:
		var pickup := PICKUP_SCENE.instantiate() as Pickup
		pickup.kind = ["health_small", "health_small", "energy_small", "health_big", "energy_big"].pick_random()
		pickup.temporary = true
		get_parent().add_child.call_deferred(pickup)
		pickup.position = position + Vector2(0, -8)
	queue_free()
