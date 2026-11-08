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
			"idle": [[3.5, -29.0], [3.5, -29.5], [3.5, -29.0], [3.5, -28.5]],
			"run": [[5.9, -28.1], [5.9, -29.2], [5.9, -30.0], [5.9, -30.0], [5.9, -29.2], [5.9, -28.1], [5.9, -29.2], [5.9, -30.0], [5.9, -30.0], [5.9, -29.2]],
			"jump": [[4.3, -27.1], [4.3, -27.1]],
			"fall": [[3.0, -27.5], [3.0, -27.5]],
			"dash": [[8.9, -22.6], [8.9, -22.6]],
			"wall": [[1.7, -28.3]],
			"hurt": [[-1.1, -26.6]]
		},
		"arm_row": 7,
		"arm_origin": [32, 32],
		"muzzle": [18.0, 2.5]
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
