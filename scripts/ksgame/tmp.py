# Goal: implement per frame rendering, where each frame is rendered to a separate image file on the fly.
import bpy

# Set the output path
bpy.context.scene.render.filepath = "/path/to/output/directory/frame_"

# Set the output format to PNG
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Loop over the frames you want to render
for frame in range(start_frame, end_frame + 1):
    # Set the current frame
    bpy.context.scene.frame_set(frame)

    # Render the frame to an image
    bpy.ops.render.render(write_still=True)
