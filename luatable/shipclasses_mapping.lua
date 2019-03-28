local d = {}
---------------------------------
--   以下为舰娘和舰级的对应数据   -- 
---------------------------------

d.shipclassDataTb = {
	["J"] = {
		519,
		394
	},
	["U型潜艇IT"] = {
		539
	},
	["U型潜艇IXC"] = {
		431,
		334
	},
	["Z1"] = {
		174,
		180,
		310,
		311,
		179,
		175
	},
	["三式潜航运输艇"] = {
		402,
		163
	},
	["云龙"] = {
		404,
		429,
		430,
		332,
		331,
		406
	},
	["伊400"] = {
		9181
	},
	["伊501"] = {
		530
	},
	["伊丽莎白女王"] = {
		439,
		364
	},
	["伊势"] = {
		77,
		82,
		88,
		87
	},
	["俾斯麦"] = {
		173,
		171,
		178,
		172
	},
	["凤翔"] = {
		89,
		285
	},
	["列克星敦"] = {
		545,
		550,
		438,
		433
	},
	["初春"] = {
		38,
		40,
		41,
		419,
		239,
		238,
		240,
		326,
		241,
		39
	},
	["利根"] = {
		189,
		274,
		71,
		273,
		72,
		188
	},
	["加贺"] = {
		84,
		278
	},
	["千岁"] = {
		108,
		109,
		297,
		107,
		105,
		106,
		103,
		296,
		291,
		102,
		292,
		104
	},
	["占守"] = {
		518,
		517,
		376,
		377
	},
	["卡萨布兰卡"] = {
		396,
		544
	},
	["古鹰"] = {
		60,
		59,
		262,
		417,
		416,
		263
	},
	["吕号"] = {
		436
	},
	["吹雪"] = {
		201,
		12,
		203,
		420,
		32,
		206,
		11,
		9,
		426,
		10,
		205,
		33,
		368,
		202,
		204,
		486
	},
	["哥特兰"] = {
		579,
		574
	},
	["埃塞克斯"] = {
		397,
		549
	},
	["塔什干"] = {
		395,
		516
	},
	["塔斯特司令官"] = {
		372,
		491
	},
	["夕云"] = {
		303,
		359,
		564,
		133,
		424,
		345,
		324,
		302,
		528,
		543,
		542,
		344,
		373,
		485,
		563,
		135,
		484,
		349,
		304,
		325,
		686,
		452,
		425,
		688,
		527,
		409,
		453,
		134,
		680,
		410
	},
	["夕张"] = {
		293,
		115
	},
	["大凤"] = {
		156,
		153
	},
	["大和"] = {
		546,
		136,
		131,
		148,
		143
	},
	["大淀"] = {
		321,
		183
	},
	["大鲸"] = {
		184
	},
	["大鹰"] = {
		534,
		529,
		536,
		380,
		381,
		526
	},
	["天鹰"] = {
		444,
		365
	},
	["天龙"] = {
		51,
		478,
		214,
		213,
		52,
		477
	},
	["妙高"] = {
		63,
		267,
		64,
		319,
		266,
		268,
		192,
		193,
		265,
		62,
		65,
		194
	},
	["岛风"] = {
		229,
		50
	},
	["川内"] = {
		158,
		160,
		54,
		224,
		223,
		56,
		159,
		222,
		55
	},
	["巡潜3"] = {
		400,
		128
	},
	["巡潜乙"] = {
		367,
		401,
		483,
		191
	},
	["巡潜乙（改二）"] = {
		127,
		399
	},
	["巡潜甲型改二"] = {
		495,
		494,
		375,
		374
	},
	["希佩尔海军上将"] = {
		176,
		177
	},
	["弗莱彻"] = {
		689,
		562
	},
	["扎拉"] = {
		496,
		361,
		449,
		358,
		448
	},
	["扶桑"] = {
		27,
		411,
		287,
		286,
		26,
		412
	},
	["择捉"] = {
		525,
		524,
		531,
		384,
		383,
		565,
		540,
		386,
		385,
		685
	},
	["改伊势"] = {
		553,
		554
	},
	["改最上"] = {
		503,
		504
	},
	["改风早"] = {
		460,
		352
	},
	["日振"] = {
		678,
		551,
		552,
		679
	},
	["日进"] = {
		586,
		690,
		581
	},
	["明石"] = {
		182,
		187
	},
	["春日丸"] = {
		521
	},
	["晓"] = {
		36,
		237,
		236,
		235,
		37,
		234,
		35,
		437,
		34,
		147
	},
	["最上"] = {
		130,
		125,
		508,
		509,
		70,
		129,
		124,
		120,
		121,
		73
	},
	["朝潮"] = {
		97,
		251,
		489,
		328,
		463,
		468,
		253,
		95,
		198,
		414,
		490,
		96,
		252,
		49,
		249,
		98,
		687,
		327,
		464,
		583,
		250,
		413,
		48,
		470,
		248,
		199
	},
	["海大VI"] = {
		398,
		126
	},
	["潜特"] = {
		403,
		155,
		493,
		606
	},
	["特种船丙"] = {
		161,
		166
	},
	["球磨"] = {
		101,
		216,
		100,
		217,
		118,
		57,
		58,
		25,
		99,
		146,
		547,
		215,
		24,
		119
	},
	["瑞穗"] = {
		348,
		451
	},
	["甘古特"] = {
		511,
		513,
		512
	},
	["白露"] = {
		144,
		457,
		498,
		246,
		43,
		47,
		459,
		469,
		458,
		243,
		245,
		46,
		369,
		242,
		244,
		351,
		42,
		45,
		405,
		145,
		497,
		247,
		323,
		44,
		350
	},
	["皇家方舟"] = {
		393,
		515
	},
	["睦月"] = {
		1,
		254,
		256,
		30,
		418,
		29,
		6,
		548,
		435,
		165,
		308,
		31,
		260,
		309,
		255,
		258,
		164,
		434,
		7,
		2,
		261,
		481,
		259,
		366,
		257,
		28
	},
	["神威"] = {
		500,
		499,
		162
	},
	["神风"] = {
		475,
		473,
		387,
		476,
		370,
		472,
		474,
		371,
		471,
		363
	},
	["祥凤"] = {
		560,
		282,
		116,
		74,
		117,
		555
	},
	["秋月"] = {
		532,
		330,
		423,
		346,
		537,
		421,
		357,
		422
	},
	["秋津洲"] = {
		450,
		445
	},
	["约翰·C·巴特勒"] = {
		561,
		681
	},
	["纳尔逊"] = {
		576,
		571
	},
	["绫波"] = {
		231,
		94,
		390,
		207,
		15,
		14,
		480,
		16,
		230,
		93,
		13,
		195,
		208,
		232,
		407,
		391,
		479,
		233
	},
	["维托里奥·维内托"] = {
		446,
		447,
		442,
		441
	},
	["翔鹤"] = {
		288,
		462,
		111,
		461,
		112,
		467,
		466,
		110
	},
	["苍龙"] = {
		197,
		279,
		90
	},
	["衣阿华"] = {
		440,
		360
	},
	["西北风"] = {
		443,
		347,
		575,
		580
	},
	["赤城"] = {
		277,
		83
	},
	["金刚"] = {
		86,
		149,
		211,
		152,
		78,
		79,
		85,
		209,
		210,
		150,
		151,
		9183,
		212
	},
	["长良"] = {
		488,
		220,
		221,
		22,
		219,
		114,
		289,
		200,
		487,
		290,
		21,
		113,
		141,
		23,
		53,
		218
	},
	["长门"] = {
		573,
		275,
		81,
		541,
		80,
		276
	},
	["阳炎"] = {
		568,
		186,
		17,
		132,
		556,
		19,
		455,
		312,
		316,
		320,
		322,
		122,
		170,
		313,
		567,
		454,
		362,
		415,
		18,
		300,
		294,
		181,
		355,
		557,
		301,
		228,
		20,
		226,
		169,
		566,
		227,
		558,
		456,
		559,
		167,
		190,
		168,
		329,
		225,
		317,
		354
	},
	["阿贺野"] = {
		137,
		139,
		314,
		140,
		305,
		306,
		138,
		307
	},
	["青叶"] = {
		123,
		295,
		142,
		264,
		61
	},
	["飞鹰"] = {
		284,
		408,
		92,
		75,
		283
	},
	["飞龙"] = {
		91,
		196,
		280
	},
	["香取"] = {
		356,
		154,
		465,
		343
	},
	["马可尼"] = {
		605,
		535
	},
	["高雄"] = {
		271,
		66,
		69,
		272,
		68,
		427,
		428,
		269,
		270,
		9182,
		67
	},
	["黎塞留"] = {
		392,
		492
	},
	["齐柏林伯爵"] = {
		432,
		353
	},
	["龙凤"] = {
		185,
		318
	},
	["龙骧"] = {
		76,
		281,
		157
	}
}

return d
