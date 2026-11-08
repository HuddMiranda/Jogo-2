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
		_load_layers()
		queue_redraw()

var _texture: Texture2D
var _offset := Vector2.ZERO
## Arte HD: camadas pintadas (art/hd/backgrounds/<bioma>/1.png = mais longe).
var _layers: Array[Texture2D] = []
var _camera := Vector2.ZERO


func _load_layers() -> void:
	_layers.clear()
	var base := "res://art/hd/backgrounds/%s/" % biome
	var index := 1
	while ResourceLoader.exists(base + "%d.png" % index):
		_layers.append(load(base + "%d.png" % index))
		index += 1
	if not _layers.is_empty():
		texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS


func _ready() -> void:
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED


func _process(_delta: float) -> void:
	var camera := get_viewport().get_camera_2d()
	if camera:
		_camera = camera.get_screen_center_position()
		var center := _camera * PARALLAX
		_offset = Vector2(fposmod(center.x, 128.0), fposmod(center.y, 128.0)).round()
		queue_redraw()


func _draw() -> void:
	if not _layers.is_empty():
		# Cada camada ocupa a altura da tela e anda mais rápido quanto mais perto.
		for i in _layers.size():
			var layer := _layers[i]
			var factor := 0.08 + 0.5 * float(i) / maxf(1.0, _layers.size() - 1)
			var scale_factor := SCREEN.y / layer.get_height()
			var width := layer.get_width() * scale_factor
			var x := -fposmod(_camera.x * factor, width)
			while x < SCREEN.x:
				draw_texture_rect(layer, Rect2(x, 0, width, SCREEN.y), false)
				x += width
		return
	if _texture:
		draw_texture_rect(_texture, Rect2(-_offset, SCREEN + Vector2(128, 128)), true)
	draw_rect(Rect2(Vector2.ZERO, SCREEN), Color(0.0, 0.0, 0.02, 0.35))
