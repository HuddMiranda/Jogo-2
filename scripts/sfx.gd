extends Node
## Efeitos sonoros sintetizados na hora (autoload "Sfx"), estilo chip de
## console: ondas quadradas, dente de serra e ruído com varredura de tom.
## Uso: Sfx.play(&"shot"). Para trocar por arquivos .ogg/.wav, ponha-os em
## res://audio/sfx/<nome>.ogg: eles têm preferência sobre o som sintetizado.

const RATE := 22050
const VOICES := 12

## nome: [tom inicial, tom final, duração (s), onda, volume, ruído (0 a 1)]
const SOUNDS := {
	&"slash": [1600.0, 300.0, 0.1, "saw", 0.3, 0.85],
	&"shot": [880.0, 520.0, 0.07, "square", 0.35, 0.0],
	&"shot_mid": [520.0, 240.0, 0.14, "square", 0.45, 0.1],
	&"shot_full": [300.0, 80.0, 0.3, "saw", 0.55, 0.25],
	&"charge": [180.0, 900.0, 0.5, "square", 0.18, 0.0],
	&"charged": [900.0, 1200.0, 0.12, "square", 0.2, 0.0],
	&"jump": [300.0, 600.0, 0.08, "square", 0.25, 0.0],
	&"land": [140.0, 60.0, 0.05, "square", 0.25, 0.4],
	&"dash": [200.0, 900.0, 0.12, "saw", 0.2, 0.5],
	&"hurt": [600.0, 120.0, 0.25, "saw", 0.45, 0.3],
	&"enemy_hit": [400.0, 200.0, 0.06, "square", 0.3, 0.2],
	&"no_damage": [1400.0, 1300.0, 0.05, "square", 0.25, 0.0],
	&"explode": [220.0, 30.0, 0.4, "square", 0.45, 0.85],
	&"boss_explode": [160.0, 20.0, 1.2, "saw", 0.6, 0.9],
	&"pickup": [700.0, 1400.0, 0.12, "square", 0.3, 0.0],
	&"heal": [500.0, 900.0, 0.05, "square", 0.2, 0.0],
	&"weapon_get": [300.0, 1500.0, 0.9, "square", 0.35, 0.0],
	&"menu_move": [900.0, 900.0, 0.04, "square", 0.2, 0.0],
	&"menu_select": [600.0, 1200.0, 0.12, "square", 0.3, 0.0],
	&"door": [90.0, 140.0, 0.6, "saw", 0.3, 0.4],
	&"death": [800.0, 40.0, 1.0, "square", 0.45, 0.2],
	&"enemy_shot": [500.0, 300.0, 0.08, "saw", 0.2, 0.2],
	&"boss_roar": [120.0, 60.0, 0.7, "saw", 0.5, 0.6],
}

var _streams: Dictionary[StringName, AudioStream] = {}
var _players: Array[AudioStreamPlayer] = []
var _next := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for name: StringName in SOUNDS:
		var path := "res://audio/sfx/%s.ogg" % name
		_streams[name] = load(path) if ResourceLoader.exists(path) else _synth(SOUNDS[name])
	for i in VOICES:
		var player := AudioStreamPlayer.new()
		add_child(player)
		_players.append(player)


func play(sound: StringName, pitch := 1.0, volume_db := 0.0) -> void:
	var stream: AudioStream = _streams.get(sound)
	if stream == null:
		return
	var player := _players[_next]
	_next = (_next + 1) % _players.size()
	player.stream = stream
	player.pitch_scale = pitch * randf_range(0.97, 1.03)
	player.volume_db = volume_db
	player.play()


func _synth(spec: Array) -> AudioStreamWAV:
	var f0: float = spec[0]
	var f1: float = spec[1]
	var duration: float = spec[2]
	var wave: String = spec[3]
	var volume: float = spec[4]
	var noise: float = spec[5]
	var count := int(RATE * duration)
	var data := PackedByteArray()
	data.resize(count * 2)
	var phase := 0.0
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(spec)
	var held := 0.0
	for i in count:
		var t := float(i) / count
		var freq := lerpf(f0, f1, t)
		phase = fmod(phase + freq / RATE, 1.0)
		var tone := (1.0 if phase < 0.5 else -1.0) if wave == "square" else phase * 2.0 - 1.0
		if i % 4 == 0:
			held = rng.randf_range(-1.0, 1.0)
		var envelope := minf(1.0, t * 40.0) * (1.0 - t) * (1.0 - t * 0.3)
		var sample := (tone * (1.0 - noise) + held * noise) * envelope * volume
		data.encode_s16(i * 2, int(clampf(sample, -1.0, 1.0) * 32000.0))
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = RATE
	stream.data = data
	return stream
