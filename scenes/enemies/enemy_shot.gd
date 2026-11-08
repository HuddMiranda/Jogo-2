extends Area2D
## Projétil inimigo: fere a caçadora e some ao bater numa parede.

var velocity := Vector2.ZERO
var fall_gravity := 0.0
var color := Color(0.7, 1.0, 0.3)
var damage := 2
var radius := 4.0
var _time := 0.0


func _ready() -> void:
	collision_layer = 0
	collision_mask = 3  # mundo e jogador
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = radius
	shape.shape = circle
	add_child(shape)
	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	_time += delta
	velocity.y += fall_gravity * delta
	position += velocity * delta
	if _time > 4.0:
		queue_free()
	queue_redraw()


func _on_body_entered(body: Node) -> void:
	if body is Player:
		(body as Player).take_damage(damage, global_position.x - velocity.x)
	queue_free()


func _draw() -> void:
	var pulse := 1.0 + 0.25 * sin(_time * 30.0)
	draw_circle(Vector2.ZERO, radius * pulse + 2.0, Color(color, 0.35))
	draw_circle(Vector2.ZERO, radius, color)
	draw_rect(Rect2(-1, -1, 2, 2), Color.WHITE)
