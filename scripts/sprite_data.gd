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
				"fps": 18
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
			},
			"spin": {
				"row": 7,
				"frames": 8,
				"fps": 24
			}
		},
		"shoulders": {
			"idle": [[5, -30], [5, -30], [5, -30], [5, -30]],
			"run": [[6, -30], [6, -28], [6, -22], [6, -22], [6, -26], [6, -30], [6, -28], [6, -22], [6, -22], [6, -26]],
			"jump": [[5, -28], [5, -28]],
			"fall": [[5, -29], [5, -29]],
			"dash": [[6, -25], [6, -25]],
			"wall": [[5, -30]],
			"hurt": [[4, -29]],
			"spin": [[5, -28], [5, -28], [5, -28], [5, -28], [5, -28], [5, -28], [5, -28], [5, -28]]
		},
		"arm_row": 8,
		"arm_origin": [32, 32],
		"muzzle_down": [-1, 12],
		"muzzle": [13, 3]
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
