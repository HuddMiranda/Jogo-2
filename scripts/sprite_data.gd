class_name SpriteData
## Gerado por tools/generate_sprites.py. Não edite à mão.

const SHEETS := {
	"hero": {
		"frame": [64, 64],
		"origin": [32, 60],
		"anims": {
			"idle": {
				"row": 0,
				"frames": 4,
				"fps": 5
			},
			"run": {
				"row": 1,
				"frames": 10,
				"fps": 16
			},
			"jump": {
				"row": 2,
				"frames": 2,
				"fps": 8
			},
			"fall": {
				"row": 3,
				"frames": 2,
				"fps": 8
			},
			"dash": {
				"row": 4,
				"frames": 2,
				"fps": 10
			},
			"wall": {
				"row": 5,
				"frames": 1,
				"fps": 1
			},
			"hurt": {
				"row": 6,
				"frames": 1,
				"fps": 1
			}
		},
		"shoulders": {
			"idle": [[3.1, -29.5], [3.1, -30.0], [3.1, -29.5], [3.1, -29.0]],
			"run": [[5.8, -28.5], [5.8, -29.7], [5.8, -30.4], [5.8, -30.4], [5.8, -29.7], [5.8, -28.5], [5.8, -29.7], [5.8, -30.4], [5.8, -30.4], [5.8, -29.7]],
			"jump": [[3.9, -27.6], [3.9, -27.6]],
			"fall": [[2.5, -28.0], [2.5, -28.0]],
			"dash": [[9.3, -22.9], [9.3, -22.9]],
			"wall": [[1.1, -28.8]],
			"hurt": [[-2.2, -27.0]]
		},
		"arm_row": 7,
		"arm_origin": [32, 32],
		"muzzle": [19.0, 2.5]
	},
	"crawler": {
		"frame": [48, 32],
		"origin": [20, 30],
		"anims": {
			"walk": {
				"row": 0,
				"frames": 4,
				"fps": 8
			},
			"shoot": {
				"row": 1,
				"frames": 1,
				"fps": 1
			}
		}
	},
	"flyer": {
		"frame": [48, 40],
		"origin": [24, 22],
		"anims": {
			"fly": {
				"row": 0,
				"frames": 3,
				"fps": 18
			}
		}
	},
	"turret": {
		"frame": [32, 32],
		"origin": [16, 30],
		"anims": {
			"closed": {
				"row": 0,
				"frames": 1,
				"fps": 1
			},
			"opening": {
				"row": 1,
				"frames": 1,
				"fps": 1
			},
			"open": {
				"row": 2,
				"frames": 1,
				"fps": 1
			}
		}
	},
	"wasp": {
		"frame": [96, 96],
		"origin": [48, 84],
		"anims": {
			"idle": {
				"row": 0,
				"frames": 4,
				"fps": 10
			},
			"dash": {
				"row": 1,
				"frames": 2,
				"fps": 12
			},
			"shoot": {
				"row": 2,
				"frames": 2,
				"fps": 6
			},
			"hurt": {
				"row": 3,
				"frames": 1,
				"fps": 1
			}
		}
	},
	"items": {
		"frame": [32, 32],
		"origin": [16, 30],
		"anims": {
			"health_small": {
				"row": 0,
				"frames": 4,
				"fps": 6
			},
			"health_big": {
				"row": 1,
				"frames": 4,
				"fps": 6
			},
			"energy_small": {
				"row": 2,
				"frames": 4,
				"fps": 6
			},
			"energy_big": {
				"row": 3,
				"frames": 4,
				"fps": 6
			},
			"heart": {
				"row": 4,
				"frames": 4,
				"fps": 6
			},
			"capsule": {
				"row": 5,
				"frames": 4,
				"fps": 6
			}
		}
	}
}
