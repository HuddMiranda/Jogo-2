class_name HDHero
extends Node2D
## Elyra em alta resolução com animação recortada (cutout): peças desenhadas
## à parte (art/hd/vex_parts/, geradas por tools/hd_parts.py) presas num
## esqueleto (quadril → tronco → pescoço/cabeça e ombros → braços → espada;
## quadril → coxas → canelas → pés). A cada quadro, cada articulação vai
## suavemente da pose atual para a pose da animação: o movimento fica fluido
## e as trocas de animação (parar, pousar, virar) não "pulam".
##
## Interface: play(), attack(), anim, charge_level, weapon_color, flash e
## muzzle() (a mão da espada, de onde saem os poderes). A origem fica nos pés.
## As poses espelham tools/hd_rig.py (usado para prévias): mexa nos dois.

const PARTS_DIR := "res://art/hd/vex_parts/"
## 4 unidades do esqueleto = 1 pixel do jogo.
const UNIT := 0.25
const HIP := Vector2(0, -92)
const NECK := Vector2(2, -60)
const SHOULDER_B := Vector2(-12, -50)
const SHOULDER_F := Vector2(12, -50)
const HIP_B := Vector2(-4, 0)
const HIP_F := Vector2(5, 0)
const THIGH := 34.0
const SHIN := 34.0
const UPPER_ARM := 24.0
const HAND := 24.0
## Ponto da lâmina onde brilha a carga.
const BLADE_GLOW := Vector2(0, 44)
const SOLE := [Vector2(-10, 24), Vector2(28, 24)]
## Peças, de trás para a frente: [nome, é do lado de trás].
const ORDER := [["upper_arm", true], ["forearm", true], ["shoulder", true], ["thigh", true], ["shin", true],
		["foot", true], ["torso", false], ["thigh", false], ["shin", false], ["foot", false], ["skirt", false], ["head", false],
		["upper_arm", false], ["sword", false], ["forearm", false], ["shoulder", false]]
const BACK_TINT := Color(0.72, 0.7, 0.78)
## Quão rápido as articulações chegam na pose nova (maior = mais rápido).
const BLEND := 18.0
## Golpes de espada: braço da frente de [início] até [fim] (armf, cf, sw).
## 0 = de cima para baixo, 1 = de baixo para cima, 2 = golpe carregado.
const ATTACK_TIME := 0.26
const SWINGS := [[Vector3(2.7, 0.2, 0.4), Vector3(0.25, 0.1, 1.0)], [Vector3(-0.2, 0.3, 1.2), Vector3(2.4, 0.4, 0.6)],
		[Vector3(2.9, 0.1, 0.3), Vector3(0.15, 0.05, 1.1)]]

var anim := "idle"
var charge_level := 0
var weapon_color := Color(0.55, 1.0, 0.7)
var flash := 0.0
var tint := Color.WHITE
## Parado no tempo (rastro do dash).
var frozen := false

var _time := 0.0
var _cur: Dictionary = {}
var _rig: Node2D
var _sprites: Array[Sprite2D] = []
var _glow: Node2D
var _muzzle := Vector2.ZERO
var _blade := Vector2.ZERO
var _attack_time := -1.0
var _attack_kind := 0


func _ready() -> void:
	_rig = Node2D.new()
	_rig.scale = Vector2(UNIT, UNIT)
	_rig.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	add_child(_rig)
	for entry: Array in ORDER:
		var sprite := Sprite2D.new()
		sprite.texture = load(PARTS_DIR + entry[0] + ".png")
		sprite.centered = false
		sprite.offset = -HDParts.PARTS[entry[0]]["pivot"]
		if entry[1]:
			sprite.self_modulate = BACK_TINT
		_rig.add_child(sprite)
		_sprites.append(sprite)
	_glow = Node2D.new()
	_glow.draw.connect(_draw_glow)
	add_child(_glow)
	if _cur.is_empty():
		_cur = pose(anim, 0.0)
	_apply()


func play(name: String) -> void:
	if name != anim:
		if anim == "spin":
			_cur["spin"] = 0.0
		anim = name


## Começa um golpe de espada (ver SWINGS).
func attack(kind: int) -> void:
	_attack_kind = kind
	_attack_time = 0.0


func is_attacking() -> bool:
	return _attack_time >= 0.0


func has_anim(_name: String) -> bool:
	return true


## Mão da espada (no espaço deste nó, antes de virar).
func muzzle() -> Vector2:
	return _muzzle


## Cópia parada da pose atual (rastro do dash).
func make_ghost() -> HDHero:
	var ghost := HDHero.new()
	ghost.frozen = true
	ghost.anim = anim
	ghost._cur = _cur.duplicate()
	return ghost


func _process(delta: float) -> void:
	if frozen:
		return
	_time += delta
	var target := pose(anim, _time)
	var k := 1.0 - exp(-BLEND * delta)
	for key: String in target:
		if key == "spin":
			_cur[key] = target[key]
		else:
			_cur[key] = lerpf(_cur.get(key, target[key]), target[key], k)
	if _attack_time >= 0.0:
		# O golpe comanda o braço da frente direto (rápido e seco), sem suavizar.
		_attack_time += delta
		var swing: Array = SWINGS[_attack_kind]
		var arm: Vector3 = swing[0]
		if _attack_time >= 0.04:
			var u := minf(1.0, (_attack_time - 0.04) / 0.08)
			arm = (swing[0] as Vector3).lerp(swing[1], 1.0 - pow(1.0 - u, 3.0))
		_cur["armf"] = arm.x
		_cur["cf"] = arm.y
		_cur["sw"] = arm.z
		_cur["lean"] = target["lean"] + (-0.05 if _attack_kind == 1 else 0.12)
		if _attack_time >= ATTACK_TIME:
			_attack_time = -1.0
	_apply()


## Pose alvo da animação no instante t (ângulos em radianos, "para a frente" positivo).
static func pose(name: String, t: float) -> Dictionary:
	var p := {"lean": 0.05, "bob": 0.0, "thf": 0.28, "knf": 0.05, "thb": -0.2, "knb": 0.05, "ftf": 0.0,
			"ftb": 0.0, "armb": 0.08, "elb": 0.2, "armf": 0.35, "cf": 0.9, "sw": 1.7, "spin": 0.0}
	match name:
		"idle":
			var breath := sin(t * 2.2)
			p["bob"] = -1.2 + breath * 1.2
			p["armb"] = 0.08 + breath * 0.03
			p["armf"] = 0.35 + breath * 0.03
		"run":
			var ph := t * 9.5
			var front := _run_leg(ph)
			var back := _run_leg(ph + PI)
			p.merge({"lean": 0.16, "bob": -5.0 * absf(cos(ph)), "thf": front[0], "knf": front[1], "ftf": front[2],
					"thb": back[0], "knb": back[1], "ftb": back[2], "armb": -0.55 * sin(ph), "elb": 0.9,
						"armf": 0.1 + 0.5 * sin(ph), "cf": 0.5, "sw": -1.35}, true)
		"jump":
			p.merge({"lean": 0.08, "thf": 1.15, "knf": 1.7, "thb": 0.25, "knb": 1.35, "ftb": 0.6, "armb": -0.6,
					"elb": 0.6, "armf": -0.4, "cf": 0.6, "sw": -1.2}, true)
		"fall":
			p.merge({"lean": 0.0, "thf": 0.45, "knf": 0.55, "thb": -0.25, "knb": 0.35, "ftb": 0.45,
					"armb": -1.2 + sin(t * 6.0) * 0.1, "elb": 0.4, "armf": 0.6, "cf": 0.4, "sw": 1.9}, true)
		"spin":
			p.merge({"lean": 0.45, "thf": 2.0, "knf": 2.55, "thb": 1.75, "knb": 2.45, "ftf": 0.5, "ftb": 0.6,
					"armb": 0.9, "elb": 1.6, "armf": 0.6, "cf": 1.2, "sw": -1.4, "spin": t * 15.0}, true)
		"dash":
			p.merge({"lean": 0.42, "bob": 8.0, "thf": 1.05, "knf": 1.35, "thb": -0.95, "knb": 0.2, "ftb": 0.6,
					"armb": -0.5, "elb": 0.5, "armf": -0.7, "cf": 0.3, "sw": -1.3}, true)
		"wall":
			p.merge({"lean": -0.12, "thf": 0.85, "knf": 1.5, "thb": 0.15, "knb": 1.0, "ftb": 0.4, "armb": -2.2,
					"elb": -0.4, "armf": 0.5, "cf": 0.8, "sw": 1.6}, true)
		"hurt":
			p.merge({"lean": -0.38, "bob": -2.0, "thf": 0.5, "knf": 0.6, "thb": -0.5, "knb": 0.35, "armb": -2.0,
					"elb": 0.5, "armf": -0.4, "cf": 0.3, "sw": 0.6}, true)
	return p


static func _run_leg(phase: float) -> Array:
	var thigh := 0.18 + 0.9 * sin(phase)
	var knee := 0.15 + 1.35 * maxf(0.0, cos(phase + 0.75))
	var foot := 0.55 if thigh < -0.3 else (-0.15 if thigh > 0.6 else 0.0)
	return [thigh, knee, foot]


func _apply() -> void:
	var p := _cur
	var hip := Transform2D(0.0, HIP + Vector2(p["lean"] * 6.0, -p["bob"]))
	if p["spin"] != 0.0:
		var center := HIP + Vector2(0, 10)
		hip = Transform2D(p["spin"], center) * Transform2D(0.0, -center) * hip
	var torso := hip * Transform2D(p["lean"], Vector2.ZERO)
	var legs := {}
	for side in ["b", "f"]:
		var th: float = p["th" + side]
		var kn: float = p["kn" + side]
		var ft: float = p["ft" + side]
		var thigh := hip * Transform2D(-th, HIP_F if side == "f" else HIP_B)
		var shin := thigh * Transform2D(kn, Vector2(0, THIGH))
		var foot := shin * Transform2D(ft - (-th + kn), Vector2(0, SHIN))
		legs[side] = [thigh, shin, foot]
	var up_b := torso * Transform2D(-p["armb"], SHOULDER_B)
	var fore_b := up_b * Transform2D(-p["elb"], Vector2(0, UPPER_ARM))
	var up_f := torso * Transform2D(-p["armf"], SHOULDER_F)
	var fore_f := up_f * Transform2D(-p["cf"], Vector2(0, UPPER_ARM))
	var sword := fore_f * Transform2D(-p["sw"], Vector2(0, HAND))
	var transforms: Array[Transform2D] = [up_b, fore_b, torso * Transform2D(0.0, SHOULDER_B),
			legs["b"][0], legs["b"][1], legs["b"][2], torso, legs["f"][0], legs["f"][1], legs["f"][2], torso,
			torso * Transform2D(0.0, NECK), up_f, sword, fore_f, torso * Transform2D(0.0, SHOULDER_F)]
	# No chão, a sola mais baixa encosta na origem.
	var shift := 0.0
	if anim in ["idle", "run", "dash", "hurt"]:
		var sole := -INF
		for foot: Transform2D in [legs["b"][2], legs["f"][2]]:
			for point: Vector2 in SOLE:
				sole = maxf(sole, (foot * point).y)
		shift = -sole
	var part_scale := Vector2(HDParts.UNITS_PER_PIXEL, HDParts.UNITS_PER_PIXEL)
	for i in _sprites.size():
		var t: Transform2D = transforms[i]
		_sprites[i].transform = Transform2D(t.get_rotation(), part_scale, 0.0, t.origin + Vector2(0, shift))
	_muzzle = ((fore_f * Vector2(0, HAND)) + Vector2(0, shift)) * UNIT
	_blade = ((sword * BLADE_GLOW) + Vector2(0, shift)) * UNIT
	_rig.modulate = Color(tint.r + flash, tint.g + flash, tint.b + flash, tint.a)
	_glow.queue_redraw()


func _draw_glow() -> void:
	if charge_level <= 0 or frozen:
		return
	var pulse := 0.5 + 0.5 * sin(_time * 30.0)
	var radius := (3.0 if charge_level == 1 else 6.0) + pulse * 2.0
	var color := weapon_color if charge_level == 1 else weapon_color.lerp(Color.WHITE, pulse * 0.6)
	_glow.draw_circle(_blade, radius + 2.0, Color(color, 0.25))
	_glow.draw_circle(_blade, radius * 0.5, Color(1, 1, 1, 0.9))
