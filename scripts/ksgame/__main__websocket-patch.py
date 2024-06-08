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
import asyncio
import websockets
import json
from mathutils import Vector

# Todo:
# 1 web casting
# 1 implement per frame rendering, where each frame is rendered to a separate image file on the fly.
#--------------------------------------------
# This operator registers itself (via .execute method) so that 
# the blender timer runs .modal method of this class every frame 
# (with scene animation running).
# event.type == 'FRAME_CHANGE_POST' becomes true every frame.
# event.type == 'A' becomes true every time user pressed A key.

def init_bricks():
    # Instead of using a class and store data in it, 
    #   (which was a failed attempt, since random and frequent data losses) 
    #   this function stores data as objects.
    sequence = [1, 2, 0, 3, 0, 2, 0, 3, 0, 2, 1, 2, 0, 1, 2, 0, 0, 3, 0, 4, 0, 3, 4, 3, 2, 1]
    # path_brick = bpy.data.objects.get('path_brick')
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

async def connect_websocket(operator_instance):
    uri = "ws://127.0.0.1:8080"  
    messages = []
    try:  
        async with websockets.connect(uri) as websocket:
            while not operator_instance.cancel_requested:
                try:
                    message = await websocket.recv()
                    messages.append(message)  
                except websockets.ConnectionClosed:
                    print("WebSocket connection closed.")
                    break  
    except (OSError, websockets.exceptions.WebSocketException) as e:
        print(f"WebSocket connection error: {e}")

    return messages  

class ModalTimerOperator(bpy.types.Operator):
    bl_idname = "wm.modal_timer_operator"
    bl_label = "ks game"
    path_util = None

    def modal(self, context, event):
        current_frame = bpy.context.scene.frame_current

        # openGL render frame
        # ... (You can uncomment this section if you need to save images) ...


        # ... (Your collision logic remains unchanged) ...
        # ... (Your escape key handling remains unchanged) ...

        # Handle key events from both WebSocket and keyboard
        if event.type == 'TIMER':
            messages = asyncio.run(connect_websocket(self))  # Get WebSocket messages
            for message in messages:
                data = json.loads(message)
                if data.get("key") in ['a', 'd']:
                    self.handle_key_input(context, data["key"])
        elif event.type in {'A', 'D'}:  # Handle regular keyboard events
            self.handle_key_input(context, event.type)

        return {'PASS_THROUGH'}

    def handle_key_input(self, context, key):
        # ... (Your existing key handling logic, using the 'key' variable) ...
        # Check if the bike is already moving (using the text object's content)
        bike_mover = bpy.data.objects.get('bike-mover')
        text_obj_key = bpy.data.objects.get('ui.Text.key') 
        text_obj_fn = bpy.data.objects.get('ui.Text.FN') 

        if text_obj_key.data.body == str(f"bike_mover is moving"):
            text_obj_key.data.body = str(f"bike_mover is not moving")
        else:
            text_obj_key.data.body = str(f"bike_mover is moving")

        frame_number = bpy.context.scene.frame_current
        text_obj_fn.data.body = str(f"FN:{frame_number}")

        # Handle key event based on 'a' or 'd' (using the 'key' variable)
        if key == 'a':
            if bike_mover.location.x < 1:
                bike_mover.location.x += 0.5
        elif key == 'd':
            if bike_mover.location.x > -1:
                bike_mover.location.x -= 0.5
        bpy.context.view_layer.update() # Need this for the change to be visible in 3D View

    def execute(self, context):
        # ... (Your execute method remains unchanged) ...

    def cancel(self, context):
        # ... (Your cancel method remains unchanged) ...

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

# ... (Rest of your code remains unchanged) ...
