extends Enemy
## Bulbo: casulo preso ao chão. Fechado, rebate os tiros; abre de tempos em
## tempos, cospe três esporos em leque na direção da caçadora e fecha de novo.

@export var cycle := 2.6
var _timer := 0.0


func _ready() -> void:
	super()
	uses_gravity = false


func _ai(delta: float) -> void:
	velocity = Vector2.ZERO
	_timer += delta
	var phase := fmod(_timer, cycle)
	if phase < cycle - 1.2:
		sprite.play("closed")
	elif phase < cycle - 1.0:
		sprite.play("opening")
	else:
		if sprite.anim != "open":
			sprite.play("open")
			var player := get_player()
			if player and not player.is_dead():
				var aim := (player.global_position + Vector2(0, -16) - (global_position + Vector2(0, -12))).normalized()
				for spread: float in [-0.3, 0.0, 0.3]:
					shoot(global_position + Vector2(0, -14), aim.rotated(spread) * 170.0, Color(1.0, 0.85, 0.3))


func _is_blocking() -> bool:
	return sprite.anim == "closed"
