@tool
class_name SheetSprite
extends Node2D
## Desenha uma animação de uma folha de sprites (art/sprites/<sheet>.png,
## dados em SpriteData). A origem do nó é a origem do quadro (pés / centro).
## Vire o desenho com scale.x = -1.
##
## ARTE HD: se existir art/hd/<sheet>/info.cfg, usa a arte pintada em alta
## resolução no lugar da pixel art: cada animação é uma pasta de PNGs
## numerados (art/hd/<sheet>/<animação>/0001.png, 0002.png...). Detalhes em
## docs/ARTE_HD.md.

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
## Arte HD: animação -> quadros; escala (desenho -> jogo); pés no desenho; qps.
var _hd: Dictionary = {}
var _hd_scale := 1.0
var _hd_pivot := Vector2.ZERO
var _hd_fps: Dictionary = {}
var _hd_info: ConfigFile


func _ready() -> void:
	_load()


func _load() -> void:
	_load_hd()
	_data = SpriteData.SHEETS.get(sheet, {})
	var path := "res://art/sprites/%s.png" % sheet
	_texture = load(path) as Texture2D if ResourceLoader.exists(path) else null
	queue_redraw()


func _load_hd() -> void:
	_hd = {}
	var base := "res://art/hd/%s/" % sheet
	var info := ConfigFile.new()
	if info.load(base + "info.cfg") != OK:
		return
	_hd_info = info
	var drawn_height: float = info.get_value("sprite", "drawn_height", 192.0)
	var game_height: float = info.get_value("sprite", "game_height", 48.0)
	_hd_scale = game_height / drawn_height
	_hd_pivot = info.get_value("sprite", "pivot", Vector2.ZERO)
	for key in info.get_section_keys("fps") if info.has_section("fps") else []:
		_hd_fps[key] = info.get_value("fps", key)
	for entry in ResourceLoader.list_directory(base):
		if not entry.ends_with("/"):
			continue
		var anim_name := entry.trim_suffix("/")
		var files: Array[String] = []
		for file in ResourceLoader.list_directory(base + entry):
			if file.ends_with(".png"):
				files.append(file)
		files.sort()
		var frames: Array[Texture2D] = []
		for file in files:
			frames.append(load(base + entry + file))
		if not frames.is_empty():
			_hd[anim_name] = frames
	if not _hd.is_empty():
		texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS


func is_hd() -> bool:
	return not _hd.is_empty()


## Animação que de fato é desenhada (subclasses podem trocar, ex.: "_shoot").
func shown_anim() -> String:
	return anim


## Troca de animação (recomeça do quadro 0 só se for outra).
func play(name: String) -> void:
	if name != anim:
		anim = name
		_time = 0.0


func has_anim(name: String) -> bool:
	if is_hd():
		return _hd.has(name)
	return _data.get("anims", {}).has(name)


func current_frame() -> int:
	if is_hd():
		var frames: Array = _hd.get(shown_anim(), _hd.values()[0])
		return int(_time * float(_hd_fps.get(shown_anim(), 12))) % frames.size()
	var info: Dictionary = _data.get("anims", {}).get(anim, {})
	if info.is_empty():
		return 0
	return int(_time * float(info["fps"])) % int(info["frames"])


func _process(delta: float) -> void:
	_time += delta * speed
	queue_redraw()


func _draw() -> void:
	if is_hd():
		_draw_hd()
		return
	_draw_frame(anim, current_frame())


func _draw_hd() -> void:
	var frames: Array = _hd.get(shown_anim(), _hd.get("idle", _hd.values()[0]))
	var texture: Texture2D = frames[current_frame() % frames.size()]
	var rect := Rect2(-_hd_pivot * _hd_scale, texture.get_size() * _hd_scale)
	draw_texture_rect(texture, rect, false, tint)
	if flash > 0.0:
		draw_texture_rect(texture, rect, false, Color(1.6, 1.6, 1.6, flash * 0.7))


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
