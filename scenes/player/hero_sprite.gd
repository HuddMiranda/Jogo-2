@tool
class_name HeroSprite
extends SheetSprite
## Sprite da caçadora: corpo + braço da frente desenhado por cima, solto ou
## virado canhão (ao atirar), com o brilho da carga na boca do canhão.

## Mostra o canhão apontado (logo depois de atirar).
var cannon := false
## Nível da carga (0, 1, 2) e cor da arma atual.
var charge_level := 0
var weapon_color := Color(0.48, 1.0, 0.88)


func shoulder() -> Vector2:
	var list: Array = _data.get("shoulders", {}).get(anim, [])
	var frame := current_frame()
	if frame < list.size():
		return Vector2(list[frame][0], list[frame][1])
	return Vector2(3, -28)


## Boca do canhão (no espaço deste nó, antes de virar).
func muzzle() -> Vector2:
	var tip: Array = _data.get("muzzle", [13, 2])
	return shoulder() + Vector2(tip[0], tip[1])


func _draw() -> void:
	super()
	if _texture == null or not _data.has("arm_row"):
		return
	var size := Vector2(_data["frame"][0], _data["frame"][1])
	var arm_origin := Vector2(_data["arm_origin"][0], _data["arm_origin"][1])
	var src := Rect2(Vector2((1 if cannon else 0) * size.x, _data["arm_row"] * size.y), size)
	draw_texture_rect_region(_texture, Rect2(shoulder() - arm_origin, size), src, tint)
	if flash > 0.0:
		draw_texture_rect_region(_texture, Rect2(shoulder() - arm_origin, size), src, Color(1, 1, 1, flash * 0.8))
	if charge_level > 0:
		# Energia acumulando na boca do canhão.
		var tip := muzzle() if cannon else shoulder() + Vector2(4, 10)
		var pulse := 0.5 + 0.5 * sin(_time * 30.0)
		var radius := (3.0 if charge_level == 1 else 6.0) + pulse * 2.0
		var color := weapon_color if charge_level == 1 else weapon_color.lerp(Color.WHITE, pulse * 0.6)
		draw_circle(tip, radius + 2.0, Color(color, 0.25))
		draw_circle(tip, radius * 0.5, Color(1, 1, 1, 0.9))
