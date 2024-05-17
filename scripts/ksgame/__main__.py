# This code is written for a Blender indie game project "Uncirtain Days"
# This code is published with the MIT license, as is, no support obligation.
# Please use this code for whatever you want, but at your risk.
# It would be nice if you made something cool from here, then I'd love to know.
# I like all kind of games.
# Kamiya Seisaku, Kamiya Kei, 2024
import bpy
import sys
import os
from mathutils import Vector
# Todo:
# 1 init score
# 2 Youtube publication prep 
# 3 bricks actions 
# [5/10]
#   04:00 game frame rate reduced to 8 fps (property>Output panel>Scene>Format>Frame Rate, was 24)
# -increase score
# -move passed brick forward
# -curve path  
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

class ModalTimerOperator(bpy.types.Operator):
    bl_idname = "wm.modal_timer_operator"
    bl_label = "ks game"
    path_util = None

    def modal(self, context, event):
        # game score is held in the ui text object, custom property "score"
        # increase score when the bike hits one of the bricks
        if bpy.context.scene.frame_current % 60 == 0:
            # brick hit logics (CPU heavy) run only every 60 frames
            # Check the distance between the bike and each brick
            # run hit action and then the hit brick is renamed by adding "_hit"
            colision_range = range(1, 10) #originally: range(1, 31)
            bricks = [bpy.data.objects.get(f'path_brick.{i:03d}') for i in colision_range]
            bricks = [brick for brick in bricks if brick is not None] # remove None objects. hit bricks become None.
            for brick_id, brick in enumerate(bricks):
                bike = bpy.data.objects.get('bikev16')
                bike_location = bike.location
                # set hit point of the bike in front of bike, negative in y direction
                hit_point = bike_location + Vector((0, -2, 0))
                bpy.context.view_layer.objects.active = brick
                distance = (hit_point - brick.location).length
                if distance < .5:  # If the distance is less than 3m
                    # Now let the hit brick play "brick_hit" hit action.
                    # This involves 1 create animation data 2 create a nla track, and 3 create a action strip. 
                    brick.animation_data_create()
                    action = bpy.data.actions["brick_hit"]

                    # Get the list of NLA tracks
                    tracks = brick.animation_data.nla_tracks

                    # Check if there are any tracks already.  If not, create one.
                    for track in tracks:
                        if track.name == "brick_hit_track":
                            break
                    else:
                        if len(tracks) > 0:
                            track = tracks.new(prev=tracks[-1]) # If there are, insert the new track before the last one
                        else:
                            track = tracks.new() # If there aren't, just append the new track at the end

                        track.name = "brick_hit_track" # Set the name of the track

                    # add a strip (plain "brick_hit" action) to the track
                    strip = track.strips.new(name="brick_hit", start=bpy.context.scene.frame_current, action=action)
                    # # Shift the action to start at the current frame
                    strip.frame_start = bpy.context.scene.frame_current
                    strip.frame_end = strip.frame_start + (action.frame_range[1] - action.frame_range[0])
                    bpy.context.view_layer.objects.active = brick #Need this to make location changes into blender data
                    # Todo: 5/15 for some reason the brick is not getting deleted
                    # 5/15 bricks is recreated every frame from brick objects so removing from bricks list makes no sense:  bricks.remove(id=brick_id) #remove the hit brick from the array bricks so it wont get hit again
                    bpy.ops.object.select_all(action="DESELECT")
                    brick.select_set(True) # Select the object in 3D view
                    # hide the brick in 3D view
                    brick.name = brick.name + "_hit"
                    # no I don't delete the object, I want it to play hit animation first.  bpy.ops.object.delete() # Delete the object from blender data
                    # todo------------------------------------------

                    score_obj = bpy.data.objects.get('ui.Text.score')
                    score_obj["score"] += 1
                    bpy.context.view_layer.objects.active = score_obj #Need this to make location changes into blender data
                    score = score_obj["score"]
                    score_obj.data.body = str(f"Score:{score}")
                    bpy.context.view_layer.objects.active = score_obj #Need this to make location changes into blender data
                    FN_obj = bpy.data.objects.get('ui.Text.FN')
                    FN_obj.data.body = str(f"FN:{bpy.context.scene.frame_current}")
                    bpy.context.view_layer.objects.active = score_obj #Need this to make location changes into blender data
                    break  # pass this frame (and not detect key events till next frame)
        
        # key event handling runs every frame for better reactivity

        # Avoids "AttributeError: 'Depsgraph' object has no attribute 'type'" when mouse cursor is not in 3D view
        if isinstance(event, bpy.types.Event) == False:
            return {'PASS_THROUGH'}

        if event.type == 'ESC':
                self.cancel(context)
                return {'CANCELLED'}

        # Todo: need repeated key event handling: pass event while action "brick_hit" is playing in nla (getting better but not perfect)
        # Add and play action "brick_hit" at the scene frame when the bike hits the brick (object distance < threshold)

        if event.type in {'A', 'D'}:
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

        return {'PASS_THROUGH'}

    def execute(self, context):
        # called when bpy.ops.wm.modal_timer_operator() is called or user selects menu

        # Register modal method of this class as frame_change_post handler
        # After this registration, modal method of this class will be called
        # every frame

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
#register()
#init_bricks()
#unregister()

if __name__ == "__main__":
    register()
#    bpy.ops.wm.modal_timer_operator()