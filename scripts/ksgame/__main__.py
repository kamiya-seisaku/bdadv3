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
# [5/9] 
# *lets fix score and release as beta
#   12:00 init_bricks was called statically from blender text editor not from this file.
#   15:50 scoreing not increasing, test visinity threshold 2 (was.7)
# -init score
# -increase score
# -move passed brick forward
# -curve path  
#--------------------------------------------
# This operator registers itself (via .execute method) so that 
# the blender timer runs .modal method of this class every frame 
# (with scene animation running).
# event.type == 'FRAME_CHANGE_POST' becomes true every frame.
# event.type == 'A' becomes true every time user pressed A key.

class ModalTimerOperator(bpy.types.Operator):
    bl_idname = "wm.modal_timer_operator"
    bl_label = "ks game"
    path_util = None

    def modal(self, context, event):
        # game score is held in the ui text object, custom property "score"
        # increase score when the bike hits one of the bricks

        # to show the score in the 3D view, the body of the ui text object
        # is set according to the same object's custom property "score"

        if bpy.context.scene.frame_current % 60 == 0:
            score_obj = bpy.data.objects.get('ui.Text.004.score')

            # Check the distance between the bike and each brick
            bike = bpy.data.objects.get('bikev16') # Get the bike object
            colision_range = range(1, 10) #originally: range(1, 31)
            bricks = [bpy.data.objects.get(f'path_brick.{i:03d}') for i in colision_range] # Get the brick objects
            for brick in bricks:
                distance = (bike.location - brick.location).length
                if distance < 0.7:  # If the distance is less than 50cm
                    score_obj["score"] += 1
                    bpy.context.view_layer.objects.active = score_obj #Need this to make location changes into blender data
                    break  # Assuming the score should only be incremented once per frame

            score = score_obj["score"]
            score_obj.data.body = str(f"Score:{score}")
            bpy.context.view_layer.objects.active = score_obj #Need this to make location changes into blender data
        
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
                if bike_mover.location.x < 1:
                    bike_mover.location.x += 0.5
            if et == 'D':
                if bike_mover.location.x > -1:
                    bike_mover.location.x -= 0.5
            bpy.context.view_layer.objects.active = bike_mover #Need this to make location changes into blender data
            bpy.context.view_layer.update() #Need this for the change to be visible in 3D View

        # self.path_util.update_path_bricks(bpy.context.scene.frame_current)

        return {'PASS_THROUGH'}

    def execute(self, context):
        # This method will be called when the operator "Modal Timer Operator" is called 
        #   which is when the user selected the menu item
        #   (not when the class ModalTimerOperator is registered)

        # Register modal method of this class as frame_change_post handler
        # After this registration, modal method of this class will be called
        # every frame
        wm = context.window_manager
        bpy.app.handlers.frame_change_post.append(self.modal)
        wm.modal_handler_add(self)

        # Switch blender UI to modeling workspace
        bpy.context.window.workspace = bpy.data.workspaces['Modeling']

        # Switch 3D view shading to rendered
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].shading.type = 'RENDERED'

        # Creates ride path before scene animation plays
        init_bricks()
        # Play active scene animation
        bpy.ops.screen.animation_play()
 
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        # self.delete_path_bricks()
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