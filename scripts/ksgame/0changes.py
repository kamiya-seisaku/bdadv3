        # Todo: Add and play action "brick_hit" at the scene frame when the bike hits the brick (object distance < threshold)
        if event.type in {'A', 'D'} | event.type == 'TIMER':
            if event.type == 'TIMER':
                messages = asyncio.run(connect_websocket(self))  # Get messages
                for message in messages:
                    data = json.loads(message)
                    if data.get("key") in ['a', 'd']:
                        key_input = data.get("key").upper()
            elif event.type in {'A', 'D'}:
                    key_input = data.get("key")

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
                frame_number = bpy.context.scene.frame_current
                # to show the score in the 3D view, the body of the ui text object
                # is set according to the same object's custom property "score"
                text_obj_fn.data.body = str(f"FN:{frame_number}")
                # key event handling
                if key_input == 'A':
                    if bike_mover.location.x < 1:
                        bike_mover.location.x += 0.5
                if key_input == 'D':
                    if bike_mover.location.x > -1:
                        bike_mover.location.x -= 0.5
                bpy.context.view_layer.objects.active = bike_mover #Need this to make location changes into blender data
                bpy.context.view_layer.update() #Need this for the change to be visible in 3D View
