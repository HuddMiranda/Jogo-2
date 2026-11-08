@tool
class_name SheetSprite
extends Node2D
## Desenha uma animação de uma folha de sprites (art/sprites/<sheet>.png,
## dados em SpriteData). A origem do nó é a origem do quadro (pés / centro).
## Vire o desenho com scale.x = -1.

@export var sheet := "hero":
	set(value):
		sheet = value
		_load()
@export var anim := "idle"
## Velocidade da animação (1 = normal).
@export var speed := 1.0
## Cor multiplicada (piscar ao levar dano, brilho da carga...).
var tint := Color.WHITE
## Brilho branco por cima (0 a 1), para o "flash" de dano.
var flash := 0.0

var _time := 0.0
var _texture: Texture2D
var _data: Dictionary = {}


func _ready() -> void:
	_load()


func _load() -> void:
	_data = SpriteData.SHEETS.get(sheet, {})
	var path := "res://art/sprites/%s.png" % sheet
	_texture = load(path) as Texture2D if ResourceLoader.exists(path) else null
	queue_redraw()


## Troca de animação (recomeça do quadro 0 só se for outra).
func play(name: String) -> void:
	if name != anim:
		anim = name
		_time = 0.0


func has_anim(name: String) -> bool:
	return _data.get("anims", {}).has(name)


func current_frame() -> int:
	var info: Dictionary = _data.get("anims", {}).get(anim, {})
	if info.is_empty():
		return 0
	return int(_time * float(info["fps"])) % int(info["frames"])


func _process(delta: float) -> void:
	_time += delta * speed
	queue_redraw()


func _draw() -> void:
	_draw_frame(anim, current_frame())


func _draw_frame(name: String, frame: int) -> void:
	if _texture == null or _data.is_empty():
		return
	var info: Dictionary = _data["anims"].get(name, _data["anims"].values()[0])
	var size := Vector2(_data["frame"][0], _data["frame"][1])
	var origin := Vector2(_data["origin"][0], _data["origin"][1])
	var src := Rect2(Vector2(frame * size.x, info["row"] * size.y), size)
	draw_texture_rect_region(_texture, Rect2(-origin, size), src, tint)
	if flash > 0.0:
		draw_texture_rect_region(_texture, Rect2(-origin, size), src, Color(1, 1, 1, flash * 0.8))
