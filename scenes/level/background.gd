extends Node2D
## Fundo da fase (fica numa CanvasLayer atrás de tudo, em coordenadas de
## tela): a textura de parede do bioma (art/tiles/<bioma>_wall.png) repetida,
## andando mais devagar que a câmera (paralaxe), com uma névoa escura por cima.

const PARALLAX := 0.45
const SCREEN := Vector2(640, 360)

var biome := "ruins":
	set(value):
		biome = value
		var path := "res://art/tiles/%s_wall.png" % biome
		_texture = load(path) if ResourceLoader.exists(path) else null
		queue_redraw()

var _texture: Texture2D
var _offset := Vector2.ZERO


func _ready() -> void:
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED


func _process(_delta: float) -> void:
	var camera := get_viewport().get_camera_2d()
	if camera:
		var center := camera.get_screen_center_position() * PARALLAX
		_offset = Vector2(fposmod(center.x, 128.0), fposmod(center.y, 128.0)).round()
		queue_redraw()


func _draw() -> void:
	if _texture:
		draw_texture_rect(_texture, Rect2(-_offset, SCREEN + Vector2(128, 128)), true)
	draw_rect(Rect2(Vector2.ZERO, SCREEN), Color(0.0, 0.0, 0.02, 0.35))
