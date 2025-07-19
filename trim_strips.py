import bpy


class SEQUENCER_OT_trim_all_strips(bpy.types.Operator):
    bl_idname = "sequencer.trim_all_strips"
    bl_label = "Trim All Strips Start/End"
    bl_options = {'REGISTER', 'UNDO'}

    trim_frames: bpy.props.IntProperty(name="Trim Frames", default=bpy.context.scene.render.fps, min=1)

    def execute(self, context):
        seq = context.scene.sequence_editor
        for s in seq.sequences_all:
            if s.frame_final_duration > self.trim_frames * 5:
                s.frame_final_start += self.trim_frames
                s.frame_final_end -= self.trim_frames
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(SEQUENCER_OT_trim_all_strips.bl_idname)

def register():
    bpy.utils.register_class(SEQUENCER_OT_trim_all_strips)
    bpy.types.SEQUENCER_MT_strip.append(menu_func)

def unregister():
    bpy.types.SEQUENCER_MT_strip.remove(menu_func)
    bpy.utils.unregister_class(SEQUENCER_OT_trim_all_strips)
