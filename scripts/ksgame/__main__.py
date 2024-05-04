import bpy
import sys
import os

class PlayAndBlendActionsOperator(bpy.types.Operator):
    bl_idname = "object.play_and_blend_actions"
    bl_label = "Play and Blend Actions"

    # Initialize loop count and frame number variables
    loop_count = 0
    frame_number = 0

    def execute(self, context):
        # Initialize loop count and frame number variables
        loop_count = 0
        frame_number = bpy.context.scene.frame_current
        bpy.ops.screen.animation_play()
        return {'FINISHED'}

    def modal(self, context, event):
        text_obj = bpy.data.objects.get('ui.Text.003')
        frame_number = bpy.context.scene.frame_current
        text_obj.data.body = str(f"frame: {frame_number}")
        obj = context.object

        # Ensure the object is an armature with animation data
        if obj.type == 'ARMATURE' and obj.animation_data:

            # Disable existing 'A' and 'D' key bindings
            km = bpy.context.window_manager.keyconfigs.user.keymaps['3D View']
            for kmi in km.keymap_items:
                if kmi.type in {'A', 'D'}:
                    km.keymap_items.remove(kmi)

            # Play 'bike.ride' action
            bike_ride = bpy.data.actions.get('bike.ride')
            if bike_ride:
                obj.animation_data.action = bike_ride

            # Blend 'bike.turn.l' action when a key is pressed
            bike_turn_l = bpy.data.actions.get('bike.turn.l')
            if bike_turn_l and context.window.event.keyname == 'A':
                # Create a new NLA track and add the action strip
                track = obj.animation_data.nla_tracks.new()
                strip = track.strips.new('bike.turn.l', 1, bike_turn_l)

                # Set blending options
                strip.blend_type = 'ADD'
                strip.blend_in = 10
                strip.blend_out = 10

        return {'FINISHED'}

#--------------------------------------------
# This operator registers itself (via .execute) as a timer event so that 
# the blender timer runs .modal of this class per frame.
class ModalTimerOperator(bpy.types.Operator):
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"
    
    # _timer = None

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'FRAME_CHANGE_POST':
            # change theme color, silly!
            color = context.preferences.themes[0].view_3d.space.gradients.high_gradient
            color.s = 1
            color.h += 0.01
            PlayAndBlendActionsOperator.modal(self, context, event)
            
        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        # self._timer = wm.event_timer_add(0.1, window=context.window)
        bpy.app.handlers.frame_change_post.append(self.modal)
        wm.modal_handler_add(self)
        PlayAndBlendActionsOperator.execute(self, context)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        # wm.event_timer_remove(self._timer)
        bpy.app.handlers.frame_change_post.remove(self.modal)


#--------------------------------------------
# Register ModalTimerOperator in layout menu
def menu_func(self, context):
    # for ws in {self.layout, self.scripting, self.animation}
    #     ws.operator(ModalTimerOperator.bl_idname, text=ModalTimerOperator.bl_label)

   self.layout.operator(ModalTimerOperator.bl_idname, text=ModalTimerOperator.bl_label)
   self.scripting.operator(ModalTimerOperator.bl_idname, text=ModalTimerOperator.bl_label)
   self.animation.operator(ModalTimerOperator.bl_idname, text=ModalTimerOperator.bl_label)


def register():
    bpy.utils.register_class(ModalTimerOperator)
    bpy.utils.register_class(PlayAndBlendActionsOperator)
    bpy.types.VIEW3D_MT_view.append(menu_func)


# Register and add to the "view" menu (required to also use F3 search "Modal Timer Operator" for quick access).
def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)
    bpy.utils.unregister_class(PlayAndBlendActionsOperator)
    bpy.types.VIEW3D_MT_view.remove(menu_func)

# Todo: [debug]
register()

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.wm.modal_timer_operator()
