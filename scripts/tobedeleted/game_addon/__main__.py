###Main game script.  This script is implemented in game.blend file and run in the ubuntu environment.
#Made by kamiya seisaku and distributed under cc0.

# bl_info = {
#     "name": "Start Game",
#     "author": "kkey",
#     "version": (1, 0),
#     "blender": (4, 1, 0),
#     "location": "View3D",
#     "description": "Start Game",
#     "warning": "",
#     "doc_url": "",
#     "category": "other",
# }

import bpy
import subprocess
import os

def game_per_frame_handler(scene):
    # this function gets called per frame
    # ui text update
    bpy.data.objects["ui.Text"].data.body = f"frame: {scene.frame_current}"
    # todo:    
    return

class VIEW3D_OT_process_input(bpy.types.Operator):
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"

    def __init__(self):
        print("Start")

    def __del__(self):
        print("End")

    def execute(self, context):
        context.object.location.x += 1
        return {'FINISHED'}

    def modal(self, context, event):
        if event.type == 'Q' and event.shift and event.ctrl:
            terminate_game()
            return {'CANCELLED'}
        elif event.type == 'A':
            bpy.data.objects["bikev16"].location[0] -= .5
        elif event.type == 'D':
            bpy.data.objects["bikev16"].location[0] += .5
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def get_userpref_path():
    # Get the Blender version
    blender_version = '.'.join(bpy.app.version_string.split('.')[:2])  # '2.93.5' -> '2.93'

    # Get the base path
    if os.name == 'nt':  # Windows
        base_path = os.path.join(os.getenv('APPDATA'), 'Blender Foundation', 'Blender')
    elif os.uname().sysname == 'Darwin':  # macOS
        base_path = os.path.join(os.getenv('HOME'), 'Library', 'Application Support', 'Blender')
    else:  # Linux and others
        base_path = os.path.join(os.getenv('HOME'), '.config', 'blender')

    # Get the path to the userpref.blend file
    userpref_path = os.path.join(base_path, blender_version, 'config', 'userpref.blend')
    return(userpref_path)
    
# class three_d_view_keymap_util:
#     def __init__(self):
#         # Get the current key configuration
#         self.kc = bpy.context.window_manager.keyconfigs.active

#         # Get the 3D view keymap
#         self.km = self.kc.keymaps['3D View']

#         # Store the active keymap items
#         self.active_keymap_items = [kmi for kmi in self.km.keymap_items if kmi.active]

#     def disable_default_keymap(self):
#         # Disable the 3D view keymap
#         for kmi in self.km.keymap_items:
#             kmi.active = False

#     def reactivate_default_keymap(self):
#         # Reactivate the stored keymap items
#         for kmi in self.active_keymap_items:
#             kmi.active = True

def init_game():
    userpref_path = get_userpref_path()
    bpy.data.objects["ui.Text"].data.body = userpref_path
    #TODO: set userpref.blend aside to preserve preferences.
    
    # keymap_util = three_d_view_keymap_util()
    # keymap_util.disable_default_keymap()    # Disable the default keymap
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(game_per_frame_handler)
    bpy.utils.register_class(VIEW3D_OT_process_input)

    bpy.context.scene.frame_set(1)    # Set the starting frame to 1
    bpy.ops.screen.animation_play()   # Start the animation
    return
 
def terminate_game():
    # Reactivate the default keymap
    # keymap_util=three_d_view_keymap_util()
    # keymap_util.reactivate_default_keymap()
    #TODO: restore userpref.blend that was set aside.

    return

init_game()
