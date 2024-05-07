# This code is written for an indie game project "Uncirtain Days"
# by Kamiya Seisaku.
# This code is published with the MIT license, as is, no support obligation.
# Please use this code for whatever you want.
# It would be nice if you made something cool from here, then I'd love to know, 
# but you have no obligation to do so.
# I appreciate the blender team and the community for all they do.
# Kamiya Kei, 2024
import bpy
import sys
import os
# Todo:
#   -15:30 now lets make a ride-path
# [5/7] 
# Done:
# [5/7]
#   -15:00 clean the code
#     -removed KeybindingUtil for now, its not working. 
#     -removed nla editing codes its not in use for now.
#   -14:30 Bike shifted realtime with A and D keys! yay. Parented the bike to bike-mover empty and moved bike-mover on event A and D.
#   -14:00 key assign, w and d fine. ui text updated in realtime. yay. 
#   -13:00 need key assign.  w first, then d first.  
#     -manually remove assign.
#     -assign keymap.
# [5/6]
#   -17:00 PlayAndBlendActionsOperator removed entirely and function ok.
#   -15:33 animation playing going allright but not reacting to keyboard, got to move PlayAndBlendActionsOperator to ModalTimerOperator

#--------------------------------------------
# This operator registers itself (via .execute method) so that 
# the blender timer runs .modal method of this class every frame 
# (with scene animation running).
# event.type == 'FRAME_CHANGE_POST' becomes true every frame.
# event.type == 'A' becomes true every time user pressed A key.

class PathUtil:
    def __init__(self, sequence, rect):
        self.sequence = sequence
        self.rect = rect
        self.rectangles = []
        self.phase = 0

    def create_rectangles(self):
        for i, x in enumerate(self.sequence):
            if i < len(self.rectangles):
                new_rect = self.rectangles[i]
            else:
                new_rect = self.rect.copy()
                new_rect.data = self.rect.data.copy()
                new_rect.animation_data_clear()
                bpy.context.collection.objects.link(new_rect)
                self.rectangles.append(new_rect)
            new_rect.location.x = x
            new_rect.location.y = i + 1
            new_rect.location.z = 0

    def update_location(self, frame_count):
        self.phase = frame_count % len(self.sequence)
        for i, rect in enumerate(self.rectangles):
            rect.location.x = self.sequence[(i + self.phase) % len(self.sequence)]
            rect.location.y = i + 1


class ModalTimerOperator(bpy.types.Operator):
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"
    path_util = None

    def modal(self, context, event):
        if event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}

        if event.type in {'A', 'D'}:
            et = event.type
            text_obj = bpy.data.objects.get('ui.Text.003')
            frame_number = bpy.context.scene.frame_current
            text_obj.data.body = str(f"FN:{frame_number}, {et} pressed")
            bike_mover = bpy.data.objects.get('bike-mover')
            if et == 'A':
                if bike_mover.location.x >= 1:
                    bike_mover.location.x += 0.5
            if et == 'D':
                if bike_mover.location.x <= -1:
                    bike_mover.location.x -= 0.5

        self.path_util.update_location(bpy.context.scene.frame_current)

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        bpy.app.handlers.frame_change_post.append(self.modal)
        wm.modal_handler_add(self)

        # Create riding path.
        sequence = [1, 2, 0, 3, 0, 2, 0, 3, 0, 2, 1, 2, 0, 1, 2, 0, 0, 3, 0, 4, 0, 3, 4, 3, 2, 1]
        rect = bpy.data.objects.get('path_brick')
        self.path_util = PathUtil(sequence, rect)
        self.path_util.create_rectangles()

        # Switch to modeling workspace
        bpy.context.window.workspace = bpy.data.workspaces['Modeling']

        # Switch 3D view shading to rendered
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].shading.type = 'RENDERED'

        # Play active scene animation
        bpy.ops.screen.animation_play()
 
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        bpy.app.handlers.frame_change_post.remove(self.modal)


#--------------------------------------------
# Register ModalTimerOperator in layout menu
def menu_func(self, context):
   self.layout.operator(ModalTimerOperator.bl_idname, text=ModalTimerOperator.bl_label)


# Register and add to the "view" menu (required to also use F3 search "Modal Timer Operator" for quick access).
def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)
    bpy.types.VIEW3D_MT_view.remove(menu_func)

def register():
    # unregister()
    bpy.utils.register_class(ModalTimerOperator)
    bpy.types.VIEW3D_MT_view.append(menu_func)

# Todo: [debug]
register()

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.wm.modal_timer_operator()