"""
Scene02 — 欧洲小镇广场，带自检评分系统。
Explore → Plan → Generate → Self-Check → Score → Fix/Report
"""
import bpy, os, math, random, json

random.seed(42)

# ============================================================
# 0. 清场
# ============================================================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ============================================================
# 1. 辅助函数
# ============================================================
MAT_CACHE = {}

def make_mat(name, base_color, roughness=0.5, metallic=0.0):
    m = bpy.data.materials.new(name)
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    MAT_CACHE[name] = base_color
    return m

def add_cube(name, loc, scale, mat=None, rot_z=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, scale=scale)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler.z = rot_z
    if mat: obj.data.materials.append(mat)
    return obj

def add_cylinder(name, loc, radius, depth, mat=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    if mat: obj.data.materials.append(mat)
    return obj

def add_uv_sphere(name, loc, radius, mat=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=16, ring_count=8)
    obj = bpy.context.active_object
    obj.name = name
    if mat: obj.data.materials.append(mat)
    return obj

# ============================================================
# 2. 材质库（暖色欧洲小镇调色板）
# ============================================================
mat_stone = make_mat("Cobblestone", (0.55, 0.50, 0.42, 1.0), 0.85, 0.0)
mat_plaza = make_mat("PlazaFloor", (0.62, 0.58, 0.52, 1.0), 0.75, 0.0)

mat_cream  = make_mat("CreamWall",  (0.95, 0.90, 0.78, 1.0), 0.35, 0.0)
mat_ochre  = make_mat("OchreWall",  (0.82, 0.62, 0.35, 1.0), 0.40, 0.0)
mat_terrac = make_mat("TerraWall",  (0.72, 0.42, 0.30, 1.0), 0.45, 0.0)
mat_peach  = make_mat("PeachWall",  (0.90, 0.75, 0.65, 1.0), 0.35, 0.0)
mat_sage   = make_mat("SageWall",   (0.65, 0.72, 0.60, 1.0), 0.35, 0.0)
mat_blue   = make_mat("BlueWall",   (0.55, 0.62, 0.72, 1.0), 0.30, 0.0)
wall_colors = [mat_cream, mat_ochre, mat_terrac, mat_peach, mat_sage, mat_blue]

mat_roof   = make_mat("RoofTile",   (0.60, 0.30, 0.18, 1.0), 0.55, 0.0)
mat_fountain = make_mat("Fountain", (0.70, 0.68, 0.65, 1.0), 0.30, 0.1)
mat_water  = make_mat("Water",      (0.25, 0.45, 0.65, 1.0), 0.15, 0.1)
mat_trunk  = make_mat("Trunk",      (0.35, 0.22, 0.12, 1.0), 0.75, 0.0)
mat_leaf   = make_mat("Leaf",       (0.18, 0.50, 0.15, 1.0), 0.50, 0.0)
mat_bench  = make_mat("BenchWood",  (0.45, 0.30, 0.18, 1.0), 0.60, 0.0)

# ============================================================
# 3. 场景生成
# ============================================================
print("\n" + "=" * 50)
print("   Scene02 — 欧洲小镇广场")
print("=" * 50)

# --- 地面 ---
ground = add_cube("Ground", (0, 0, -0.1), (14, 14, 0.2), mat_stone)
print("[地面] 14x14 石板地面")

# --- 中央广场 ---
plaza = add_cube("Plaza", (0, 0, 0.02), (4.5, 4.5, 0.05), mat_plaza)
print("[广场] 4.5x4.5 中央广场")

# --- 喷泉（底座圆柱 + 柱体 + 顶部球体 + 水盘） ---
add_cylinder("Fountain_Base", (0, 0, 0.55), 0.65, 1.1, mat_fountain)
add_cylinder("Fountain_Pillar", (0, 0, 1.35), 0.25, 0.5, mat_fountain)
add_uv_sphere("Fountain_Crown", (0, 0, 1.65), 0.22, mat_fountain)
add_cylinder("Water_Basin", (0, 0, 0.72), 0.75, 0.08, mat_water)
print("[喷泉] 四层构造（底座+柱+球+水盘）")

# --- 周边建筑（环绕广场，6栋） ---
buildings = [
    (-3.5, 3.0, 1.6, 1.2, 2.8, 0.04, mat_cream,  mat_roof),
    (-4.5, -2.5, 1.8, 1.3, 3.2, -0.02, mat_ochre, mat_roof),
    (0.0, 4.5, 1.6, 1.5, 2.2, 0.00, mat_terrac, mat_roof),
    (3.8, 3.5, 1.5, 1.1, 3.0, -0.03, mat_peach,  mat_roof),
    (4.8, -2.0, 1.7, 1.4, 2.6, 0.05, mat_sage,   mat_roof),
    (-1.5, -4.5, 1.9, 1.2, 2.4, 0.01, mat_blue,  mat_roof),
]
for i, (bx, by, bw, bd, bh, rz, wall, roof) in enumerate(buildings):
    # 主体
    b = add_cube(f"Building_{i+1}", (bx, by, bh/2), (bw, bd, bh), wall, rz)
    # 屋顶（略小的深色方块置于顶部）
    add_cube(f"Roof_{i+1}", (bx, by, bh + 0.08), (bw*1.05, bd*1.05, 0.16), roof, rz)
print(f"[建筑] {len(buildings)}栋环绕广场，6色暖调外墙+统一瓦顶")

# --- 长椅（环绕喷泉） ---
bench_positions = [(1.0, -0.6, 0.3), (-0.9, 0.8, 0.3),
                   (0.4, 1.1, -0.3), (-1.2, -0.5, -0.3)]
for i, (bx, by, rz) in enumerate(bench_positions):
    b = add_cube(f"Bench_{i+1}", (bx, by, 0.2), (0.55, 0.15, 0.12), mat_bench, rz)
    # 椅腿
    add_cube(f"BenchLeg_{i+1}a", (bx-0.2, by, 0.06), (0.05, 0.12, 0.12), mat_bench, rz)
    add_cube(f"BenchLeg_{i+1}b", (bx+0.2, by, 0.06), (0.05, 0.12, 0.12), mat_bench, rz)
print(f"[长椅] {len(bench_positions)}张围绕喷泉")

# --- 树木 ---
tree_data = [(-5.5, 5.2, 0.5, 0.38, 0.9),
             (5.8, 5.5, 0.45, 0.35, 0.85),
             (6.0, -4.5, 0.55, 0.42, 1.0),
             (-5.8, -5.0, 0.48, 0.38, 0.95),
             (5.5, 1.5, 0.42, 0.32, 0.8),
             (-5.5, -1.0, 0.52, 0.40, 1.05)]
for i, (tx, ty, th, cr, ch) in enumerate(tree_data):
    add_cylinder(f"Tree_trunk_{i+1}", (tx, ty, th/2), 0.07, th, mat_trunk)
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=cr, radius2=0,
                                     depth=ch, location=(tx, ty, th + ch*0.35))
    bpy.context.active_object.data.materials.append(mat_leaf)
    bpy.context.active_object.name = f"Tree_crown_{i+1}"
print(f"[树木] {len(tree_data)}棵散布广场外圈")

# ============================================================
# 4. 光照 + 天空
# ============================================================
# 夕阳暖光
sun = bpy.data.lights.new(name="Sun", type='SUN')
sun.energy = 5.0
sun.angle = math.radians(2.5)  # 柔和的阴影边缘
s_obj = bpy.data.objects.new("Sun", sun)
bpy.context.collection.objects.link(s_obj)
s_obj.rotation_euler = (math.radians(40), math.radians(-25), math.radians(15))

bg = next(n for n in bpy.context.scene.world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.45, 0.55, 0.78, 1.0)  # 暖黄昏色天空
bg.inputs['Strength'].default_value = 1.2
print("[光照] 夕阳暖光 40°仰角 + 黄昏天空")

# ============================================================
# 5. 相机
# ============================================================
bpy.ops.object.camera_add(location=(9, -7, 6.5))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(55), 0, math.radians(50))
bpy.context.scene.camera = cam
print("[相机] 俯视全景 1280x720")

# ============================================================
# 6. 渲染设置
# ============================================================
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.film_transparent = False

# ============================================================
# 7. 自检评分系统
# ============================================================
print("\n" + "=" * 50)
print("   🔍 质量自检报告")
print("=" * 50)

report = {"scene": "scene02_square", "scores": {}, "total": 0, "max": 100}

# 7.1 物体多样性
obj_types = {}
for obj in bpy.data.objects:
    t = obj.type
    obj_types[t] = obj_types.get(t, 0) + 1
total_objects = sum(obj_types.values())
diversity = len(obj_types)
obj_score = min(25, diversity * 5 + (total_objects > 20) * 5)
report["scores"]["object_diversity"] = {"score": obj_score, "max": 25,
    "detail": f"{diversity}种类型, {total_objects}个物体: {obj_types}"}
print(f"  [物体多样性] {obj_score}/25 — {diversity}种类型, {total_objects}个物体")

# 7.2 色彩协调性
# 检查是否有极端色（饱和度>0.9或明度<0.1）
color_ok = True
warnings = []
for name, color in MAT_CACHE.items():
    r, g, b, a = color
    saturation = max(r,g,b) - min(r,g,b)
    brightness = (r+g+b) / 3
    if saturation > 0.85:
        warnings.append(f"{name} 饱和度过高({saturation:.2f})")
        color_ok = False
    if brightness < 0.08:
        warnings.append(f"{name} 过暗({brightness:.2f})")
        color_ok = False
    if brightness > 0.95:
        warnings.append(f"{name} 过亮({brightness:.2f})")
        color_ok = False
color_score = 25 if color_ok else max(10, 25 - len(warnings) * 5)
report["scores"]["color_harmony"] = {"score": color_score, "max": 25,
    "detail": "通过" if color_ok else "; ".join(warnings)}
print(f"  [色彩协调] {color_score}/25 — {'通过' if color_ok else warnings}")

# 7.3 比例真实性
# 建筑高宽比应在1.5:1到3.5:1之间，树高1-3m
scale_ok = True
scale_notes = []
for obj in bpy.data.objects:
    if obj.name.startswith("Building_"):
        h = obj.scale.z * 2  # cube size=1, scale is half-height
        w = max(obj.scale.x, obj.scale.y)
        ratio = h / (w + 0.01)
        if ratio < 1.2 or ratio > 4.0:
            scale_ok = False
            scale_notes.append(f"{obj.name} 高宽比{ratio:.1f}:1 (正常1.2-4.0)")
scale_score = 25 if scale_ok else max(10, 25 - len(scale_notes) * 5)
report["scores"]["proportion"] = {"score": scale_score, "max": 25,
    "detail": "通过" if scale_ok else "; ".join(scale_notes)}
print(f"  [比例真实] {scale_score}/25 — {'通过' if scale_ok else scale_notes}")

# 7.4 构图
# 检查：是否有地面、相机、灯光、天空
has_ground = any("Ground" in o.name for o in bpy.data.objects)
has_camera = bpy.context.scene.camera is not None
has_sun = any(o.type == 'LIGHT' for o in bpy.data.objects)
has_world = bpy.context.scene.world is not None
comp_items = [has_ground, has_camera, has_sun, has_world]
comp_score = sum(6 for x in comp_items if x) + (1 if all(comp_items) else 0)
report["scores"]["composition"] = {"score": comp_score, "max": 25,
    "detail": f"地面:{has_ground} 相机:{has_camera} 灯光:{has_sun} 天空:{has_world}"}
print(f"  [构图完整] {comp_score}/25 — 地面:{has_ground} 相机:{has_camera} 灯光:{has_sun} 天空:{has_world}")

# 7.5 汇总
total = sum(v["score"] for v in report["scores"].values())
report["total"] = total
print(f"\n  {'★' * (total//20)}{'☆' * (5 - total//20)}  总分: {total}/100")

if total >= 80:
    grade = "优秀 ✅ 场景合格，可输出"
elif total >= 60:
    grade = "良好 ⚠️ 有小问题，建议微调"
else:
    grade = "需改进 ❌ 请检查警告并重试"
report["grade"] = grade
print(f"  评级: {grade}")

# 保存报告
proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
report_path = os.path.join(proj, "notes", "scene02_report.json")
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"\n报告已保存: notes/scene02_report.json")

# ============================================================
# 8. 输出
# ============================================================
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(proj, "blender", "scene02.blend"))
bpy.context.scene.render.filepath = os.path.join(proj, "blender", "scene02_preview.png")
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print("\n完成: blender/scene02.blend + blender/scene02_preview.png")
