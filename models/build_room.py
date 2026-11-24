"""
Smart Room example - 3D model of the bedroom, one file per part.

Run:   pip install manifold3d trimesh numpy
       python build_room.py
Out:   parts/<name>.stl    every part on its own, in mm, in its own local coordinates
       parts/<name>.glb    the same part, coloured (Blender, three.js, online viewers)
       room.glb            the whole room, every part a named node, placed (metres, Y-up glTF)
       room_layout.json    where each part sits in the room (mm, Z-up), so you can rebuild it

Coordinates in this script (mm, Z up):
  x = 0..ROOM_W  west -> east      y = 0..ROOM_D  south (door) -> north (window)
  z = 0..ROOM_H  floor -> ceiling  walls sit OUTSIDE this box.

Part local coordinates (so each STL is easy to reuse):
  wall-mounted things: back against the wall at z=0, facing +z
  floor-standing things: standing on z=0, centred on x/y

The Room Panel (the room's only sensor/control device) is not modelled here: it is the
real case from https://github.com/gustavwrisberg/room-panel (hardware/case/out/),
copied into devices/ and placed next to the door.
Everything else is a simple stand-in with the right size, not a copy of any product's design.
"""
import json
from pathlib import Path

import numpy as np
import trimesh
import manifold3d as m
from manifold3d import Manifold as M, CrossSection as CS

m.set_circular_segments(40)
HERE = Path(__file__).parent
PARTS = HERE / "parts"
DEVICES = HERE / "devices"

# ------------------------------------------------------------------ ROOM PARAMETERS (mm)
ROOM_W, ROOM_D, ROOM_H = 4500.0, 3600.0, 2500.0
WALL_T, FLOOR_T = 100.0, 20.0

WINDOW_W, WINDOW_H, SILL_Z = 1200.0, 1300.0, 850.0       # north wall
WINDOW_X = ROOM_W / 2                                     # window centre
DOOR_W, DOOR_H, DOOR_X = 900.0, 2100.0, 1050.0            # south wall, door centre

RADIATOR_W, RADIATOR_H, RADIATOR_D, RADIATOR_Z = 1000.0, 600.0, 100.0, 150.0
PANEL_Z = 1400.0              # room panel centre height (by the door, light-switch height)

# ------------------------------------------------------------------ helpers
def box(x0, y0, z0, x1, y1, z1):
    return M.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

def cbox(w, d, h, z0=0.0):
    """box centred on x/y, standing on z0"""
    return box(-w / 2, -d / 2, z0, w / 2, d / 2, z0 + h)

def cyl(d, h, z0=0.0, x=0.0, y=0.0, d2=None):
    return M.cylinder(h, d / 2, (d2 if d2 else d) / 2).translate([x, y, z0])

def rbox(w, d, h, r, z0=0.0):
    """rounded-corner box centred on x/y"""
    r = min(r, w / 2 - 0.01, d / 2 - 0.01)
    return CS.square([w - 2 * r, d - 2 * r]).translate([-w / 2 + r, -d / 2 + r]) \
             .offset(r, m.JoinType.Round).extrude(h).translate([0, 0, z0])

def to_trimesh(man):
    mesh = man.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=True)

def rot(axis, deg):
    return trimesh.transformations.rotation_matrix(np.radians(deg), axis)

def move(x, y, z):
    return trimesh.transformations.translation_matrix([x, y, z])

def chain(*mats):
    out = np.eye(4)
    for a in mats:
        out = out @ a
    return out

def frame(origin, normal):
    """local x = to the right when you face the wall, local y = up, local z = into the room (normal)"""
    n = np.array(normal, float); n /= np.linalg.norm(n)
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(up, n)
    T = np.eye(4)
    T[:3, 0], T[:3, 1], T[:3, 2], T[:3, 3] = right, up, n, origin
    return T

def on_north_wall(x, z):   # wall at y = ROOM_D, facing south
    return frame([x, ROOM_D, z], [0, -1, 0])

def on_south_wall(x, z):   # wall at y = 0, facing north
    return frame([x, 0, z], [0, 1, 0])

# ------------------------------------------------------------------ PARTS
# Each builder returns a manifold in local coordinates.

def floor():
    return box(-WALL_T, -WALL_T, -FLOOR_T, ROOM_W + WALL_T, ROOM_D + WALL_T, 0)

def wall(length, openings=()):
    """local: x along the wall (0..length), y up, z = thickness (0 = room side, negative = outside)"""
    w = box(0, 0, -WALL_T, length, ROOM_H, 0)
    for (x0, y0, x1, y1) in openings:
        w -= box(x0, y0, -WALL_T - 1, x1, y1, 1)
    return w

def wall_north():
    x0 = WINDOW_X - WINDOW_W / 2
    return wall(ROOM_W + 2 * WALL_T, [(x0 + WALL_T, SILL_Z, x0 + WALL_T + WINDOW_W, SILL_Z + WINDOW_H)])

def wall_south():
    s0 = ROOM_W + WALL_T - (DOOR_X + DOOR_W / 2)     # local x runs east -> west on this wall
    return wall(ROOM_W + 2 * WALL_T, [(s0, 0, s0 + DOOR_W, DOOR_H)])

def wall_plain_ew():
    return wall(ROOM_D)

def window_frame():
    """outer frame, sits in the wall opening. local: x along wall centred, y up from sill, z = depth"""
    f, d = 60.0, 70.0
    outer = box(-WINDOW_W / 2, 0, -d, WINDOW_W / 2, WINDOW_H, 0)
    inner = box(-WINDOW_W / 2 + f, f, -d - 1, WINDOW_W / 2 - f, WINDOW_H - f, 1)
    sill = box(-WINDOW_W / 2 - 30, -20, -10, WINDOW_W / 2 + 30, 0, 160)   # inside window board
    return outer - inner + sill

def window_sash():
    f, d = 60.0, 56.0
    w, h = WINDOW_W - 2 * 60 + 2 * 15, WINDOW_H - 2 * 60 + 2 * 15
    outer = box(-w / 2, 0, -d, w / 2, h, 0)
    inner = box(-w / 2 + f, f, -d - 1, w / 2 - f, h - f, 1)
    return outer - inner

def window_glass():
    w, h = WINDOW_W - 2 * 60 - 2 * 45 + 20, WINDOW_H - 2 * 60 - 2 * 45 + 20
    return box(-w / 2, 0, -34, w / 2, h, -10)

def window_handle():
    base = rbox(30, 70, 12, 6)
    lever = box(-8, -5, 12, 8, 120, 26)
    return base + lever

def door():
    t = 40.0
    leaf = box(0, 0, -t, DOOR_W - 10, DOOR_H - 10, 0)
    handle = cyl(20, 60, 0, x=DOOR_W - 90, y=1050) + box(DOOR_W - 210, 1040, 50, DOOR_W - 90, 1060, 70)
    return leaf + handle

def blind_headrail():
    """cellular blind headrail with the motor end (IKEA HOPPVALS + motor on the room-panel J2 header).
    local: x along the wall centred, y up (top at 0), z out of the wall"""
    w = WINDOW_W + 100
    rail = box(-w / 2, -45, 0, w / 2, 0, 45)
    motor = box(w / 2 - 160, -55, 0, w / 2, 0, 55)          # motor + board housing at the right end
    brackets = sum((box(x - 20, -10, 0, x + 20, 10, 10) for x in (-w / 2 + 80, w / 2 - 240)), M())
    return rail + motor + brackets

def blind_fabric(drop=700.0, pleat=25.0):
    """cellular blind fabric hanging from the headrail, folded zig-zag. drop = how far down it is"""
    w = WINDOW_W + 60
    n = max(2, int(drop / pleat))
    pts = []
    for i in range(n + 1):
        pts.append([-drop + i * drop / n, 8.0 if i % 2 else 22.0])
    pts += [[p[0], p[1] - 4.0] for p in reversed(pts)]
    return _fabric_from_profile(pts, w)

def _fabric_from_profile(pts, w):
    # profile is (y, z): extrude along x
    sec = CS([[[p[1], p[0]] for p in pts]], m.FillRule.EvenOdd)            # 2D in (z, y)
    ext = sec.extrude(w)                               # (z, y, x)
    # map (a=z, b=y, c=x) -> (x, y, z)
    mesh = ext.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    v2 = np.column_stack([v[:, 2] - w / 2, v[:, 1] - 45, v[:, 0]])
    tri = np.asarray(mesh.tri_verts)[:, ::-1]           # axis swap flips winding
    return M(m.Mesh(vert_properties=v2.astype(np.float32), tri_verts=tri.astype(np.uint32)))

def blind_bottom_rail():
    w = WINDOW_W + 60
    return box(-w / 2, -25, 4, w / 2, 0, 30)

def radiator():
    """type-22 style panel radiator. local: x along the wall centred, y up from its bottom, z out of the wall"""
    w, h, d = RADIATOR_W, RADIATOR_H, RADIATOR_D
    back = box(-w / 2, 0, 15, w / 2, h, 30)
    front = box(-w / 2, 0, d - 15, w / 2, h, d)
    fins = sum((box(x - 1.5, 30, 30, x + 1.5, h - 30, d - 15) for x in np.arange(-w / 2 + 20, w / 2 - 10, 25)), M())
    top = box(-w / 2, h - 3, 15, w / 2, h, d)
    grooves = sum((box(x - 3, 20, d - 2, x + 3, h - 20, d + 1) for x in np.arange(-w / 2 + 50, w / 2 - 20, 50)), M())
    brackets = sum((box(x - 20, h - 80, 0, x + 20, h - 50, 15) for x in (-w / 2 + 120, w / 2 - 120)), M())
    return back + front + fins + top + brackets - grooves

def radiator_valve():
    """valve body + M30x1.5 valve thread the TRV screws onto. local: axis along +x"""
    body = cyl(28, 60).rotate([0, 90, 0])
    thread = cyl(30, 12, 60).rotate([0, 90, 0])
    pipe = cyl(16, 140, -140).translate([20, 0, 0])
    return body + thread + pipe

def trv():
    """generic smart radiator thermostat (IKEA LILJEBAGGE is the one used), axis along +x.
    Simple cylinder with a display face - a stand-in, not a copy of the product."""
    nut = cyl(36, 14)
    body = cyl(54, 80, 14, d2=52)
    cap = cyl(52, 6, 94, d2=44)
    display = box(-12, -14, 86, 12, 14, 101)          # flat display window on the end face
    return (nut + body + cap - box(-11, -13, 99, 11, 13, 102) + display).rotate([0, 90, 0])

def pendant_lamp():
    """ceiling pendant: canopy, cord, shade. local: hangs down from z=0 (ceiling)"""
    canopy = cyl(110, 25, -25)
    cord = cyl(6, 520, -545)
    shade_outer = cyl(400, 220, -760, d2=120)
    shade_inner = cyl(390, 212, -762, d2=112)
    socket = cyl(40, 50, -600)
    return canopy + cord + (shade_outer - shade_inner) + socket

def bulb():
    """smart bulb stand-in (IKEA KAJPLATS E27 is the one used)"""
    base = cyl(27, 25)
    neck = cyl(40, 20, 25, d2=58)
    globe = M.sphere(47.5).translate([0, 0, 85])
    return base + neck + globe

def robot_vacuum():
    """lidar robot vacuum stand-in (a Roborock is used in the example). local: on the floor, front = +y"""
    body = cyl(350, 80, 10)
    bumper = cyl(352, 45, 20) - cyl(340, 47, 19) - box(-200, -200, 0, 200, 0, 100)
    lidar = cyl(80, 15, 90)
    wheels = sum((box(sx * 120 - 12, -40, 0, sx * 120 + 12, 40, 30) for sx in (-1, 1)), M())
    brush = cyl(60, 6, 4, x=-110, y=90) + cyl(60, 6, 4, x=110, y=90)
    return body + bumper + lidar + wheels + brush

def vacuum_dock():
    """self-empty dock stand-in. local: back against the wall at y=0... standing on the floor, faces +y"""
    ramp = box(-170, 0, 0, 170, 300, 15)
    tower = rbox(320, 180, 420, 40).translate([0, 90, 0])
    return ramp + tower

def bed():
    """double bed 160 x 200, headboard at x=0 (against the wall), foot towards +x, centred on y"""
    L, W = 2000.0, 1600.0
    frame = box(60, -W / 2, 120, 60 + L, W / 2, 300)
    legs = sum((box(x, sy * (W / 2 - 60) - 30, 0, x + 60, sy * (W / 2 - 60) + 30, 120)
                for x in (80, L - 20) for sy in (-1, 1)), M())
    headboard = box(0, -W / 2 - 20, 0, 60, W / 2 + 20, 1050)
    mattress = box(80, -W / 2 + 15, 300, L + 40, W / 2 - 15, 520)
    return frame + legs + headboard + mattress

def bed_linen():
    """duvet and two pillows on the mattress (separate part so it can get its own colour)"""
    L, W = 2000.0, 1600.0
    duvet = box(650, -W / 2 + 5, 520, L + 50, W / 2 - 5, 580) + box(L + 20, -W / 2 + 5, 330, L + 50, W / 2 - 5, 580)
    pillows = sum((rbox(500, 700, 120, 60, 520).translate([360, y, 0]) for y in (-390, 390)), M())
    return duvet + pillows

def nightstand():
    return rbox(450, 400, 500, 15) - box(-200, -150, 280, 200, 210, 460)

def bedside_lamp():
    """table lamp: base, stem, shade (the bulb is a separate part)"""
    base = cyl(140, 20)
    stem = cyl(16, 260, 20)
    shade = cyl(280, 220, 220, d2=200) - cyl(270, 222, 219, d2=190)
    socket = cyl(40, 50, 260)
    return base + stem + shade + socket

def rug():
    return rbox(2400, 1700, 10, 20)

def tv_bench():
    return box(-800, -200, 0, 800, 200, 450) - box(-780, -150, 60, -10, 210, 390) - box(10, -150, 60, 780, 210, 390)

def tv():
    screen = box(-620, -25, 600, 620, 25, 1320)
    stand = box(-150, -100, 450, 150, 100, 470) + box(-25, -15, 470, 25, 15, 620)
    return screen + stand

def ha_hub():
    """small home-server box stand-in (Home Assistant Green / used mini PC)"""
    return rbox(112, 112, 32, 10)

def thread_radio():
    """USB Thread radio stand-in (Home Assistant Connect ZBT-2) on a short extension cable"""
    stick = rbox(28, 90, 14, 5, 0)
    cable = box(-3, -260, 0, 3, -45, 5)
    return stick + cable

def bookshelf():
    w, d, h = 800.0, 300.0, 1800.0
    s = box(-w / 2, -d / 2, 0, w / 2, d / 2, h)
    for i in range(5):
        z0 = 40 + i * 350
        s -= box(-w / 2 + 18, -d / 2 + 10, z0, w / 2 - 18, d / 2 + 1, z0 + 330)
    return s

def plant():
    pot = cyl(220, 280, d2=260) - cyl(200, 280, 20, d2=240)
    soil = cyl(232, 10, 240)
    stem = cyl(20, 500, 250)
    leaves = M.sphere(220).scale([1, 1, 1.3]).translate([0, 0, 900])
    return pot + soil + stem + leaves

# ------------------------------------------------------------------ Room Panel from its own repo
def load_stl(path):
    return trimesh.load(path, force="mesh")

def room_panel_assembly():
    """Room Panel case, as printed: front face on z=0 facing -z. Turned so the front faces +z and
    the back sits on z=0 (against the wall), centred on x/y."""
    d = DEVICES / "room-panel"
    W, H, D = 145.0, 70.0, 24.0
    flip = chain(move(0, 0, D), rot([0, 1, 0], 180), move(-W, 0, 0))   # front -> +z, mirror-free
    centre = move(-W / 2, -H / 2, 0)
    T = chain(centre, flip)
    parts = {"room_panel_front_shell": load_stl(d / "front_shell.stl"),
             "room_panel_back_plate": load_stl(d / "back_plate.stl")}
    # button caps and knob: front-view coordinates from room_panel_case.py (PCB at 8,8)
    for i, (bx, by) in enumerate([(26.3, 14.9), (26.3, 26.2), (26.3, 38.3), (26.3, 50.0)]):
        c = load_stl(d / "button_cap.stl")
        c.apply_transform(move(W - (8 + bx), H - (8 + by), -1.0))
        parts[f"room_panel_button_{i + 1}"] = c
    # e-paper module stand-in behind the display window (Waveshare 2.9" outline from room_panel_case.py)
    disp_x0, disp_y0 = 8 + 37 + 4, (H - 38.0) / 2
    epd = to_trimesh(box(W - (disp_x0 + 89.5), H - (disp_y0 + 38.0), 2.05, W - disp_x0, H - disp_y0, 3.2))
    parts["room_panel_epaper"] = epd
    k = load_stl(d / "knob.stl")
    k.apply_transform(chain(move(W - (8 + 26.3), H - (8 + 3.2), 0), rot([1, 0, 0], 180)))
    parts["room_panel_knob"] = k
    for g in parts.values():
        g.apply_transform(T)
    return parts

# ------------------------------------------------------------------ COLOURS (RGBA 0-255)
COL = {
    "floor": (196, 160, 120, 255), "wall": (238, 236, 230, 255), "frame": (250, 250, 250, 255),
    "glass": (170, 205, 230, 90), "metal": (180, 182, 186, 255), "radiator": (245, 245, 245, 255),
    "trv": (232, 232, 228, 255), "fabric": (215, 205, 185, 255), "lamp": (40, 44, 48, 255),
    "bulb": (255, 236, 180, 255), "vacuum": (35, 37, 40, 255), "dock": (60, 62, 66, 255),
    "wood": (160, 120, 80, 255), "rug": (180, 175, 160, 255),
    "tv": (20, 20, 22, 255), "hub": (235, 235, 235, 255), "radio": (245, 245, 245, 255),
    "panel": (225, 225, 220, 255), "panel_back": (150, 150, 150, 255),
    "door": (245, 245, 240, 255), "plant": (70, 130, 80, 255), "pot": (190, 110, 80, 255),
    "linen": (232, 228, 218, 255), "white": (250, 250, 250, 255), "epaper": (205, 207, 198, 255),
}

# ------------------------------------------------------------------ ROOM LAYOUT
# name: (builder, colour, placement matrix in room coordinates, group, description)
def layout():
    wx = WINDOW_X
    north_inside = on_north_wall
    L = {}
    def add(name, geom, col, T, group, desc):
        L[name] = (geom, col, T, group, desc)

    # structure
    add("floor", floor(), "floor", np.eye(4), "structure", "Floor slab, wood colour")
    add("wall_north", wall_north(), "wall", frame([-WALL_T, ROOM_D, 0], [0, -1, 0]),
        "structure", "North wall with window opening")
    add("wall_south", wall_south(), "wall", frame([ROOM_W + WALL_T, 0, 0], [0, 1, 0]),
        "structure", "South wall with door opening")
    add("wall_west", wall_plain_ew(), "wall", frame([0, 0, 0], [1, 0, 0]), "structure", "West wall")
    add("wall_east", wall_plain_ew(), "wall", frame([ROOM_W, ROOM_D, 0], [-1, 0, 0]), "structure", "East wall")
    add("door", door(), "door", frame([DOOR_X + DOOR_W / 2 - 5, -20, 0], [0, 1, 0]),
        "structure", "Door leaf with handle")

    # window
    add("window_frame", window_frame(), "frame", north_inside(wx, SILL_Z) @ move(0, 0, -15),
        "window", "Window frame and inside window board")
    add("window_sash", window_sash(), "frame", north_inside(wx, SILL_Z + 45) @ move(0, 0, -20),
        "window", "Opening sash (inward-opening, tilt/turn)")
    add("window_glass", window_glass(), "glass", north_inside(wx, SILL_Z + 90) @ move(0, 0, -20),
        "window", "Double glazing")
    add("window_handle", window_handle(), "white", north_inside(wx + WINDOW_W / 2 - 110, SILL_Z + 600) @ move(0, 0, -20),
        "window", "Window handle")

    # blinds (curtains)
    top = SILL_Z + WINDOW_H + 120
    drop = 650.0
    add("blind_headrail", blind_headrail(), "frame", north_inside(wx, top), "blinds",
        "Cellular blind headrail (IKEA HOPPVALS) with the motor housing on the right")
    add("blind_fabric", blind_fabric(drop), "fabric", north_inside(wx, top),
        "blinds", f"Cellular (honeycomb) blind fabric, shown {drop:.0f} mm down")
    add("blind_bottom_rail", blind_bottom_rail(), "frame", north_inside(wx, top - 45 - drop), "blinds",
        "Bottom rail of the blind")

    # heating
    rad_T = north_inside(wx, RADIATOR_Z) @ move(0, 0, 40)
    add("radiator", radiator(), "radiator", rad_T, "heating", "Type-22 panel radiator, 1000 x 600 mm")
    valve_T = rad_T @ move(RADIATOR_W / 2, 80, 60)
    add("radiator_valve", radiator_valve(), "metal", valve_T, "heating", "Valve body with M30 x 1.5 thread")
    add("trv", trv(), "trv", valve_T @ move(72, 0, 0), "heating",
        "Smart radiator thermostat stand-in (IKEA LILJEBAGGE, Matter over Thread)")

    # lights
    add("pendant_lamp", pendant_lamp(), "lamp", move(ROOM_W / 2, ROOM_D / 2, ROOM_H), "lights", "Ceiling pendant")
    add("bulb_pendant", bulb(), "bulb", chain(move(ROOM_W / 2, ROOM_D / 2, ROOM_H - 600), rot([1, 0, 0], 180)),
        "lights", "Smart bulb stand-in (IKEA KAJPLATS E27, Matter over Thread), ceiling")
    ns = 2850.0                                   # nightstand with the bedside lamp (north side of the bed)
    add("bedside_lamp", bedside_lamp(), "lamp", move(225, ns, 500), "lights", "Bedside table lamp")
    add("bulb_bedside", bulb(), "bulb", move(225, ns, 780), "lights", "Second smart bulb (bedside)")

    # vacuum
    add("vacuum_dock", vacuum_dock(), "dock", move(3700, 0, 0), "vacuum", "Self-empty dock against the south wall")
    add("robot_vacuum", robot_vacuum(), "vacuum", chain(move(3150, 1150, 0), rot([0, 0, 1], 35)), "vacuum",
        "Robot vacuum stand-in (Roborock with the core integration)")

    # furniture
    add("rug", rug(), "rug", move(1700, 1800, 0), "furniture", "Rug under the foot of the bed")
    add("bed", bed(), "wood", move(0, 1800, 0), "furniture", "Double bed 160 x 200 cm, headboard on the west wall")
    add("bed_linen", bed_linen(), "linen", move(0, 1800, 0), "furniture", "Duvet and pillows")
    add("nightstand_south", nightstand(), "wood", move(225, 750, 0), "furniture", "Nightstand")
    add("nightstand_north", nightstand(), "wood", move(225, 2850, 0), "furniture", "Nightstand with the bedside lamp")
    add("tv_bench", tv_bench(), "wood", chain(move(ROOM_W - 200, 1800, 0), rot([0, 0, 1], 90)), "furniture", "TV bench")
    add("tv", tv(), "tv", chain(move(ROOM_W - 200, 1800, 0), rot([0, 0, 1], 90)), "furniture", "TV")
    add("bookshelf", bookshelf(), "wood", chain(move(ROOM_W - 150, 3050, 0), rot([0, 0, 1], 90)), "furniture", "Bookshelf")
    add("plant", plant(), "plant", move(ROOM_W / 2 - 900, ROOM_D - 300, 0), "furniture", "Plant by the window")

    # hub
    add("ha_hub", ha_hub(), "hub", move(ROOM_W - 330, 2520, 450), "hub", "Home Assistant Green / mini PC")
    add("thread_radio", thread_radio(), "radio", move(ROOM_W - 120, 2520, 450), "hub",
        "Home Assistant Connect ZBT-2 (Thread) on a USB extension")

    # the Room Panel (real case STLs)
    panel_x = DOOR_X + DOOR_W / 2 + 200
    for name, g in room_panel_assembly().items():
        col = "panel_back" if "back" in name else "epaper" if "epaper" in name else "panel"
        L[name] = (g, col, on_south_wall(panel_x, PANEL_Z), "devices",
                   "Room Panel (github.com/gustavwrisberg/room-panel), next to the door: radar, climate, light, CO2, controls")
    return L

# parts fixed to a wall: the viewer hides them together with that wall
def wall_of(name):
    if name == "door" or name.startswith("room_panel"):
        return "south"
    if name.startswith(("window_", "blind_", "radiator", "trv")):
        return "north"
    return None

# ------------------------------------------------------------------ EXPORT
def main():
    PARTS.mkdir(exist_ok=True)
    scene = trimesh.Scene()
    info = {"units": "mm", "up": "z", "room": {"width_x": ROOM_W, "depth_y": ROOM_D, "height_z": ROOM_H},
            "parts": []}
    for name, (geom, col, T, group, desc) in layout().items():
        tm = geom if isinstance(geom, trimesh.Trimesh) else to_trimesh(geom)
        rgba = COL[col]
        tm.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            name=col, baseColorFactor=rgba, metallicFactor=0.0, roughnessFactor=0.8,
            alphaMode="BLEND" if rgba[3] < 255 else "OPAQUE", doubleSided=True))
        device = group == "devices"
        if not device:                               # device STLs already live in devices/
            tm.export(PARTS / f"{name}.stl")
            trimesh.Scene({name: tm}).export(PARTS / f"{name}.glb")
        # room scene: metres, glTF Y-up
        to_gltf = chain(rot([1, 0, 0], -90), np.diag([0.001, 0.001, 0.001, 1.0]))
        scene.add_geometry(tm, node_name=name, geom_name=name, transform=to_gltf @ T)
        ext = tm.extents
        info["parts"].append({
            "name": name, "group": group, "description": desc, "wall": wall_of(name),
            "file": "devices/ (from your device repo)" if device else f"parts/{name}.stl",
            "size_mm": [round(float(e), 1) for e in ext],
            "transform_mm": np.round(T, 4).tolist(),
        })
        print(f"{group:10s} {name:28s} {ext[0]:7.0f} x {ext[1]:7.0f} x {ext[2]:7.0f} mm")
    scene.export(HERE / "room.glb")
    (HERE / "room_layout.json").write_text(json.dumps(info, indent=1))
    print(f"\n{len(info['parts'])} parts -> parts/, room.glb, room_layout.json")

if __name__ == "__main__":
    main()
