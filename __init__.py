# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.app import driver_namespace
bl_info = {
    "name": "Viewport Monogamy",
    "author": "Nechiti Octavian",
    "blender": (2,90,0),
    "version": (0,9),
    "description": "Choose different devices for viewport rendering and final rendering", 
    "category": "Render",
    }

class Viewport_Monogamy_Properties(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty(name="ID")
    name: bpy.props.StringProperty(name="Name")
    use: bpy.props.BoolProperty(name="Use", default=False, options={'PROPORTIONAL'})


def get_gpus():
    if bpy.context.preferences.addons['cycles'].preferences['compute_device_type'] == 0:
        return [device for device in bpy.context.preferences.addons['cycles'].preferences.get_devices_for_type('NONE')]
    elif bpy.context.preferences.addons['cycles'].preferences['compute_device_type'] == 1:
        return [device for device in bpy.context.preferences.addons['cycles'].preferences.get_devices_for_type('CUDA')]
    elif bpy.context.preferences.addons['cycles'].preferences['compute_device_type'] == 2:
        return [device for device in bpy.context.preferences.addons['cycles'].preferences.get_devices_for_type('OPENCL')]
    elif bpy.context.preferences.addons['cycles'].preferences['compute_device_type'] == 3:
        return [device for device in bpy.context.preferences.addons['cycles'].preferences.get_devices_for_type('OPTIX')]

viewport_gpus_in_use = []

def viewport_gpus(gpus):
    global viewport_gpus_in_use
    viewport_gpus = []
    for viewport_gpu in gpus:
        if viewport_gpu['use'] == True:
            viewport_gpus.append(viewport_gpu['id'])
    viewport_gpus_in_use = viewport_gpus


pre_render_handler_key = "GPU_PRE_01"
post_render_handler_key = "GPU_POST_01"


def pre_render(self):
    viewport_gpus(get_gpus())
    for device in get_gpus():
        for final_device in bpy.context.scene.viewport_monogamy_devices:
            try:
                final_device['use']
            except KeyError:
                final_device['use'] = None
            if device['id'] == final_device['id'] and final_device['use'] != None:
                device['use'] = True  


def post_render(self):
    for device in get_gpus():
        for viewport_device in viewport_gpus_in_use:
            if device['id'] != viewport_device:
                device['use'] = 0
    

def delete_handler(handler_key):
    if handler_key in driver_namespace:
        if driver_namespace[handler_key] in bpy.app.handlers.render_pre:
            bpy.app.handlers.render_pre.remove(driver_namespace[handler_key])
            del driver_namespace[handler_key]
        elif driver_namespace[handler_key] in bpy.app.handlers.render_post:
            bpy.app.handlers.render_post.remove(driver_namespace[handler_key])
            del driver_namespace[handler_key]


class SCENE_OT_viweport_device(bpy.types.Operator):
    """Set final render devices"""
    bl_idname = "scene.set_viewport_devices"
    bl_label = "Viewport Devices"
    bl_options = {'REGISTER', 'UNDO'}
    

    def execute(self, context):
        delete_handler(pre_render_handler_key)
                    
        bpy.app.handlers.render_pre.append(pre_render)
        driver_namespace[pre_render_handler_key] = pre_render

        delete_handler(post_render_handler_key)

        bpy.app.handlers.render_post.append(post_render)
        driver_namespace[post_render_handler_key] = post_render
        
        return {'FINISHED'}
    

class SCENE_OT_refresh_devices(bpy.types.Operator):
    """Refresh Render Devices"""
    bl_idname = "scene.refresh_devices"
    bl_label = "Refresh Rendering devices"
 

    def execute(self, context):
        bpy.context.scene.viewport_monogamy_devices.clear()
        for device in get_gpus():
            gpu = bpy.context.scene.viewport_monogamy_devices.add()
            gpu.id = device.id
            gpu.name = device.name
       
        return {'FINISHED'}


class SCENE_PT_viewport_devices(bpy.types.Panel):
    COMPAT_ENGINES = {'CYCLES'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_label = "Viewport Monogamy"

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES    

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        box = layout.box()
        col = box.column(heading="Viewport Devices:", align=False)

        for gpu in get_gpus():
            col.prop(gpu, "use", text = gpu.name)
        
        box2 = layout.box()
        col = box2.column(heading="Final Render Devices:", align=False)
        
        for my_gpu in bpy.context.scene.viewport_monogamy_devices:
            col.prop(my_gpu, "use", text = my_gpu.name)

        col.operator('scene.refresh_devices',
            text = 'Refresh Devices')
        col.operator('scene.set_viewport_devices',
            text = "Set Devices")    
        

    

def register():
    bpy.utils.register_class(SCENE_OT_viweport_device)
    bpy.utils.register_class(SCENE_PT_viewport_devices)
    bpy.utils.register_class(SCENE_OT_refresh_devices)
    bpy.utils.register_class(Viewport_Monogamy_Properties)
    bpy.types.Scene.viewport_monogamy_devices = bpy.props.CollectionProperty(type=Viewport_Monogamy_Properties)
    
    
def unregister():
    bpy.utils.unregister_class(SCENE_OT_viweport_device)
    bpy.utils.unregister_class(SCENE_PT_viewport_devices)
    bpy.utils.unregister_class(SCENE_OT_refresh_devices)
    bpy.utils.unregister_class(Viewport_Monogamy_Properties)
    delete_handler(pre_render_handler_key)
    delete_handler(post_render_handler_key)
    del bpy.types.Scene.viewport_monogamy_devices
    
if __name__ == '__main__':
    register()