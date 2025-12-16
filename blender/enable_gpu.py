import bpy

bpy.ops.preferences.addon_enable(module='microscopynodes')
bpy.ops.preferences.addon_enable(module='cycles')

prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'CUDA'
prefs.get_devices()
for d in prefs.devices:
    if d.type != 'CPU':
        d.use = True

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'

bpy.ops.wm.save_userpref()
