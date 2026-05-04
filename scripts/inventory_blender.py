"""清点 Blender 5.1 全部插件、扩展和能力"""
import bpy

print("=" * 60)
print("Blender 版本:", bpy.app.version_string)
print("Python 版本:", bpy.app.version)

# ---------- 所有插件（内置 + 用户安装） ----------
print("\n" + "=" * 60)
print("【已启用插件】")
for mod in sorted(bpy.context.preferences.addons.keys()):
    addon = bpy.context.preferences.addons[mod]
    name = getattr(addon.module, 'bl_info', {}).get('name', mod)
    ver = getattr(addon.module, 'bl_info', {}).get('version', '?')
    desc = getattr(addon.module, 'bl_info', {}).get('description', '')
    category = getattr(addon.module, 'bl_info', {}).get('category', '')
    print(f"  {mod}")
    try:
        if isinstance(ver, (tuple, list)) and len(ver) >= 3:
            vstr = f"v{ver[0]}.{ver[1]}.{ver[2]}"
        else:
            vstr = str(ver)
    except:
        vstr = str(ver)
    print(f"    名称: {name}  {vstr}")
    print(f"    分类: {category}")
    print(f"    说明: {desc}")

print("\n" + "=" * 60)
print("【已安装但未启用的插件】")
import addon_utils
for mod in sorted(addon_utils.modules()):
    loaded_default = addon_utils.check(mod.__name__)[1]
    if not loaded_default:
        bl_info = getattr(mod, 'bl_info', {})
        if bl_info:
            name = bl_info.get('name', mod.__name__)
            cat = bl_info.get('category', '')
            desc = bl_info.get('description', '')
            print(f"  {mod.__name__}")
            print(f"    名称: {name}")
            print(f"    分类: {cat}")
            print(f"    说明: {desc}")

# ---------- 扩展（Blender 4.2+ 新系统） ----------
print("\n" + "=" * 60)
print("【扩展 (Extensions)】")
try:
    from bl_extension import bl_extension_ops, bl_extension_utils
    repo = bl_extension_utils.get_repo('blender_org')
    if repo:
        for pkg in repo.get('packages', []):
            print(f"  {pkg.get('id', '?')} - {pkg.get('name', '?')}")
            print(f"    版本: {pkg.get('version', '?')}")
except Exception as e:
    print(f"  扩展扫描失败: {e}")

# ---------- 渲染引擎 ----------
print("\n" + "=" * 60)
print("【渲染引擎】")
for engine in bpy.types.RenderEngine.__subclasses__():
    eng_id = getattr(engine, 'bl_idname', '?')
    eng_label = getattr(engine, 'bl_label', '?')
    print(f"  {eng_id} - {eng_label}")

# ---------- MCP 相关 ----------
print("\n" + "=" * 60)
print("【BlenderMCP 状态】")
if 'blender_mcp' in bpy.context.preferences.addons:
    print("  BlenderMCP: ✔ 已启用")
else:
    print("  BlenderMCP: ✘ 未找到")

# ---------- 可用的关键 API 模块 ----------
print("\n" + "=" * 60)
print("【关键 bpy 模块】")
key_modules = ['bpy.ops.mesh', 'bpy.ops.object', 'bpy.ops.wm',
               'bpy.data', 'bpy.context', 'bpy.types', 'bpy.utils',
               'bpy.path', 'bpy.app', 'mathutils', 'bmesh']
for m in key_modules:
    try:
        mod = __import__(m)
        print(f"  {m}: ✔")
    except:
        print(f"  {m}: ✘")

# ---------- 物体类型 ----------
print("\n" + "=" * 60)
print("【可用物体类型】")
for obj_type in dir(bpy.types):
    if obj_type.startswith('_'):
        continue
    try:
        cls = getattr(bpy.types, obj_type)
        if hasattr(cls, 'bl_rna') and hasattr(cls, 'bl_rna') and 'Object' in str(getattr(cls, '__bases__', '')):
            pass
    except:
        pass

# 直接列常见类型
obj_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'CURVES',
             'POINTCLOUD', 'VOLUME', 'GPENCIL', 'ARMATURE', 'LATTICE',
             'EMPTY', 'LIGHT', 'LIGHT_PROBE', 'CAMERA', 'SPEAKER']
print("  ", ", ".join(obj_types))

# ---------- 修改器 ----------
print("\n" + "=" * 60)
print("【修改器类型】")
mod_count = 0
for attr in dir(bpy.types):
    if attr.endswith('Modifier') and hasattr(getattr(bpy.types, attr), 'bl_rna'):
        mod_count += 1
print(f"  共 {mod_count} 种修改器")

# 列举常用
common_mods = ['SubdivisionModifier', 'BevelModifier', 'SolidifyModifier',
               'ArrayModifier', 'BooleanModifier', 'MirrorModifier',
               'DecimateModifier', 'RemeshModifier', 'SkinModifier',
               'DisplaceModifier', 'WaveModifier', 'CastModifier',
               'SimpleDeformModifier', 'ShrinkwrapModifier',
               'ParticleSystemModifier', 'OceanModifier',
               'GeometryNodesModifier', 'NodesModifier']
for m in common_mods:
    exists = hasattr(bpy.types, m)
    print(f"  {m}: {'✔' if exists else '✘'}")

print("\n" + "=" * 60)
print("清点完成")
