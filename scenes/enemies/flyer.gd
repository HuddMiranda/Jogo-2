extends Enemy
## Zumbidor: drone-inseto que paira e, quando a sentinela chega perto,
## mergulha em linha reta onde ela está e volta a subir.

enum State { HOVER, DIVE, RISE }

@export var dive_speed := 280.0

var _state := State.HOVER
var _timer := 0.0
var _home := Vector2.ZERO
var _dive := Vector2.ZERO


func _ready() -> void:
	super()
	uses_gravity = false
	_home = global_position


func _ai(delta: float) -> void:
	_timer += delta
	var player := get_player()
	sprite.play("fly")
	match _state:
		State.HOVER:
			var target := _home + Vector2(sin(_timer * 2.0) * 30.0, sin(_timer * 3.0) * 8.0)
			velocity = (target - global_position) * 4.0
			if player and not player.is_dead():
				facing = signf(player.global_position.x - global_position.x)
				if _timer > 1.0 and global_position.distance_to(player.global_position) < 200.0:
					_dive = (player.global_position + Vector2(0, -18) - global_position).normalized()
					_state = State.DIVE
					_timer = 0.0
		State.DIVE:
			velocity = _dive * dive_speed
			if _timer > 0.9 or get_slide_collision_count() > 0:
				_state = State.RISE
				_timer = 0.0
		State.RISE:
			velocity = (_home - global_position).normalized() * 140.0
			if global_position.distance_to(_home) < 8.0:
				_state = State.HOVER
				_timer = 0.0
