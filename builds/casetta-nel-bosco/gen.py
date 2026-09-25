#!/usr/bin/env python3
"""Casetta nel bosco v2: senza alberi, con più dettagli.
Ogni blocco della palette è verificato contro il database ufficiale
(minecraft_blocks_java_26.1.json, scaricato da GitHub): nome, forma,
altezza e colore vengono da lì, non da conoscenza pregressa.

Convenzioni: X = ovest->est, Y = alto, Z = nord->sud (Z crescente = sud).
facing degli scalini = direzione del lato ALTO (N=-Z, S=+Z, E=+X, W=-X).
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent
DB_PATH = REPO / "database" / "minecraft_blocks_java_26.1.json"
W, H, D = 28, 11, 22          # X, Y, Z
AIR = ".."

db = json.load(open(DB_PATH, encoding="utf-8"))
DB = {b["id"]: b for b in db["blocks"]}
DB_VERSION = db["meta"]["version"]

# ------------------------------------------------------------- palette ----
# codice -> id reale nel database. Forma/nome/altezza/colore letti dal db.
BLOCK_IDS = {
    "GR": "grass_block", "CB": "cobblestone", "DP": "dirt_path",
    "SP": "spruce_planks", "SL": "spruce_log", "ST": "stripped_spruce_log",
    "SS": "spruce_stairs", "SB": "spruce_slab", "SD": "spruce_door",
    "SF": "spruce_fence", "GP": "glass_pane",
    "CW": "cobblestone_wall", "CS": "cobblestone_stairs",
    "LA": "lantern", "CH": "chest", "BA": "barrel", "FU": "furnace",
    "CT": "crafting_table", "BS": "bookshelf", "BD": "red_bed",
    "HB": "hay_block", "LD": "ladder", "BL": "bell",
    "FL": "farmland", "WH": "wheat", "WA": "water",
    "FP": "flower_pot", "PP": "potted_poppy", "PD": "potted_dandelion",
}
# forma reale del database -> forma di rendering del visualizzatore (vedi SKILL.md)
SHAPE_MAP = {
    "full": "full", "slab": "slab", "stair": "stair",
    "wall": "wall", "fence": "fence", "pane": "pane", "door": "door",
}
# per i blocchi mappati su "other": ingombro approssimato [dx, dy(=altezza db), dz]
OTHER_SIZE = {
    "lantern": (0.375, None, 0.375), "chest": (0.875, None, 0.875),
    "bed": (1.0, None, 1.0), "hay_block": (1.0, None, 1.0),
    "ladder": (0.125, None, 0.75), "bell": (0.5, None, 0.5),
    "farmland": (1.0, None, 1.0), "passable": (1.0, None, 1.0),  # wheat, water
    "potted": (0.375, None, 0.375),
}

PALETTE = {}
for code, mc_id in BLOCK_IDS.items():
    assert mc_id in DB, f"{mc_id!r} non trovato nel database blocchi"
    b = DB[mc_id]
    shape = SHAPE_MAP.get(b["shape"])
    size = None
    if shape is None:
        shape = "other"
        dx, _, dz = OTHER_SIZE.get(b["shape"], (0.75, None, 0.75))
        size = [dx, round(b["height"], 4) or 0.875, dz]   # water: height 0 nel db -> 0.875 (livello sorgente)
    PALETTE[code] = {"id_db": mc_id, "name_en": b["name_en"], "name_it": b["name_it"],
                      "color": b["color"], "shape": shape, "height_db": b["height"]}
    if size:
        PALETTE[code]["size"] = size
ORDER = list(BLOCK_IDS.keys())

grid = [[[AIR] * W for _ in range(D)] for _ in range(H)]   # grid[y][z][x]
facing = {}


def put(x, y, z, code, f=None, over=True):
    assert 0 <= x < W and 0 <= y < H and 0 <= z < D, (code, x, y, z)
    assert code in PALETTE, code
    if not over and grid[y][z][x] != AIR:
        return
    grid[y][z][x] = code
    if f:
        assert PALETTE[code]["shape"] == "stair", code
        facing[f"{x},{y},{z}"] = f


def rect(x0, x1, z0, z1, y, code, edge_only=False):
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            if edge_only and not (x in (x0, x1) or z in (z0, z1)):
                continue
            put(x, y, z, code)


# ---- terreno ---------------------------------------------------------------
for z in range(D):
    for x in range(W):
        put(x, 0, z, "GR")

# =========================================================== CASETTA =======
X0, X1, Z0, Z1 = 6, 15, 6, 13     # perimetro esterno (muri inclusi)
DX = 11                            # colonna della porta
ZR = (Z0 + Z1) // 2                # 9: prima colonna del colmo (colmo = ZR, ZR+1)

# fondamenta + pavimento
rect(X0, X1, Z0, Z1, 0, "CB", edge_only=True)
for z in range(Z0 + 1, Z1):
    for x in range(X0 + 1, X1):
        put(x, 0, z, "SP")

# muri: y1 base in pietrisco, y2-3 in abete con angoli in tronco
for z in range(Z0, Z1 + 1):
    for x in range(X0, X1 + 1):
        if not (x in (X0, X1) or z in (Z0, Z1)):
            continue
        corner = x in (X0, X1) and z in (Z0, Z1)
        put(x, 1, z, "CB")
        for y in (2, 3):
            put(x, y, z, "SL" if corner else "SP")

# porta (sud) e finestre
put(DX, 1, Z1, "SD")
put(DX, 2, Z1, "SD")
for wx in (8, 13):
    put(wx, 2, Z1, "GP")
put(11, 2, Z0, "GP")               # finestra nord, di fronte alla porta
put(X0, 2, ZR, "GP")               # finestra ovest

# camino: canna in pietrisco sul muro est, sale oltre il tetto, cappello di scalini
for y in (1, 2, 3):
    put(X1, y, ZR, "CB")
for y in range(1, 9):
    put(X1 + 1, y, ZR, "CB")
for d, f in ((0, "N"), (1, "S"), (-1, "W"), (0, "E")):
    pass
put(X1 + 1, 8, ZR - 1, "CS", "S")
put(X1 + 1, 8, ZR, "CS", "N")
put(X1 - 1, 1, ZR, "FU")           # fornace addossata al camino, dentro casa

# tetto a due falde, colmo largo 2 (ZR, ZR+1); gronda sporgente di 1
for x in range(X0, X1 + 1):
    put(x, 3, Z0 - 1, "SS", "S")
    put(x, 4, Z0, "SS", "S")
    put(x, 5, Z0 + 1, "SS", "S")
    put(x, 6, Z0 + 2, "SS", "S")
    put(x, 6, ZR, "SP")
    put(x, 6, ZR + 1, "SP")
    put(x, 6, Z1 - 2, "SS", "N")
    put(x, 5, Z1 - 1, "SS", "N")
    put(x, 4, Z1, "SS", "N")
    put(x, 3, Z1 + 1, "SS", "N")
# timpani (infilaggio triangolare) + finestrino nel timpano ovest
GABLE_FILL = {Z0 + 1: (4,), Z0 + 2: (4, 5), ZR: (4, 5), ZR + 1: (4, 5), Z1 - 2: (4, 5), Z1 - 1: (4,)}
for gx in (X0, X1):
    for z, ys in GABLE_FILL.items():
        for y in ys:
            if gx == X0 and z == ZR and y == 5:
                put(gx, y, z, "GP")            # oblò del sottotetto
            else:
                put(gx, y, z, "SP")

# soppalco (sottotetto), con apertura per la scala a pioli in (7, 8)
LOFT_HOLE = (7, 8)
for z in range(Z0 + 1, Z1):
    for x in range(X0 + 1, X1):
        if (x, z) == LOFT_HOLE:
            continue
        put(x, 4, z, "SP")
put(*LOFT_HOLE[:1], 1, LOFT_HOLE[1], "LD")   # scala a pioli, muro ovest interno
put(LOFT_HOLE[0], 2, LOFT_HOLE[1], "LD")
put(LOFT_HOLE[0], 3, LOFT_HOLE[1], "LD")
put(12, 5, 8, "BD"); put(13, 5, 8, "BD")     # letto in soppalco
put(8, 5, 11, "CH")                          # baule in soppalco
put(10, 5, 9, "LA")                          # lanterna in soppalco

# arredi al piano terra
put(7, 1, 9, "BS"); put(7, 1, 10, "BS"); put(7, 1, 11, "BS")   # libreria, muro ovest
put(8, 1, 12, "CH")                                            # baule
put(9, 1, 11, "SF"); put(9, 2, 11, "SB")                       # tavolino (gambo + piano)
put(10, 1, 11, "SF"); put(10, 2, 11, "SB")
put(12, 1, 12, "CT")                                           # banco da lavoro
put(13, 1, 12, "FU")                                           # fornace
put(13, 1, 11, "BA")                                           # barile
put(9, 1, 8, "LA")                                             # lanterna a terra

# =========================================================== PORTICO =======
PX0, PX1, PZ0, PZ1 = 9, 13, 14, 16
for z in range(PZ0, PZ1 + 1):
    for x in range(PX0, PX1 + 1):
        put(x, 0, z, "SP")
for (px, pz) in ((PX0, PZ1), (PX1, PZ1)):
    put(px, 1, pz, "SF"); put(px, 2, pz, "SF"); put(px, 3, pz, "LA")
for x in range(PX0, PX1 + 1):
    for z in range(PZ0, PZ1 + 1):
        put(x, 4, z, "SB")                     # tettoia piana sul portico
for x in range(PX0 + 1, PX1):                       # gradino d'ingresso (dorso verso il portico)
    put(x, 0, PZ1 + 1, "CS", "N")

# =========================================================== VIALETTO ======
for z in range(PZ1 + 2, D):
    for x in range(10, 13):
        put(x, 0, z, "DP")
put(11, 1, D - 3, "BL")
for x, z, code in ((9, PZ1 + 2, "PP"), (13, PZ1 + 2, "PD"), (9, D - 2, "FP"), (13, D - 2, "FP")):
    put(x, 1, z, code)

# =========================================================== POZZO =========
WX0, WX1, WZ0, WZ1 = 17, 19, 9, 11
rect(WX0, WX1, WZ0, WZ1, 1, "CW", edge_only=True)
put(18, 0, 10, "WA")
put(WX0, 2, WZ0, "SF"); put(WX0, 3, WZ0, "LA")
put(WX1, 2, WZ1, "SF"); put(WX1, 3, WZ1, "LA")

# =========================================================== LEGNAIA =======
YX0, YX1, YZ0, YZ1 = 17, 21, 13, 17
for (yx, yz) in ((YX0, YZ0), (YX1, YZ0), (YX0, YZ1), (YX1, YZ1)):
    put(yx, 1, yz, "SF"); put(yx, 2, yz, "SF")
for x in range(YX0, YX1 + 1):
    for z in range(YZ0, YZ1 + 1):
        put(x, 3, z, "SP")
for dx in (0, 1):
    for dz in (0, 1):
        put(YX0 + 1 + dx, 1, YZ0 + 1 + dz, "ST")
put(YX0 + 1, 1, YZ1 - 1, "HB"); put(YX0 + 2, 1, YZ1 - 1, "HB")
put(YX1 - 1, 1, YZ0 + 1, "BA")
put((YX0 + YX1) // 2, 2, (YZ0 + YZ1) // 2, "LA")

# =========================================================== ORTO ==========
OX0, OX1, OZ0, OZ1 = 22, 26, 6, 13
rect(OX0, OX1, OZ0, OZ1, 1, "SF", edge_only=True)
grid[1][ (OZ0 + OZ1) // 2 ][OX0] = AIR                     # varco d'ingresso
for z in range(OZ0 + 1, OZ1):
    for x in range(OX0 + 1, OX1):
        put(x, 0, z, "FL")
        if (x + z) % 2 == 0:
            put(x, 1, z, "WH")

# ------------------------------------------------------ edifici (bbox) -----
BUILDINGS = [
    {"id": "casetta", "name": "Casetta", "bbox": [X0, 0, Z0, X1 + 1, 8, Z1]},
    {"id": "portico", "name": "Portico", "bbox": [PX0, 0, PZ0, PX1, 4, PZ1]},
    {"id": "vialetto", "name": "Vialetto d'ingresso", "bbox": [8, 0, PZ1 + 1, 14, 1, D - 1]},
    {"id": "pozzo", "name": "Pozzo", "bbox": [WX0, 0, WZ0, WX1, 3, WZ1]},
    {"id": "legnaia", "name": "Legnaia", "bbox": [YX0, 0, YZ0, YX1, 3, YZ1]},
    {"id": "orto", "name": "Orto", "bbox": [OX0, 0, OZ0, OX1, 1, OZ1]},
    {"id": "terreno", "name": "Terreno", "bbox": [0, 0, 0, W - 1, H - 1, D - 1]},
]


def owner(x, y, z):
    for i, b in enumerate(BUILDINGS):
        x0, y0, z0, x1, y1, z1 = b["bbox"]
        if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1:
            return i
    return -1


# ------------------------------------------------------------ validazione --
tot = Counter()
per_b = [Counter() for _ in BUILDINGS]
per_layer = Counter()
for y in range(H):
    for z in range(D):
        for x in range(W):
            c = grid[y][z][x]
            if c == AIR:
                continue
            assert c in PALETTE, (c, x, y, z)
            o = owner(x, y, z)
            assert o >= 0, (x, y, z)
            tot[c] += 1
            per_b[o][c] += 1
            per_layer[y] += 1
n_stairs = sum(v for k, v in tot.items() if PALETTE[k]["shape"] == "stair")
assert n_stairs == len(facing), (n_stairs, len(facing))
assert tot["SD"] == 2 and tot["BD"] == 2

data = {
    "title": "Casetta nel bosco",
    "subtitle": "Capanna in abete con soppalco, portico, camino, pozzo, legnaia e orto. Ruota il 3D, scorri i livelli, taglia in verticale, isola un edificio o un tipo di blocco.",
    "db_version": DB_VERSION,
    "dims": [W, H, D],
    "order": ORDER,
    "palette": {c: {"en": p["name_en"], "it": p["name_it"], "color": p["color"],
                     "shape": p["shape"], **({"size": p["size"]} if "size" in p else {})}
                for c, p in PALETTE.items()},
    "buildings": BUILDINGS,
    "layers": [["".join(row) for row in grid[y]] for y in range(H)],
    "facing": facing,
    "start": {"y": 1, "axis": "x", "pos": DX},
}

# Questo generatore produce SOLO il dato (build.json): il rendering è a carico
# di /viewer.html (motore condiviso da tutte le build del repo), aperto come
# viewer.html?b=builds/casetta-nel-bosco/build.json
(HERE / "build.json").write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
(HERE / "_expected.json").write_text(json.dumps({
    "total": sum(tot.values()), "by_code": dict(tot),
    "by_building": [dict(c) for c in per_b], "by_layer": [per_layer[y] for y in range(H)],
}, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"db versione {DB_VERSION} | dims {W}x{H}x{D} | totale blocchi {sum(tot.values())}")
for b, c in zip(BUILDINGS, per_b):
    print(f'  {b["name"]}: {sum(c.values())}')
print("  per blocco:", dict(tot.most_common()))
print("  altre-forme (other) usate:", sorted({c for c in tot if PALETTE[c]["shape"] == "other"}))
sys.exit(0)
