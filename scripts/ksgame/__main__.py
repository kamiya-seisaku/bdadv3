######## 2024/6/9 checked out from 6b96863 (probably working ver) #####
######## 2024/6/9 adding parts from websock ver #######################

# This code is written for a Blender indie game project "Uncirtain Days"
# This code is published with the MIT license, as is, no support obligation.
# Please use this code for whatever you want, but at your risk.
# It would be nice if you made something cool from here, then I'd love to know.
# I like all kind of games.
# Kamiya Seisaku, Kamiya Kei, 2024
import bpy
import sys
import os
import glob
from mathutils import Vector
# import asyncio
import websockets
# import json
# import subprocess

def init_bricks():
    sequence = [1, 2, 0, 3, 0, 2, 0, 3, 0, 2, 1, 2, 0, 1, 2, 0, 0, 3, 0, 4, 0, 3, 4, 3, 2, 1]
    rectangles = []

    # Delete existing bricks first, then make copies
    brick_names = [f"path_brick.{i:03d}" for i in range(1, 30)]
    brick_names_hit = [name + "_hit" for name in brick_names]
    all_brick_names = brick_names + brick_names_hit
    for name in all_brick_names:
        if name in bpy.data.objects:
            bpy.ops.object.select_all(action="DESELECT")
            bpy.data.objects[name].select_set(True)
            bpy.ops.object.delete()

    original_brick = bpy.data.objects.get("path_brick")
    bpy.context.view_layer.objects.active = original_brick # Explicitly set the active object
    bpy.context.view_layer.update() #Force refrect data changes to view
    for i in range(1, len(sequence)):
        # then (re)create the brick copy
        brick_name = f"path_brick.{i:03d}"
        bpy.ops.object.select_all(action="DESELECT")
        original_brick.select_set(True)
        bpy.ops.object.duplicate()
        bpy.ops.object.select_all(action='DESELECT')
        brick = bpy.data.objects.get(brick_name)
        bpy.context.view_layer.objects.active = brick
        bpy.context.view_layer.update()

        if brick is not None:
            rectangles.append(brick)

    # Position the bricks according to the sequence
    for i, x in enumerate(sequence):
        if i < len(rectangles): #runs only up to rectangles length, even when sequence was longer 
            new_rect = rectangles[i]
            interval = -4.0
            offset = -2.0
            new_rect.location.x = x
            new_rect.location.y = offset + i * interval
            new_rect.location.z = 4
            # new_rect.parent = original_brick
            bpy.context.view_layer.objects.active = new_rect
            bpy.context.view_layer.update()

# async def connect_websocket(operator_instance):
#      = "ws://localhost:8080"  
#     messages = []
#     try:
#         async with websockets.connect(uri) as websocket:
#             while not operator_instance.cancel_requested:
#                 try:
#                     message = await websocket.recv()
#                     messages.append(message)  # Store received messages
#                 except websockets.ConnectionClosed:
#                     print("WebSocket connection closed.")
#                     break  # Exit the loop on connection closure
#     except (OSError, websockets.exceptions.WebSocketException) as e:
#         print(f"WebSocket connection error: {e}")
#     return messages  # Return all received messages

class ModalTimerOperator(bpy.types.Operator):
    bl_idname = "wm.modal_timer_operator"
    bl_label = "ks game"
    path_util = None

    websocket = None # websocket connection. variable in class score should be sustained
    uri = "ws://localhost:8080"  

    def modal(self, context, event):
        current_frame = bpy.context.scene.frame_current

        # Avoids "AttributeError: 'Depsgraph' object has no attribute 'type'" when mouse cursor is not in 3D view
        if isinstance(event, bpy.types.Event) == False:
            return {'PASS_THROUGH'}

        if event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}

        # Check for WebSocket connection (if not already connected)
        if not self.websocket:
            try:
                self.websocket = websockets.connect(self.uri)
                # Consider waiting for a successful connection before proceeding
            except Exception as e:
                print(f"WebSocket connection error: {e}")
                return {'CANCELLED'}  # Or handle the error differently

        # Receive WebSocket message (if connected)
        if self.websocket:
            try:
                message = self.websocket.recv()
                if message & message.startswith("key:"):
                    key = message.substring(4)  # Python doesn't have substring, use slicing instead
                    key = key.strip()  # Remove potential leading/trailing whitespace
                    # Process the key (similar to key_handling)
                    if key in ['A','D']:
                        print(f"{key} pressed on webpage")
                        self.key_handling(context, event, key)

            except websockets.ConnectionClosed:
                print("WebSocket connection closed.")
                self.ws = None  # Mark connection as closed
            except Exception as e:
                print(f"WebSocket receive error: {e}")

        # Todo: need repeated key event handling: pass event while action "brick_hit" is playing in nla (getting better but not perfect)
        # Add and play action "brick_hit" at the scene frame when the bike hits the brick (object distance < threshold)
        if event.type in {'A', 'D'}:
            key_input = event.type
            self.key_handling(context, event, key_input)
            return {'PASS_THROUGH'}

        return {'PASS_THROUGH'}

    def key_handling(self, context, event, key_input):
        # Check if the bike is already moving
        # if moving skip the key event handling
        # (without imprementing this socond side move happens in the next frame)
        bike_mover = bpy.data.objects.get('bike-mover')
        text_obj_key = bpy.data.objects.get('ui.Text.key') # get ui text object for key event capture display
        text_obj_fn = bpy.data.objects.get('ui.Text.FN') # get ui text object for frame number display
        # if bike_mover["is_moving"]: # not clear how bike mover custom properties are changing, lets instead use ui_text
        if text_obj_key.data.body == str(f"bike_mover is moving"):
            # bike_mover["is_moving"] = False
            text_obj_key.data.body = str(f"bike_mover is not moving")
        else:
            # bike_mover["is_moving"] = True
            text_obj_key.data.body = str(f"bike_mover is moving")
            et = event.type
            frame_number = bpy.context.scene.frame_current
            # to show the score in the 3D view, the body of the ui text object
            # is set according to the same object's custom property "score"
            text_obj_fn.data.body = str(f"FN:{frame_number}")
            # key event handling
            if et == 'A':
                if bike_mover.location.x < 1:
                    bike_mover.location.x += 0.5
            if et == 'D':
                if bike_mover.location.x > -1:
                    bike_mover.location.x -= 0.5
            bpy.context.view_layer.objects.active = bike_mover #Need this to make location changes into blender data
            bpy.context.view_layer.update() #Need this for the change to be visible in 3D View

        # self.path_util.update_path_bricks(bpy.context.scene.frame_current)
        return

    def execute(self, context):
        # called when bpy.ops.wm.modal_timer_operator() is called or user selects menu

        # Register modal method of this class as frame_change_post handler
        # After this registration, modal method of this class will be called
        # every frame

        # clear image folder
        files = glob.glob('C:\\tmp\\*')
        for f in files:
            os.remove(f)

        # running init_bricks() from operator/__main__ are'nt working.  run it from blender text editor.:       init_bricks()
        bike_mover = bpy.data.objects['bike-mover']
        bike_mover.location = [0, 0, 0]
        bpy.context.view_layer.objects.active = bike_mover #Need this to make location changes into blender data
        bpy.context.view_layer.update() #Need this for the change to be visible in 3D View

        wm = context.window_manager
        bpy.app.handlers.frame_change_post.append(self.modal)
        wm.modal_handler_add(self)

        bpy.context.window.workspace = bpy.data.workspaces['Modeling'] # Switch blender UI to modeling workspace

        # Switch 3D view shading to rendered
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].shading.type = 'RENDERED'

        score_obj = bpy.data.objects.get('ui.Text.score')
        score_obj["score"] = 0 # Reset game score
        # score = score_obj["score"] # Reset game score
        # score = 0
        bpy.ops.screen.animation_play() # Play active scene animation
 
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        bpy.app.handlers.frame_change_post.remove(self.modal)
        return {'PASS_THROUGH'}

#--------------------------------------------
# Register ModalTimerOperator in layout menu
def menu_func(self, context):
   self.layout.operator(ModalTimerOperator.bl_idname, text=ModalTimerOperator.bl_label)

# Register and add to the "view" menu (required to also use F3 search "Modal Timer Operator" for quick access).
def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)
    bpy.types.VIEW3D_MT_view.remove(menu_func)

def register():
    bpy.utils.register_class(ModalTimerOperator)
    bpy.types.VIEW3D_MT_view.append(menu_func)

# Todo: comment out [debug codes]
register()
bpy.ops.wm.modal_timer_operator()
#init_bricks()
#unregister()

if __name__ == "__main__":
    register()
    bpy.ops.wm.modal_timer_operator()