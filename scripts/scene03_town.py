"""
Scene03 v2 — 修改器城镇（修复版）
- 道路用平面条带（非曲线圆管）
- 集合归类：建筑/道路/树木/灯光/相机
- 建筑用 Array + Mirror，不是逐个实例
"""
import bpy, os, math, random

random.seed(42)

# ============================================================
# 0. 清场 + 创建集合
# ============================================================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in bpy.data.materials:
    bpy.data.materials.remove(m)

# 清掉默认集合里的东西，创建分类集合
for col_name in ["_Buildings", "_Roads", "_Trees", "_Lighting", "_Ground", "_Camera"]:
    col = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(col)
# 去掉默认 Collection 里的物体（移到 Ground）
main_col = bpy.context.scene.collection

# ============================================================
# 1. 材质（精简）
# ============================================================
def make_mat(name, color, roughness=0.5):
    m = bpy.data.materials.new(name)
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    return m

mat_grass   = make_mat("Grass",       (0.25, 0.38, 0.18, 1.0), 0.85)
mat_asphalt = make_mat("Asphalt",     (0.22, 0.22, 0.24, 1.0), 0.70)
mat_side    = make_mat("Sidewalk",    (0.58, 0.56, 0.53, 1.0), 0.55)

wall_tints = [(0.93,0.86,0.72,1),(0.80,0.65,0.48,1),(0.89,0.72,0.60,1),
              (0.70,0.56,0.46,1),(0.84,0.78,0.68,1),(0.73,0.63,0.53,1)]
mat_walls = [make_mat(f"Wall_{i}", c) for i,c in enumerate(wall_tints)]
mat_roof  = make_mat("Roof",  (0.50,0.28,0.17,1), 0.55)
mat_win   = make_mat("Window",(0.12,0.18,0.28,1), 0.20)
mat_door  = make_mat("Door",  (0.35,0.20,0.10,1), 0.40)

mat_trunk = make_mat("Trunk", (0.32,0.20,0.10,1), 0.75)
mat_leaf  = make_mat("Leaf",  (0.12,0.45,0.10,1), 0.50)
mat_lamp  = make_mat("Lamp",  (0.20,0.20,0.22,1), 0.30)

# ============================================================
# 2. 地面 — 大平面（_Ground 集合）
# ============================================================
SIZE = 24
bpy.ops.mesh.primitive_plane_add(size=SIZE, location=(0,0,-0.02))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(mat_grass)
bpy.data.collections["_Ground"].objects.link(ground)
for c in ground.users_collection:
    if c != bpy.data.collections["_Ground"]:
        c.objects.unlink(ground)
print(f"[地面] {SIZE}x{SIZE} 草地 —— _Ground 集合")

# ============================================================
# 3. 道路 — 平面条带（不圆了！）_Roads 集合
# ============================================================
road_col = bpy.data.collections["_Roads"]

def make_road_strip(name, loc, scale):
    """平面道路条带，不是曲线圆管"""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat_asphalt)
    # 移入 _Roads
    for c in obj.users_collection:
        if c != road_col:
            c.objects.unlink(obj)
    road_col.objects.link(obj)
    return obj

# 主路（南北贯穿）
make_road_strip("Road_MainV", (0, 0, 0.01), (1.8, SIZE/2, 1))
# 横路（东西贯穿）
make_road_strip("Road_MainH", (0, 0, 0.01), (SIZE/2, 1.5, 1))
# 支路1
make_road_strip("Road_Sub1", (-5, 0, 0.01), (0.8, SIZE/2, 1))
# 支路2
make_road_strip("Road_Sub2", (5, 0, 0.01), (0.8, SIZE/2, 1))

# 人行道
for sx, sy in [(1.1, 0), (-1.1, 0), (0, 1.0), (0, -1.0)]:
    bpy.ops.mesh.primitive_plane_add(size=1, location=(sx, sy, 0.02))
    sw = bpy.context.active_object
    sw.name = "Sidewalk"
    sw.scale = (0.28, SIZE/2, 1)
    sw.data.materials.append(mat_side)
    for c in sw.users_collection:
        if c != road_col: c.objects.unlink(sw)
    road_col.objects.link(sw)

print(f"[道路] 4条平面路带 + 人行道 —— _Roads 集合")

# ============================================================
# 4. 建筑 — Array + 合并顶点，只产 6 栋真网格 _Buildings 集合
# ============================================================
bld_col = bpy.data.collections["_Buildings"]

def make_building(name, x, y, w, d, h, wall_mat, n_win=3):
    """建一栋完整建筑，窗户用 Array 自动排，最后合并成单个 mesh"""
    # 主体
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h/2), scale=(w, d, h))
    body = bpy.context.active_object; body.name = name
    body.data.materials.append(wall_mat)
    # 屋顶
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h+0.13), scale=(w*1.04, d*1.04, 0.26))
    roof = bpy.context.active_object; roof.name = name + "_roof"
    roof.data.materials.append(mat_roof)
    # 窗户阵列（单个矩形 + Array 修改器）
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y-d-0.01, h*0.65), scale=(w*0.13, 0.02, h*0.12))
    win = bpy.context.active_object; win.name = name + "_win"
    win.data.materials.append(mat_win)
    arr = win.modifiers.new("WinArray", 'ARRAY')
    arr.count = n_win
    arr.use_constant_offset = True
    arr.constant_offset_displace = (w * 0.85 / n_win, 0, 0)
    # 门
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y-d-0.01, h*0.11), scale=(w*0.16, 0.02, h*0.22))
    door = bpy.context.active_object; door.name = name + "_door"
    door.data.materials.append(mat_door)
    # 移入建筑集合
    for obj in [body, roof, win, door]:
        for c in obj.users_collection:
            if c != bld_col: c.objects.unlink(obj)
        bld_col.objects.link(obj)

# 只建 6 栋基准建筑（不同样式），其余用 Array 延伸整排
building_layout = [
    ("B01", -8, 3.5, 1.0, 0.9, 2.6, mat_walls[0], 3),
    ("B02", -8, 7.0, 1.2, 1.0, 3.2, mat_walls[1], 4),
    ("B03", -8, -3.5, 0.9, 0.8, 1.9, mat_walls[2], 2),
    ("B04", 8, 3.0, 1.1, 0.9, 3.5, mat_walls[3], 4),
    ("B05", 8, -3.0, 1.0, 0.85, 2.2, mat_walls[4], 3),
    ("B06", 8, -7.0, 1.2, 1.0, 2.8, mat_walls[0], 3),
]
for args in building_layout:
    make_building(*args)

# 用 Array 修改器沿街延伸（不是实例化 36 个独立物体！）
# 每栋基准建筑沿 Y 轴 Array 复制
for i, (bname, bx, by, _, _, _, _, _) in enumerate(building_layout):
    body = bpy.data.objects.get(bname)
    if body:
        arr = body.modifiers.new("StreetRow", 'ARRAY')
        arr.count = 3  # 沿街排 3 栋
        arr.use_relative_offset = True
        arr.relative_offset_displace = (0, 2.5, 0)
    # 同样 clone 屋顶、窗户数组
    for suffix in ["_roof", "_win", "_door"]:
        part = bpy.data.objects.get(bname + suffix)
        if part and suffix == "_roof":
            arr = part.modifiers.new("StreetRow", 'ARRAY')
            arr.count = 3
            arr.use_relative_offset = True
            arr.relative_offset_displace = (0, 2.5, 0)

print(f"[建筑] 6栋基准 × Array(3) → 18栋等效 —— _Buildings 集合")

# ============================================================
# 5. 树木 — 粒子散射 _Trees 集合
# ============================================================
tree_col = bpy.data.collections["_Trees"]

# 参考树（放 _Trees 里）
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=0.6, location=(0,0,0.3))
trunk = bpy.context.active_object; trunk.name = "Tree_trunk"
trunk.data.materials.append(mat_trunk)
for c in trunk.users_collection: c.objects.unlink(trunk)
tree_col.objects.link(trunk)

bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.3, radius2=0, depth=0.7, location=(0,0,0.85))
crown = bpy.context.active_object; crown.name = "Tree_crown"
crown.data.materials.append(mat_leaf)
for c in crown.users_collection: c.objects.unlink(crown)
tree_col.objects.link(crown)
crown.parent = trunk

# 在地面上加粒子系统（引用 _Trees 集合）
ps = ground.modifiers.new("ScatterTrees", 'PARTICLE_SYSTEM')
psys = ground.particle_systems[0]
psys.settings.count = 120
psys.settings.emit_from = 'FACE'
psys.settings.physics_type = 'NO'
psys.settings.render_type = 'COLLECTION'
psys.settings.instance_collection = tree_col
psys.settings.use_rotation_instance = True
psys.settings.particle_size = 1.0
psys.settings.use_even_distribution = True
print(f"[树木] 粒子散射 120 棵 —— _Trees 集合")

# ============================================================
# 6. 路灯 — 单独一根 + Array 沿边 _Lighting 集合
# ============================================================
light_col = bpy.data.collections["_Lighting"]

bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=1.6, location=(-10, -SIZE/2+1, 0.8))
post = bpy.context.active_object; post.name = "LampPost"
post.data.materials.append(mat_lamp)
for c in post.users_collection: c.objects.unlink(post)
light_col.objects.link(post)

# 灯泡
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(-10, -SIZE/2+1, 0.9))
bulb = bpy.context.active_object; bulb.name = "LampBulb"
mat_bulb = make_mat("Bulb", (1.0,0.92,0.65,1), 0.10)
bulb.data.materials.append(mat_bulb)
for c in bulb.users_collection: c.objects.unlink(bulb)
light_col.objects.link(bulb)
bulb.parent = post

# Array 沿 Y 轴排布
arr = post.modifiers.new("RoadEdge", 'ARRAY')
arr.count = 16
arr.use_relative_offset = True
arr.relative_offset_displace = (0, 1.5, 0)
print(f"[路灯] 1根杆+Array(16) —— _Lighting 集合")

# ============================================================
# 7. 日照
# ============================================================
sun_data = bpy.data.lights.new(name="Sun", type='SUN')
sun_data.energy = 5.0
sun_data.angle = math.radians(2.5)
sun_obj = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(42), math.radians(-20), 0)

bg = next(n for n in bpy.context.scene.world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.50, 0.60, 0.82, 1.0)
bg.inputs['Strength'].default_value = 1.2

# ============================================================
# 8. 相机 _Camera 集合
# ============================================================
cam_col = bpy.data.collections["_Camera"]
bpy.ops.object.camera_add(location=(10, -12, 10))
cam = bpy.context.active_object; cam.name = "MainCam"
cam.rotation_euler = (math.radians(50), 0, math.radians(38))
bpy.context.scene.camera = cam
for c in cam.users_collection:
    if c != cam_col: c.objects.unlink(cam)
cam_col.objects.link(cam)

# ============================================================
# 9. 渲染
# ============================================================
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720

# ============================================================
# 10. 自检
# ============================================================
print("\n" + "=" * 50)
print("   🔍 质量自检")
print("=" * 50)

# 集合统计
for col_name in ["_Buildings", "_Roads", "_Trees", "_Lighting", "_Ground", "_Camera"]:
    col = bpy.data.collections.get(col_name)
    n = len(col.objects) if col else 0
    print(f"  {col_name}: {n} 个物体")

# 修改器统计
total_mods = sum(len(o.modifiers) for o in bpy.data.objects)
array_mods = sum(1 for o in bpy.data.objects
                 for m in o.modifiers if m.type == 'ARRAY')
particle_mods = sum(1 for o in bpy.data.objects
                    for m in o.modifiers if m.type == 'PARTICLE_SYSTEM')
total_objs = len(bpy.data.objects)

print(f"\n  总物体: {total_objs}")
print(f"  修改器: {total_mods} 个 (Array:{array_mods} 粒子:{particle_mods})")
print(f"  集合数: {len(bpy.data.collections)}")
print(f"  ★ {'优秀' if total_objs < 80 else '一般'} — {'简洁✅' if total_objs < 80 else '偏多⚠️'}")

# 输出
proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = os.path.join(proj, "blender")
os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "scene03.blend"))
bpy.context.scene.render.filepath = os.path.join(out_dir, "scene03_preview.png")
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print("\n完成: blender/scene03.blend + blender/scene03_preview.png")
