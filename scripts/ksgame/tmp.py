import bpy

# Create the actions
shift_left = bpy.data.actions.new("shift_left")
shift_right = bpy.data.actions.new("shift_right")

# Add the actions to the NLA track
bike = bpy.data.objects.get('bikev16')
track = bike.animation_data.nla_tracks.new()
track.strips.new("shift_left", 0, shift_left)
track.strips.new("shift_right", 0, shift_right)

# Mute all strips
for strip in track.strips:
    strip.mute = True

# In your modal operator
if et == 'A':
    # Unmute the 'shift_left' strip and mute the 'shift_right' strip
    track.strips["shift_left"].mute = False
    track.strips["shift_right"].mute = True
    # Set the start frame of the 'shift_left' strip to the current frame
    track.strips["shift_left"].frame_start = bpy.context.scene.frame_current

if et == 'D':
    # Unmute the 'shift_right' strip and mute the 'shift_left' strip
    track.strips["shift_right"].mute = False
    track.strips["shift_left"].mute = True
    # Set the start frame of the 'shift_right' strip to the current frame
    track.strips["shift_right"].frame_start = bpy.context.scene.frame_current
