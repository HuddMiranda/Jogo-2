extends Node2D
## Desenha o mapa da fase com o tileset do bioma (art/tiles/<bioma>.png):
## topo, bordas e miolo escolhidos pelos vizinhos de cada bloco; plataformas
## vazadas, espinhos em blocos de 2 px e a porta do chefe (membrana que se
## abre de baixo para cima).

const T := 16

var level  # a fase (scenes/level/level.gd)
var _atlas: Texture2D
var _time := 0.0


func _process(delta: float) -> void:
	_time += delta
	if level and _atlas == null:
		var path := "res://art/tiles/%s.png" % level.biome
		_atlas = load(path) if ResourceLoader.exists(path) else null
		queue_redraw()


func _draw() -> void:
	if level == null:
		return
	for y in level.height:
		for x in level.width:
			var c: String = level.grid[y][x]
			var rect := Rect2(x * T, y * T, T, T)
			match c:
				"#":
					_draw_block(x, y, rect)
				"=":
					var left: bool = level.cell(x - 1, y) == "="
					var right: bool = level.cell(x + 1, y) == "="
					var col := 5 if not left and not right else (0 if not left else (4 if not right else 1 + (x * 7 + y) % 3))
					_tile(rect, col, 3)
				"^":
					_draw_spikes(rect)
	_draw_door()


func _draw_block(x: int, y: int, rect: Rect2) -> void:
	var up: bool = level.is_solid(x, y - 1)
	var left: bool = level.is_solid(x - 1, y)
	var right: bool = level.is_solid(x + 1, y)
	var depth := 0
	while depth < 3 and level.is_solid(x, y - depth - 1):
		depth += 1
	var row := 0 if not up else (1 if depth < 3 else 2)
	var col := absi(hash(Vector2i(x, y))) % 4
	if not left and not right:
		col = 6
	elif not left:
		col = 4
	elif not right:
		col = 5
	_tile(rect, col, row)


func _tile(rect: Rect2, col: int, row: int) -> void:
	if _atlas:
		draw_texture_rect_region(_atlas, rect, Rect2(col * T, row * T, T, T))
	else:
		draw_rect(rect, Color(0.3, 0.35, 0.4))


func _draw_spikes(rect: Rect2) -> void:
	# Espinhos de quitina: degraus de 2 px (não tremulam com a câmera).
	var bone := Color(0.85, 0.82, 0.72)
	var dark := Color(0.35, 0.3, 0.32)
	for k in 2:
		var x := rect.position.x + 2.0 + k * 8.0
		var y := rect.end.y
		for w: float in [6.0, 6.0, 4.0, 4.0, 2.0, 2.0]:
			y -= 2.0
			var offset := (6.0 - w) / 2.0
			draw_rect(Rect2(x + offset, y, w, 2.0), dark)
			draw_rect(Rect2(x + offset, y, 2.0, 2.0), bone)


func _draw_door() -> void:
	var cells: Array = level.get("_door_cells")
	if cells.is_empty():
		return
	var open: float = level.call("door_open_amount")
	var top: float = cells[0].y * T
	var bottom: float = (cells[-1].y + 1) * T
	var x: float = cells[0].x * T
	var visible_height := (bottom - top) * (1.0 - open)
	if visible_height <= 0.0:
		return
	var rect := Rect2(x, top, T, visible_height)
	draw_rect(rect, Color(0.25, 0.08, 0.14))
	# Costelas da membrana e um olho brilhante no meio.
	var y := top + 4.0
	while y < top + visible_height - 2.0:
		draw_rect(Rect2(x + 2, y, T - 4, 2), Color(0.55, 0.18, 0.26))
		y += 8.0
	var glow := 0.6 + 0.4 * sin(_time * 4.0)
	draw_rect(Rect2(x + 4, top + visible_height * 0.5 - 4, 8, 8), Color(1.0, 0.4, 0.5, glow))
	draw_rect(Rect2(x, top, 2, visible_height), Color(0.1, 0.03, 0.06))
	draw_rect(Rect2(x + T - 2, top, 2, visible_height), Color(0.1, 0.03, 0.06))
