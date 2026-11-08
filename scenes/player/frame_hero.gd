class_name FrameHero
extends Node2D
## Elyra animada quadro a quadro (estilo Afterimage): cada animação é uma
## pasta de PNGs desenhados inteiros (art/hd/elyra/<animação>/0001.png...),
## gerados por tools/hd_frames.py, com os dados em HeroFrames
## (scripts/hero_frames.gd). A origem do nó fica nos pés.
##
## Interface usada pelo Player: play(), attack(), is_attacking(), anim,
## charge_level, weapon_color, flash, tint, muzzle() e make_ghost().

const FRAMES_DIR := "res://art/hd/elyra/"
const SLASHES := ["slash_down", "slash_up", "slash_charged"]
const AIR_ANIMS := ["jump", "fall", "spin", "wall"]

## Quadros carregados (compartilhados entre a personagem e os rastros do dash).
static var _cache: Dictionary = {}

var anim := "idle"
var charge_level := 0
var weapon_color := Color(0.75, 1.0, 0.85)
var flash := 0.0
var tint := Color.WHITE
## Parado no tempo (rastro do dash).
var frozen := false

var _time := 0.0
var _frame := 0
## Golpe em andamento (nome da animação de golpe) e seu relógio.
var _attack := ""
var _attack_time := 0.0
var _sprite: Sprite2D
var _glow: Node2D


func _ready() -> void:
	_load_frames()
	_sprite = Sprite2D.new()
	_sprite.centered = false
	_sprite.offset = -HeroFrames.PIVOT
	_sprite.scale = Vector2(HeroFrames.SCALE, HeroFrames.SCALE)
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	add_child(_sprite)
	_glow = Node2D.new()
	_glow.draw.connect(_draw_glow)
	add_child(_glow)
	_show()


static func _load_frames() -> void:
	if not _cache.is_empty():
		return
	for name: String in HeroFrames.ANIMS:
		var frames: Array[Texture2D] = []
		for i in HeroFrames.ANIMS[name]["frames"]:
			var path := FRAMES_DIR + "%s/%04d.png" % [name, i + 1]
			frames.append(load(path) if ResourceLoader.exists(path) else null)
		_cache[name] = frames


func play(name: String) -> void:
	if name != anim:
		anim = name
		_time = 0.0


func has_anim(name: String) -> bool:
	return HeroFrames.ANIMS.has(name)


## Começa um golpe: 0 = de cima para baixo, 1 = de baixo para cima, 2 = carregado.
func attack(kind: int) -> void:
	_attack = SLASHES[clampi(kind, 0, 2)]
	if anim in AIR_ANIMS:
		_attack = "air_" + _attack
	_attack_time = 0.0


func is_attacking() -> bool:
	return _attack != ""


## Animação que está aparecendo agora (o golpe tem prioridade).
func shown_anim() -> String:
	return _attack if _attack != "" else anim


## Mão da espada no quadro atual (espaço deste nó, antes de virar).
func muzzle() -> Vector2:
	var hands: Array = HeroFrames.ANIMS[shown_anim()]["hand"]
	return hands[mini(_frame, hands.size() - 1)]


## Cópia parada do quadro atual (rastro do dash).
func make_ghost() -> FrameHero:
	var ghost := FrameHero.new()
	ghost.frozen = true
	ghost.anim = anim
	ghost._attack = _attack
	ghost._attack_time = _attack_time
	ghost._time = _time
	return ghost


func _process(delta: float) -> void:
	if frozen:
		return
	_time += delta
	if _attack != "":
		_attack_time += delta
		var data: Dictionary = HeroFrames.ANIMS[_attack]
		if _attack_time * data["fps"] >= data["frames"] + 1:
			_attack = ""
	_show()


func _show() -> void:
	if _sprite == null:
		return
	var name := shown_anim()
	if not HeroFrames.ANIMS.has(name):
		name = "idle"
	var data: Dictionary = HeroFrames.ANIMS[name]
	var count: int = data["frames"]
	var clock := _attack_time if name == _attack else _time
	var index := int(clock * data["fps"])
	_frame = index % count if data["loop"] else mini(index, count - 1)
	_sprite.texture = _cache[name][_frame]
	_sprite.modulate = Color(tint.r + flash, tint.g + flash, tint.b + flash, tint.a)
	_glow.queue_redraw()


func _draw_glow() -> void:
	if charge_level <= 0 or frozen:
		return
	var blades: Array = HeroFrames.ANIMS[shown_anim()]["blade"] if HeroFrames.ANIMS.has(shown_anim()) else [Vector2.ZERO]
	var at: Vector2 = blades[mini(_frame, blades.size() - 1)]
	var pulse := 0.5 + 0.5 * sin(_time * 30.0)
	var radius := (3.0 if charge_level == 1 else 6.0) + pulse * 2.0
	var color := weapon_color if charge_level == 1 else weapon_color.lerp(Color.WHITE, pulse * 0.6)
	_glow.draw_circle(at, radius + 2.0, Color(color, 0.25))
	_glow.draw_circle(at, radius * 0.5, Color(1, 1, 1, 0.9))
