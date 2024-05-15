import bpy

def init_bricks():
    # Instead of using a class and store data in it, 
    #   (which was a failed attempt, since random and frequent data losses) 
    #   this function stores data as objects.
    sequence = [1, 2, 0, 3, 0, 2, 0, 3, 0, 2, 1, 2, 0, 1, 2, 0, 0, 3, 0, 4, 0, 3, 4, 3, 2, 1]
    # path_brick = bpy.data.objects.get('path_brick')
    rectangles = []

    for i in range(1, 30):
        # delete existing brick copy with index i
        brick_name = f"path_brick.{i:03d}"
        if brick_name in bpy.data.objects:
            # Select the object
            bpy.data.objects[brick_name].select_set(True)
            
            # Delete the object
            bpy.ops.object.delete()

    original_brick = bpy.data.objects.get("path_brick")
    for i in range(1, len(sequence)):
        # then (re)create the brick copy
        brick_name = f"path_brick.{i:03d}"
        original_brick.select_set(True)
        bpy.ops.object.duplicate()
        bpy.ops.object.select_all(action='DESELECT')
        brick = bpy.data.objects.get(brick_name)

        if brick is not None:
            rectangles.append(brick)

    # Position the bricks according to the sequence
    for i, x in enumerate(sequence):
        if i < len(rectangles): #runs only up to rectangles length, even when sequence was longer 
            new_rect = rectangles[i]
            interval = -2.0
            offset = -2.0
            new_rect.location.x = x
            new_rect.location.y = offset + i * interval
            new_rect.location.z = 2.84831
            new_rect.parent = original_brick
            bpy.context.view_layer.objects.active = new_rect
            bpy.context.view_layer.update()

init_bricks()