class_name Shot
extends Area2D
## Disparo da sentinela. O visual e o comportamento dependem da arma:
##   buster        — nível 0: tiro curto; 1: tiro médio; 2: rajada carregada
##                   (atravessa os inimigos que derruba);
##   plasma_sting  — Ferrão de Plasma: persegue o inimigo mais próximo;
##   outras armas  — por enquanto, um projétil reto na cor da arma.
## Inimigos com escudo rebatem o tiro (que sai voando sem causar dano).

const SPEEDS := [430.0, 420.0, 390.0]
const DAMAGE := [1, 2, 3]
const RADIUS := [3.0, 6.0, 11.0]

var weapon: StringName = &"buster"
var level := 0
var direction := 1.0
var super_charge := false
var velocity := Vector2.ZERO

var _time := 0.0
var _deflected := false
var _hit: Array[Node] = []


func _ready() -> void:
	collision_layer = 0
	collision_mask = 4
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = RADIUS[level] * (1.3 if super_charge else 1.0)
	shape.shape = circle
	add_child(shape)
	body_entered.connect(_on_body_entered)
	velocity = Vector2(direction * SPEEDS[level], 0.0)
	if weapon == &"plasma_sting":
		velocity = Vector2(direction * 300.0, -40.0)
	if weapon == Game.BUSTER and level == 0:
		add_to_group("small_shots")
	var notifier := VisibleOnScreenNotifier2D.new()
	notifier.rect = Rect2(-8, -8, 16, 16)
	notifier.screen_exited.connect(queue_free)
	add_child(notifier)


func damage() -> int:
	var base: int = DAMAGE[level]
	if super_charge:
		base += 1
	if weapon != Game.BUSTER:
		base = 1 + level
	return base


func _physics_process(delta: float) -> void:
	_time += delta
	if weapon == &"plasma_sting" and not _deflected:
		var target := _nearest_target()
		if target:
			var wanted := (target.global_position + Vector2(0, -12) - global_position).angle()
			velocity = velocity.rotated(clampf(angle_difference(velocity.angle(), wanted), -6.0 * delta, 6.0 * delta))
	position += velocity * delta
	if _time > 2.5:
		queue_free()
	queue_redraw()


func _nearest_target() -> Node2D:
	var best: Node2D = null
	var best_distance := 260.0
	for node in get_tree().get_nodes_in_group("enemies"):
		var enemy := node as Node2D
		if enemy and enemy not in _hit:
			var d := enemy.global_position.distance_to(global_position)
			if d < best_distance:
				best_distance = d
				best = enemy
	return best


func _on_body_entered(body: Node) -> void:
	if _deflected or body in _hit or not body.has_method("hit"):
		return
	_hit.append(body)
	var result: String = body.hit(damage(), weapon, self)
	if result == "blocked":
		# Rebatido: sai voando para trás e para cima, sem dano.
		_deflected = true
		velocity = Vector2(-signf(velocity.x) * 240.0, -240.0)
		Sfx.play(&"no_damage")
		return
	Effects.spark(get_parent(), global_position, Game.weapon_color(weapon))
	# A rajada carregada atravessa quem ela derruba.
	if level == 2 and result == "killed":
		return
	queue_free()


func _draw() -> void:
	var color := Game.weapon_color(weapon)
	var r: float = RADIUS[level] * (1.3 if super_charge else 1.0)
	var flicker := 0.5 + 0.5 * sin(_time * 40.0)
	if weapon == &"plasma_sting":
		var forward := velocity.normalized()
		var side := forward.orthogonal()
		draw_colored_polygon(PackedVector2Array([forward * 8.0, side * 3.0, -forward * 6.0, -side * 3.0]), color)
		draw_line(-forward * 4.0, forward * 6.0, Color(1, 1, 1, 0.9), 2.0)
		return
	match level:
		0:
			draw_rect(Rect2(-4, -2, 8, 4), color)
			draw_rect(Rect2(-2, -2, 4, 4), Color.WHITE)
		1:
			draw_circle(Vector2.ZERO, r + 2.0, Color(color, 0.4))
			draw_circle(Vector2.ZERO, r * 0.6, Color.WHITE)
		_:
			# Rajada: meia-lua de energia com rastro.
			var d := signf(velocity.x)
			for k in 3:
				draw_circle(Vector2(-d * (6 + k * 6), 0), r * (0.7 - k * 0.18), Color(color, 0.35 - k * 0.1))
			draw_circle(Vector2.ZERO, r + 2.0 * flicker, Color(color, 0.8))
			draw_circle(Vector2(d * 3, 0), r * 0.55, Color(1, 1, 1, 0.95))
