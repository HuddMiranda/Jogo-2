class_name Pickup
extends Area2D
## Item: vida (pequena/grande), energia de arma (pequena/grande), Semente
## da Vida (vida máxima +2) ou relicário com uma relíquia élfica.
## Itens soltos por inimigos (temporary) caem até o chão e somem depois de
## um tempo; corações e casulos ficam no lugar e só existem uma vez.

@export_enum("health_small", "health_big", "energy_small", "energy_big", "heart", "capsule") var kind := "health_small"
## Relíquia do relicário (Game.ARMOR).
@export var armor_part: StringName = &""
## Identificador para lembrar que já foi pego (corações e casulos).
@export var item_id := ""
var temporary := false

var _velocity := 0.0
var _time := 0.0
var _ray: RayCast2D
var _sprite: SheetSprite


func _ready() -> void:
	if item_id != "" and Game.is_collected(item_id):
		queue_free()
		return
	collision_layer = 0
	collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(14, 14) if kind != "capsule" else Vector2(18, 26)
	shape.shape = rect
	shape.position = Vector2(0, -rect.size.y / 2.0)
	add_child(shape)
	_sprite = SheetSprite.new()
	_sprite.sheet = "items"
	_sprite.anim = kind
	add_child(_sprite)
	if temporary:
		_ray = RayCast2D.new()
		_ray.target_position = Vector2(0, 4)
		add_child(_ray)
	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	_time += delta
	if temporary:
		if not _ray.is_colliding():
			_velocity = minf(_velocity + 900.0 * delta, 400.0)
			position.y += _velocity * delta
		if _time > 6.0:
			queue_free()
		elif _time > 4.0:
			_sprite.visible = fmod(_time, 0.15) > 0.07


func _on_body_entered(body: Node) -> void:
	var player := body as Player
	if player == null or player.is_dead():
		return
	match kind:
		"health_small":
			player.heal(2)
		"health_big":
			player.heal(8)
		"energy_small":
			Game.add_energy(2)
			Sfx.play(&"heal")
		"energy_big":
			Game.add_energy(8)
			Sfx.play(&"heal")
		"heart":
			Game.collect(item_id)
			Game.add_heart(item_id)
			Sfx.play(&"pickup")
			_announce("SEMENTE DA VIDA", "Vida máxima aumentada")
		"capsule":
			Game.collect(item_id)
			Game.add_armor(armor_part)
			Sfx.play(&"weapon_get")
			var info: Dictionary = Game.ARMOR.get(armor_part, {})
			_announce(info.get("name", "Relíquia").to_upper(), info.get("hint", ""))
			Game.save_game()
	queue_free()


func _announce(title: String, text: String) -> void:
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.call("announce", title, text)
