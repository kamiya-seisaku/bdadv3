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
# [5/8] 15:50 brics wasnt visiby relocated in create_path_bricks, 
#   needed bpy.context.view_layer.objects.active to make location into blender data object
#   now bricks are in good position except y should be negative

#   -15:30 coding PathUtil to form a path in front of the character to follow
        # todo: needs to run brick creation as the game starts (which is more of spawn), not when this code initiates
        # todo: needs to clear brickes when esc otherwise brics object 

#--------------------------------------------
# This operator registers itself (via .execute method) so that 
# the blender timer runs .modal method of this class every frame 
# (with scene animation running).
# event.type == 'FRAME_CHANGE_POST' becomes true every frame.
# event.type == 'A' becomes true every time user pressed A key.

class PathUtil:
    # create an array of brick_obj in front of the character, according to sequence
    # update the brick_obj array, as the character proceeds
    def __init__(self, sequence, brick_obj):
        self.sequence = sequence
        self.rect = brick_obj
        self.rectangles = []
        self.phase = 0

    def create_path_bricks(self):
        for i in range(1, 30):
            brick_name = f"path_brick.{i:03d}"
            brick = bpy.data.objects.get(brick_name)
            if brick is not None:
                self.rectangles.append(brick)

        # Position the bricks according to the sequence
        for i, x in enumerate(self.sequence):
            if i < len(self.rectangles): #runs only up to rectangles length, even when sequence was longer 
                new_rect = self.rectangles[i]
                interval = -2.0
                offset = -2.0
                new_rect.location.x = x
                new_rect.location.y = offset + i * interval
                new_rect.location.z = 2.84831
                bpy.context.view_layer.objects.active = new_rect
                bpy.context.view_layer.update()
        # # collection = bpy.data.collections.get('buildings') # Get the collection
        # # layer_collection = bpy.context.view_layer.layer_collection.children[collection.name] # Get the LayerCollection corresponding to the collection
        # # bpy.context.view_layer.active_layer_collection = layer_collection # Set the active layer collection
        
        # # create copies of brick_obj in front of player according to sequence
        # for i, x in enumerate(self.sequence):
        #     # if i < len(self.rectangles):
        #     #     new_rect = self.rectangles[i]
        #     # else:
        #     new_rect = self.rect.copy()
        #     new_rect.data = self.rect.data.copy()
        #     # new_rect.animation_data_clear()
        #     bpy.context.collection.objects.link(new_rect)
        #     self.rectangles.append(new_rect)
        #     interval = -2.0
        #     offset = -2.0
        #     new_rect.location.x = x
        #     new_rect.location.y = offset + i * interval
        #     new_rect.location.z = 2.84831
        #     bpy.context.view_layer.objects.active = new_rect #Need this to make location change into blender data
        #     bpy.context.view_layer.update()
        bpy.context.view_layer.update()
        bpy.ops.wm.save_as_mainfile() #save the changes into .blend file

    # def delete_path_bricks(self):
    #     # delete all path bricks created in create_path_bricks method
    #     for rect in self.rectangles:
    #         # Unlink the rectangle from the scene
    #         bpy.context.collection.objects.unlink(rect)
    #         # Delete the rectangle object
    #         bpy.data.objects.remove(rect)
    #     # Clear the rectangles list
    #     self.rectangles = []
    #     bpy.context.view_layer.update()

    # remove the last brick and add one ahead following the sequence
    def update_path_bricks(self, frame_count):
        self.phase = frame_count % len(self.sequence)
        for i, rect in enumerate(self.rectangles):
            rect.location.x = self.sequence[(i + self.phase) % len(self.sequence)]
            rect.location.y = i + 1
        self.phase += 1
        bpy.context.view_layer.update()


class ModalTimerOperator(bpy.types.Operator):
    bl_idname = "wm.modal_timer_operator"
    bl_label = "ks game"
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
            if et == 'D':
                if bike_mover.location.x < 1:
                    bike_mover.location.x += 0.5
            if et == 'A':
                if bike_mover.location.x > -1:
                    bike_mover.location.x -= 0.5

        self.path_util.update_path_bricks(bpy.context.scene.frame_current)
        bpy.context.view_layer.update()

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
        self.init_path()
        # Play active scene animation
        bpy.ops.screen.animation_play()
 
        return {'RUNNING_MODAL'}

    def init_path(self):
        # Create riding path.
        sequence = [1, 2, 0, 3, 0, 2, 0, 3, 0, 2, 1, 2, 0, 1, 2, 0, 0, 3, 0, 4, 0, 3, 4, 3, 2, 1]
        path_brick = bpy.data.objects.get('path_brick')
        self.path_util = PathUtil(sequence, path_brick)
        self.path_util.create_path_bricks()

    def cancel(self, context):
        self.delete_path_bricks()
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