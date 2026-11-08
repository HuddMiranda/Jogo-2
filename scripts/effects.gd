class_name Effects
extends Node2D
## Efeitos visuais simples, desenhados por código: orbes de energia,
## explosões e faíscas. Use os atalhos estáticos (Effects.explosion(...)).

enum Kind { ORB, BURST, SPARK }

var kind := Kind.ORB
var color := Color.WHITE
var velocity := Vector2.ZERO
var radius := 4.0
var life := 0.6
var _age := 0.0


static func orb(parent: Node, at: Vector2, tint: Color) -> Effects:
	return _spawn(parent, at, Kind.ORB, tint, 4.0, 1.2)


static func explosion(parent: Node, at: Vector2, tint := Color(1.0, 0.7, 0.3), size := 14.0) -> Effects:
	Sfx.play(&"explode", 1.0 + randf_range(-0.1, 0.1), -4.0)
	return _spawn(parent, at, Kind.BURST, tint, size, 0.35)


static func spark(parent: Node, at: Vector2, tint := Color.WHITE) -> Effects:
	return _spawn(parent, at, Kind.SPARK, tint, 6.0, 0.15)


static func _spawn(parent: Node, at: Vector2, kind_value: Kind, tint: Color, size: float, duration: float) -> Effects:
	var effect := Effects.new()
	effect.kind = kind_value
	effect.color = tint
	effect.radius = size
	effect.life = duration
	effect.z_index = 20
	parent.add_child(effect)
	effect.global_position = at
	return effect


func _process(delta: float) -> void:
	_age += delta
	position += velocity * delta
	if _age >= life:
		queue_free()
	queue_redraw()


func _draw() -> void:
	var t := _age / life
	match kind:
		Kind.ORB:
			var pulse := 1.0 + 0.3 * sin(_age * 30.0)
			draw_circle(Vector2.ZERO, radius * pulse + 2.0, Color(color, 0.35 * (1.0 - t)))
			draw_circle(Vector2.ZERO, radius * 0.6, Color(1, 1, 1, 1.0 - t))
		Kind.BURST:
			# Anel que cresce e um miolo branco que some (blocos de 2 px).
			var r := radius * (0.4 + t)
			draw_circle(Vector2.ZERO, r, Color(color, 1.0 - t))
			draw_circle(Vector2.ZERO, r * 0.6 * (1.0 - t), Color(1, 1, 0.9, 1.0 - t))
			for k in 6:
				var dir := Vector2.from_angle(k * TAU / 6.0 + 0.3)
				draw_rect(Rect2(dir * r * 1.3 - Vector2(2, 2), Vector2(4, 4)), Color(color.lightened(0.3), 1.0 - t))
		Kind.SPARK:
			var r := radius * (1.0 - t)
			draw_line(Vector2(-r, 0), Vector2(r, 0), Color(color, 1.0 - t), 2.0)
			draw_line(Vector2(0, -r), Vector2(0, r), Color(color, 1.0 - t), 2.0)
