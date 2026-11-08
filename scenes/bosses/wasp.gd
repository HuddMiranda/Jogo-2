extends Boss
## Vespa de Plasma: paira no alto da arena e alterna três ataques:
##   - investida: brilha, mira na altura da sentinela e atravessa a arena;
##   - ferrões: sobe e dispara um leque de ferrões de plasma;
##   - mergulho: posiciona-se sobre a sentinela e despenca com o ferrão.
## Com metade da vida fica mais rápida e o leque ganha mais ferrões.
## Fraqueza: Martelo Sísmico. Ao ser vencida, ensina o Ferrão de Plasma.

enum State { HOVER, DASH_WINDUP, DASH, STING, DIVE_AIM, DIVE, RECOVER }

var _state := State.HOVER
var _t := 0.0
var _target := Vector2.ZERO
var _attacks := 0


func _speed() -> float:
	return 1.35 if health <= max_health / 2 else 1.0


func _ai(delta: float) -> void:
	_t += delta * _speed()
	var player := get_player()
	if player == null:
		return
	var to_player := player.global_position - global_position
	match _state:
		State.HOVER:
			# Vai para o alto do lado oposto da arena e encara a sentinela.
			sprite.play("idle")
			if absf(to_player.x) > 4.0:
				facing = signf(to_player.x)
			if _t < 0.05:
				var left := global_position.x > arena.get_center().x
				_target = Vector2(arena.position.x + 90.0 if left else arena.end.x - 90.0, arena.position.y + 90.0)
			velocity = (_target - global_position) * 3.0
			if _t > 1.2:
				_attacks += 1
				var options := [State.DASH_WINDUP, State.STING, State.DIVE_AIM]
				_set_state(options[(_attacks + randi() % 2) % options.size()])
		State.DASH_WINDUP:
			sprite.play("dash")
			velocity = Vector2.ZERO
			sprite.tint = Color(1.6, 1.0, 0.6) if fmod(_t, 0.12) < 0.06 else Color.WHITE
			if _t > 0.5:
				sprite.tint = Color.WHITE
				_target = Vector2(arena.end.x - 40.0 if facing > 0 else arena.position.x + 40.0,
						clampf(player.global_position.y - 10.0, arena.position.y + 40.0, arena.end.y - 20.0))
				_set_state(State.DASH)
		State.DASH:
			var d := _target - global_position
			velocity = d.normalized() * 430.0 * _speed()
			if d.length() < 16.0 or _t > 1.4:
				facing = -facing
				_set_state(State.RECOVER)
		State.STING:
			sprite.play("shoot")
			velocity = Vector2(0, -60.0) if global_position.y > arena.position.y + 60.0 else Vector2.ZERO
			if _t > 0.45 and _t - delta * _speed() <= 0.45:
				var count := 5 if health <= max_health / 2 else 3
				var aim := (player.global_position + Vector2(0, -16) - global_position).angle()
				for i in count:
					var angle := aim + (i - (count - 1) / 2.0) * 0.22
					shoot(global_position + Vector2(facing * 12, 8), Vector2.from_angle(angle) * 230.0, Color(1.0, 0.7, 0.2), 2)
			if _t > 0.9:
				_set_state(State.RECOVER)
		State.DIVE_AIM:
			sprite.play("idle")
			_target = Vector2(player.global_position.x, arena.position.y + 50.0)
			velocity = (_target - global_position) * 5.0
			if _t > 0.7:
				_set_state(State.DIVE)
		State.DIVE:
			sprite.play("dash")
			velocity = Vector2(0, 460.0 * _speed())
			if is_on_floor() or global_position.y > arena.end.y - 30.0 or _t > 1.2:
				Effects.explosion(get_parent(), global_position + Vector2(0, 10), Color(1.0, 0.7, 0.2), 16.0)
				for side: float in [-1.0, 1.0]:
					shoot(global_position + Vector2(side * 10, 0), Vector2(side * 200.0, -60.0), Color(1.0, 0.7, 0.2), 2, 300.0)
				_set_state(State.RECOVER)
		State.RECOVER:
			sprite.play("idle")
			velocity = velocity.move_toward(Vector2.ZERO, 900.0 * delta)
			if _t > 0.5:
				_set_state(State.HOVER)


func _set_state(state: State) -> void:
	_state = state
	_t = 0.0


func _on_weakness_hit() -> void:
	sprite.play("hurt")
	_set_state(State.RECOVER)
