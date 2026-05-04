"""Scene01 --- 乡村场景自动生成。用法见 CLAUDE.md。"""
import bpy, os, math, random

random.seed(42)
bpy.ops.object.select_all(action='SELECT')        # 清空默认场景
bpy.ops.object.delete(use_global=False)

# ---------- 辅助函数 ----------
def make_mat(name, color, roughness=0.7):
    """创建材质。Blender 5.x: use_nodes 已废弃（默认 True）。
       通过 node.type 查找以兼容中/英文界面。"""
    m = bpy.data.materials.new(name)
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    return m

def add_cube(name, loc, scale, mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, scale=scale)
    obj = bpy.context.active_object; obj.name = name
    if mat: obj.data.materials.append(mat)
    return obj

# ---------- 材质 ----------
gnd = make_mat("Ground",   (0.35,0.25,0.15,1.0))
road = make_mat("Road",    (0.25,0.22,0.20,1.0))
trk = make_mat("Trunk",    (0.30,0.18,0.08,1.0))
leaf = make_mat("Foliage", (0.15,0.45,0.10,1.0), 0.5)
palette = [(0.92,0.82,0.65,1),(0.85,0.55,0.35,1),(0.78,0.65,0.50,1),(0.90,0.70,0.55,1),
           (0.82,0.75,0.60,1),(0.75,0.50,0.40,1),(0.88,0.78,0.62,1),(0.80,0.60,0.45,1)]
bmats = [make_mat(f"Bldg_{i}", c) for i,c in enumerate(palette)]

# ---------- 地面 + 道路 ----------
add_cube("Ground", (0,0,-0.05), (12,12,0.1), gnd)
add_cube("Road",   (0,-4,0.02),  (1.5,8,0.05), road)

# ---------- 建筑（沿道路两侧，8 栋） ----------
for x,y,h,rz,mi in [(-4,3,1.8,0.02,0),(-2.5,4.5,1.2,-0.03,1),
                     (-3.5,6,2.2,0.01,2),(-2,7.5,1.5,-0.02,3),
                     (3,2.5,2.0,-0.01,4),(4.5,4,1.6,0.03,5),
                     (3.5,6.5,2.5,-0.02,6),(5,8,1.3,0.01,7)]:
    b = add_cube(f"Bldg_{mi}", (x,y,h/2), (1,1,h), bmats[mi])
    b.rotation_euler.z = rz

# ---------- 树木（圆柱树干 + 圆锥树冠，8 棵） ----------
for tx,ty in [(-5.5,1),(-6,4),(-5,7),(6,1.5),(6.5,5),(7,7.5),(-1,-4.5),(1.5,-5)]:
    th = random.uniform(0.4,0.8); cr = random.uniform(0.3,0.45); ch = random.uniform(0.6,1.0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07, depth=th, location=(tx,ty,th/2))
    bpy.context.active_object.data.materials.append(trk)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=cr, radius2=0, depth=ch, location=(tx,ty,th+ch*0.35))
    bpy.context.active_object.data.materials.append(leaf)

# ---------- 日光 + 天空 ----------
sun = bpy.data.lights.new(name="Sun", type='SUN'); sun.energy = 4.0
s_obj = bpy.data.objects.new("Sun", sun)
bpy.context.collection.objects.link(s_obj)
s_obj.rotation_euler = (math.radians(45), math.radians(-30), math.radians(20))
bg = next(n for n in bpy.context.scene.world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.5, 0.7, 1.0, 1.0)

# ---------- 相机 ----------
bpy.ops.object.camera_add(location=(10, -6, 8))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(60), 0, math.radians(55))
bpy.context.scene.camera = cam

# ---------- 渲染 + 输出 ----------
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(proj, "blender", "scene01.blend"))
bpy.context.scene.render.filepath = os.path.join(proj, "blender", "scene01_preview.png")
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print("完成: blender/scene01.blend + blender/scene01_preview.png")
