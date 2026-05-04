"""
Blender Python 脚本模板
用法: "D:/blender-5.1.0-windows-x64/blender.exe" --python scripts/blender_template.py
"""

import bpy
import os

# ============================================================
# 脚本内容（在这里写代码）
# ============================================================


# ============================================================
# 保存 + 渲染预览（脚本末尾保留）
# ============================================================
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.save_as_mainfile(
    filepath=os.path.join(project_dir, "blender", "output.blend")
)
bpy.context.scene.render.filepath = os.path.join(project_dir, "blender", "preview.png")
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print("渲染完成: blender/preview.png")
