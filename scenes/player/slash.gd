class_name Slash
extends Area2D
## Golpe de espada da Elyra: uma área na frente dela que fere cada inimigo
## uma vez enquanto está ativa, com o rastro do corte desenhado em arco.
## Fica presa à personagem (filha do Player) e some sozinha.
##   kind 0 = de cima para baixo, 1 = de baixo para cima, 2 = golpe carregado.

## Quando o corte começa a ferir e quando acaba (segundos), e quanto dura o rastro.
const ACTIVE_FROM := 0.03
const ACTIVE_TO := 0.15
const LIFETIME := 0.22
## Centro do arco (ombro) e alcance, em pixels do jogo (virado para a direita).
const CENTER := Vector2(3, -34)

var kind := 0
var damage := 2
var direction := 1.0
var color := Color(0.85, 1.0, 0.9)

var _time := 0.0
var _hit: Array[Node] = []


func reach() -> float:
	return 34.0 if kind == 2 else 27.0


func _ready() -> void:
	collision_layer = 0
	collision_mask = 4
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(reach() + 6.0, reach() * 1.9)
	shape.shape = rect
	shape.position = Vector2(direction * (reach() * 0.5 + 2.0), CENTER.y + (2.0 if kind != 1 else -2.0))
	add_child(shape)


func _physics_process(delta: float) -> void:
	_time += delta
	if _time >= ACTIVE_FROM and _time <= ACTIVE_TO:
		for body in get_overlapping_bodies():
			_strike(body)
	if _time >= LIFETIME:
		queue_free()
	queue_redraw()


func _strike(body: Node) -> void:
	if body in _hit or not body.has_method("hit"):
		return
	_hit.append(body)
	var result: String = body.hit(damage, Game.BUSTER, self)
	var at := (body as Node2D).global_position + Vector2(0, -10) if body is Node2D else global_position
	if result == "blocked":
		Sfx.play(&"no_damage")
		Effects.spark(get_tree().current_scene, at, Color(1, 1, 1))
		return
	Effects.spark(get_tree().current_scene, at, color)


func _draw() -> void:
	# Rastro em meia-lua: varre do começo do golpe até onde a lâmina está.
	var progress := clampf((_time - ACTIVE_FROM) / 0.09, 0.0, 1.0)
	var fade := 1.0 - clampf((_time - ACTIVE_TO) / (LIFETIME - ACTIVE_TO), 0.0, 1.0)
	if progress <= 0.0 or fade <= 0.0:
		return
	var from := -1.75 if kind != 1 else 1.0
	var to := 1.0 if kind != 1 else -1.75
	var current := lerpf(from, to, progress)
	var r := reach()
	var center := Vector2(CENTER.x * direction, CENTER.y)
	var outer := PackedVector2Array()
	var inner := PackedVector2Array()
	var steps := 14
	for i in steps + 1:
		var u := float(i) / steps
		var a := lerpf(from, current, u)
		var thickness := (0.15 + 0.85 * u) * (9.0 if kind == 2 else 6.0)
		var dir := Vector2(cos(a) * direction, sin(a))
		outer.append(center + dir * r)
		inner.append(center + dir * (r - thickness))
	inner.reverse()
	var poly := outer + inner
	draw_colored_polygon(poly, Color(color, 0.35 * fade))
	draw_polyline(outer, Color(1, 1, 1, 0.9 * fade), 1.5 if kind != 2 else 2.5)
