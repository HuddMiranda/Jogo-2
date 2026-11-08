extends Enemy
## Rastejante: besouro alienígena que patrulha o chão, virando nas paredes e
## beiradas; quando a sentinela está à frente, para e cospe ácido em arco.

@export var speed := 45.0
@export var spit_interval := 2.2

var _spit_timer := 1.0
var _pause := 0.0

@onready var _ledge: RayCast2D = $Ledge


func _ai(delta: float) -> void:
	var player := get_player()
	_spit_timer -= delta
	_pause -= delta
	if _pause > 0.0:
		velocity.x = 0.0
		return
	_ledge.position.x = 14.0 * facing
	_ledge.force_raycast_update()
	if is_on_floor() and (is_on_wall() or not _ledge.is_colliding()):
		facing = -facing
	velocity.x = facing * speed
	sprite.play("walk")
	if player and _spit_timer <= 0.0 and not player.is_dead():
		var dx := player.global_position.x - global_position.x
		if absf(dx) < 260.0 and signf(dx) == facing:
			_spit_timer = spit_interval
			_pause = 0.5
			sprite.play("shoot")
			var flight := clampf(absf(dx) / 220.0, 0.5, 1.0)
			shoot(global_position + Vector2(16 * facing, -8), Vector2(dx / flight, -300.0), Color(0.7, 1.0, 0.3), 600.0)
