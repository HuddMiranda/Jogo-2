extends Node
## Estado global do jogo (autoload "Game"): as oito Bestas-Simbionte (chefes),
## suas fases e armas, as fraquezas, as peças de armadura, os Corações
## Simbiontes, o que já foi coletado e o salvamento.
##
## Premissa: no planeta Ossária, as Bestas-Simbionte (criaturas bio-mecânicas
## que guardavam o ecossistema) enlouqueceram. VEX-9, caçadora de armadura
## simbionte, enfrenta as oito; de cada uma vencida, sua armadura absorve a
## arma. Cada Besta é fraca contra a arma de outra.

signal health_changed(current: int, maximum: int)
signal weapon_changed(weapon: StringName)
signal energy_changed(weapon: StringName, current: int, maximum: int)
signal boss_health_changed(current: int, maximum: int)
signal boss_fight_started(boss_name: String)
signal boss_fight_ended

const SAVE_PATH := "user://save.json"
const SAVE_VERSION := 1
const BASE_HEALTH := 16
const HEALTH_PER_HEART := 2
const MAX_ENERGY := 28
const BUSTER := &"buster"

const STAGE_SELECT_SCENE := "res://scenes/ui/stage_select.tscn"
const LEVEL_SCENE := "res://scenes/level/level.tscn"
const TITLE_SCENE := "res://scenes/ui/title.tscn"

## As oito Bestas, na ordem da tela de seleção. `weak` é a arma que mais as
## fere; `level` é o mapa da fase (vazio = ainda em construção).
const BOSSES := [
	{"id": &"wasp", "name": "Vespa de Plasma", "stage": "Colmeia de Plasma", "weapon": &"plasma_sting",
		"weak": &"seismic_hammer", "color": Color(1.0, 0.7, 0.15), "level": "res://levels/hive.gd"},
	{"id": &"beetle", "name": "Escaravelho Tectônico", "stage": "Falha Tectônica", "weapon": &"seismic_hammer",
		"weak": &"abyss_jet", "color": Color(0.7, 0.5, 0.3), "level": ""},
	{"id": &"squid", "name": "Lula Abissal", "stage": "Fossa Abissal", "weapon": &"abyss_jet",
		"weak": &"volt_discharge", "color": Color(0.3, 0.4, 0.9), "level": ""},
	{"id": &"ray", "name": "Raia Elétrica", "stage": "Recife Voltaico", "weapon": &"volt_discharge",
		"weak": &"spore_cloud", "color": Color(0.4, 0.9, 1.0), "level": ""},
	{"id": &"fungus", "name": "Fungo Esporífero", "stage": "Pântano de Esporos", "weapon": &"spore_cloud",
		"weak": &"magma_shell", "color": Color(0.6, 0.85, 0.3), "level": ""},
	{"id": &"snail", "name": "Caracol Vulcânico", "stage": "Caldeira Vulcânica", "weapon": &"magma_shell",
		"weak": &"glacier_blade", "color": Color(1.0, 0.35, 0.15), "level": ""},
	{"id": &"mantis", "name": "Louva-a-deus Glacial", "stage": "Geleira Fóssil", "weapon": &"glacier_blade",
		"weak": &"prism_dust", "color": Color(0.7, 0.9, 1.0), "level": ""},
	{"id": &"moth", "name": "Mariposa de Cristal", "stage": "Caverna Prismática", "weapon": &"prism_dust",
		"weak": &"plasma_sting", "color": Color(0.9, 0.6, 1.0), "level": ""},
]

## Armas: o canhão (infinito) e as das Bestas (gastam energia).
const WEAPONS := {
	&"buster": {"name": "Canhão Simbionte", "color": Color(0.48, 1.0, 0.88), "cost": 0},
	&"plasma_sting": {"name": "Ferrão de Plasma", "color": Color(1.0, 0.7, 0.2), "cost": 1},
	&"seismic_hammer": {"name": "Martelo Sísmico", "color": Color(0.75, 0.55, 0.35), "cost": 2},
	&"abyss_jet": {"name": "Jato Abissal", "color": Color(0.35, 0.45, 1.0), "cost": 1},
	&"volt_discharge": {"name": "Descarga Voltaica", "color": Color(0.5, 0.95, 1.0), "cost": 2},
	&"spore_cloud": {"name": "Nuvem de Esporos", "color": Color(0.65, 0.9, 0.35), "cost": 2},
	&"magma_shell": {"name": "Casco de Magma", "color": Color(1.0, 0.4, 0.15), "cost": 2},
	&"glacier_blade": {"name": "Lâmina Glacial", "color": Color(0.75, 0.92, 1.0), "cost": 1},
	&"prism_dust": {"name": "Pó Prismático", "color": Color(0.95, 0.65, 1.0), "cost": 2},
}

## Peças da armadura simbionte, escondidas em casulos nas fases.
const ARMOR := {
	&"legs": {"name": "Pernas Saltadoras", "hint": "Dash no ar (uma vez por pulo)"},
	&"arms": {"name": "Braços Condutores", "hint": "Carga máxima mais forte; armas das Bestas também carregam"},
	&"body": {"name": "Carapaça Densa", "hint": "Metade do dano recebido"},
	&"head": {"name": "Elmo Sensorial", "hint": "Revela paredes frágeis e itens escondidos"},
}

var defeated: Array[StringName] = []
var weapons: Array[StringName] = [BUSTER]
var energy: Dictionary[StringName, int] = {}
var armor: Array[StringName] = []
var hearts: Array[String] = []
var collected: Dictionary[String, bool] = {}
var intro_cleared := false

var health := BASE_HEALTH
var current_weapon: StringName = BUSTER
## Fase sendo jogada (caminho do mapa) e o chefe dela.
var current_level := ""
var current_boss: StringName = &""
## Onde a caçadora renasce na fase atual (zero = no início).
var checkpoint := Vector2.ZERO


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	load_game()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_fullscreen"):
		var full := DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if full else DisplayServer.WINDOW_MODE_FULLSCREEN)


# --- Vida ---------------------------------------------------------------------

func max_health() -> int:
	return BASE_HEALTH + HEALTH_PER_HEART * hearts.size()


func set_health(value: int) -> void:
	health = clampi(value, 0, max_health())
	health_changed.emit(health, max_health())


func restore_all() -> void:
	set_health(max_health())
	for weapon in weapons:
		if weapon != BUSTER:
			energy[weapon] = MAX_ENERGY
	energy_changed.emit(current_weapon, weapon_energy(current_weapon), MAX_ENERGY)


# --- Armas --------------------------------------------------------------------

func weapon_energy(weapon: StringName) -> int:
	return MAX_ENERGY if weapon == BUSTER else energy.get(weapon, 0)


func select_weapon(weapon: StringName) -> void:
	if weapon in weapons:
		current_weapon = weapon
		weapon_changed.emit(weapon)
		energy_changed.emit(weapon, weapon_energy(weapon), MAX_ENERGY)


func cycle_weapon(step: int) -> void:
	var index := weapons.find(current_weapon)
	select_weapon(weapons[posmod(index + step, weapons.size())])


## Gasta energia da arma atual; retorna false se não houver o bastante.
func spend_energy(amount: int) -> bool:
	if current_weapon == BUSTER or amount <= 0:
		return true
	var left := weapon_energy(current_weapon)
	if left < amount:
		return false
	energy[current_weapon] = left - amount
	energy_changed.emit(current_weapon, energy[current_weapon], MAX_ENERGY)
	return true


func add_energy(amount: int) -> void:
	# Vai para a arma atual; com o canhão, para a mais vazia.
	var target := current_weapon
	if target == BUSTER:
		var lowest := MAX_ENERGY
		for weapon in weapons:
			if weapon != BUSTER and weapon_energy(weapon) < lowest:
				lowest = weapon_energy(weapon)
				target = weapon
	if target == BUSTER:
		return
	energy[target] = mini(weapon_energy(target) + amount, MAX_ENERGY)
	energy_changed.emit(current_weapon, weapon_energy(current_weapon), MAX_ENERGY)


func weapon_color(weapon: StringName = &"") -> Color:
	var id := current_weapon if weapon == &"" else weapon
	return WEAPONS.get(id, WEAPONS[BUSTER])["color"]


# --- Chefes e fases -------------------------------------------------------------

func boss_info(id: StringName) -> Dictionary:
	for boss: Dictionary in BOSSES:
		if boss["id"] == id:
			return boss
	return {}


## Multiplicador de dano de uma arma contra um chefe (fraqueza = 4x).
func damage_against(boss_id: StringName, weapon: StringName) -> float:
	var info := boss_info(boss_id)
	if info.is_empty():
		return 1.0
	return 4.0 if info["weak"] == weapon else 1.0


func defeat_boss(id: StringName) -> void:
	if id in defeated:
		return
	defeated.append(id)
	var weapon: StringName = boss_info(id).get("weapon", &"")
	if weapon != &"" and weapon not in weapons:
		weapons.append(weapon)
		energy[weapon] = MAX_ENERGY
	save_game()


func has_armor(part: StringName) -> bool:
	return part in armor


func collect(item_id: String) -> void:
	collected[item_id] = true


func is_collected(item_id: String) -> bool:
	return collected.has(item_id)


func add_armor(part: StringName) -> void:
	if part not in armor:
		armor.append(part)
		save_game()


func add_heart(heart_id: String) -> void:
	if heart_id not in hearts:
		hearts.append(heart_id)
		set_health(health + HEALTH_PER_HEART)
		save_game()


func start_level(path: String, boss: StringName = &"") -> void:
	current_level = path
	current_boss = boss
	checkpoint = Vector2.ZERO
	select_weapon(BUSTER)
	restore_all()
	get_tree().change_scene_to_file(LEVEL_SCENE)


func go_to_stage_select() -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file(STAGE_SELECT_SCENE)


func go_to_title() -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file(TITLE_SCENE)


# --- Salvamento ------------------------------------------------------------------

func new_game() -> void:
	defeated.clear()
	weapons = [BUSTER]
	energy.clear()
	armor.clear()
	hearts.clear()
	collected.clear()
	intro_cleared = false
	health = max_health()
	save_game()


func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)


func save_game() -> void:
	var data := {
		"version": SAVE_VERSION,
		"defeated": defeated.map(func(id: StringName) -> String: return String(id)),
		"weapons": weapons.map(func(id: StringName) -> String: return String(id)),
		"armor": armor.map(func(id: StringName) -> String: return String(id)),
		"hearts": hearts,
		"collected": collected.keys(),
		"intro_cleared": intro_cleared,
	}
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data, "\t"))


func load_game() -> void:
	if not has_save():
		return
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if not data is Dictionary or int(data.get("version", 0)) != SAVE_VERSION:
		return
	defeated.clear()
	for id: String in data.get("defeated", []):
		defeated.append(StringName(id))
	weapons = [BUSTER]
	for id: String in data.get("weapons", []):
		if WEAPONS.has(StringName(id)) and StringName(id) not in weapons:
			weapons.append(StringName(id))
	for id: String in data.get("armor", []):
		armor.append(StringName(id))
	for id: String in data.get("hearts", []):
		hearts.append(id)
	for id: String in data.get("collected", []):
		collected[id] = true
	intro_cleared = bool(data.get("intro_cleared", false))
	health = max_health()
