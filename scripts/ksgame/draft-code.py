# execute > called when operator is invoked
#   not when operator class is 

# However, in your code, 
# the execute method is also adding the modal method to the frame_change_post handlers
# then modal will be called after each frame change
# If you want to run the code in the execute method only when the operator is called, you can move the code that creates the riding path and switches the workspace and shading to a separate method, and call this method from the modal method when needed.


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
            if et == 'D':
                if bike_mover.location.x < 1:
                    bike_mover.location.x += 0.5
            if et == 'A':
                if bike_mover.location.x > -1:
                    bike_mover.location.x -= 0.5

        self.path_util.update_path_bricks(bpy.context.scene.frame_current)

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        bpy.app.handlers.frame_change_post.append(self.modal)
        wm.modal_handler_add(self)
        self.setup_path_and_view()
        return {'RUNNING_MODAL'}

    def setup_path_and_view(self):
        # Create riding path.
        sequence = [1, 2, 0, 3, 0, 2, 0, 3, 0, 2, 1, 2, 0, 1, 2, 0, 0, 3, 0, 4, 0, 3, 4, 3, 2, 1]
        path_brick = bpy.data.objects.get('path_brick')
        self.path_util = PathUtil(sequence, path_brick)
        self.path_util.create_path_bricks()

        # Switch to modeling workspace
        bpy.context.window.workspace = bpy.data.workspaces['Modeling']

        # Switch 3D view shading to rendered
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].shading.type = 'RENDERED'

        # Play active scene animation
        bpy.ops.screen.animation_play()

    def cancel(self, context):
        wm = context.window_manager
        bpy.app.handlers.frame_change_post.remove(self.modal)
