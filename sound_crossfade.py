import bpy

class SEQUENCER_OT_auto_sound_crossfade(bpy.types.Operator):
    bl_idname = "sequencer.auto_sound_crossfade"
    bl_label = "Auto Sound Crossfade"
    bl_options = {'REGISTER', 'UNDO'}

    fade_duration: bpy.props.IntProperty(name="Fade Duration", default=bpy.context.scene.render.fps)


    def get_next_strip(current):
        """指定ストリップの次に来るストリップを探す"""
        all_strips = bpy.context.scene.sequence_editor.sequences_all
        same_type_strips = [s for s in all_strips if s.type == current.type and s.name != current.name]
        print(f"current: {current.frame_start}, {current.animation_offset_start}")
        candidates = [s for s in same_type_strips if s.frame_final_start >= current.frame_final_end]
        candidates.sort(key=lambda s: s.frame_start)
        return candidates[0] if candidates else None
    
    def find_free_channel(start_frame, end_frame):
        """指定フレーム範囲に空いているチャネル番号を見つける"""
        seq = bpy.context.scene.sequence_editor
        max_channel = 0
        for s in seq.sequences_all:
            if s.frame_final_start < end_frame and s.frame_final_end > start_frame:
                max_channel = max(max_channel, s.channel)
        return max_channel + 1
    
    def move_to_free_channel(strip, new_channel):
        """指定チャネルに移動"""
        print(f"Moving {strip.name} to channel {new_channel}")
        strip.channel = new_channel
    
    def extend_strip_start(strip, extend_by):
        print(f"{strip.name} change frame_start {strip.frame_start} to {strip.frame_start - extend_by}") 
        strip.frame_final_start -= extend_by
    
    def get_volume_at_frame(strip, frame):
        try:
            return strip.path_resolve("volume").evaluate(frame)
        except AttributeError:
            # アニメーションがない場合などは現在値を返す
            return strip.volume
    
    def apply_volume_fadein(strip, fade_duration):
        start = strip.frame_final_start
        end = start + fade_duration
        #strip_volume = get_volume_at_frame(strip, end)
        print(f"fadein {strip.name}: strip_volume = 1.0: {start} to {end}")
        strip.volume = 0.0
        strip.keyframe_insert(data_path="volume", frame=start)
        strip.volume = 1.0
        strip.keyframe_insert(data_path="volume", frame=end)
    
    def apply_volume_fadeout(strip, fade_duration):
        start = strip.frame_final_end - fade_duration
        end = strip.frame_final_end
        strip.volume = 1.0 # get_volume_at_frame(strip, start)
        print(f"fadeout {strip.name}: strip_volume = {strip.volume}: {start} to {end}")
        strip.keyframe_insert(data_path="volume", frame=start)
        strip.volume = 0.0
        strip.keyframe_insert(data_path="volume", frame=end)
    
    def execute(self, context):
        print(f"fade_duration = {fade_duration}")
        scene = bpy.context.scene
        if not scene.sequence_editor:
            self.report({'WARNING'}, "No sequencer found.")
            return {'CANCELLED'}
    
        selected = [s for s in scene.sequence_editor.sequences_all if s.select and s.type == 'SOUND']
        if len(selected) != 1:
            self.report({'WARNING'}, "Please select exactly one strip.")
            return {'CANCELLED'}
    
        strip_a = selected[0]
        strip_b = self.get_next_strip(strip_a)
        print(f"crossfade audio {strip_a.name} with {strip_b.name}")
        if not strip_b:
            self.report({'WARNING'}, "No next strip found.")
            return {'CANCELLED'}
    
        # オーバーラップ開始点
        overlap_start = strip_a.frame_final_end - fade_duration
        overlap_end = strip_a.frame_final_end
        print(f"overlap start: {overlap_start}, end: {overlap_end}")
    
        # チャンネルが同じなら、bをずらす
        if strip_a.channel == strip_b.channel:
            new_channel = self.find_free_channel(overlap_start, strip_b.frame_final_end)
            self.move_to_free_channel(strip_b, new_channel)
    
        # b を前に延ばす
        self.extend_strip_start(strip_b, fade_duration)
    
        # フェードをかける
        self.apply_volume_fadeout(strip_a, fade_duration)
        self.apply_volume_fadein(strip_b, fade_duration)
        #apply_volume_fade(strip_a, overlap_start, overlap_end, 1.0, 0.0)
        #apply_volume_fade(strip_b, overlap_start, overlap_end, 0.0, 1.0)
    
        print(f"Crossfade applied: {strip_a.name} -> {strip_b.name}")

        # 処理内容
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(SEQUENCER_OT_auto_sound_crossfade.bl_idname)

def register():
    bpy.utils.register_class(SEQUENCER_OT_auto_sound_crossfade)
    bpy.types.SEQUENCER_MT_strip.append(menu_func)

def unregister():
    bpy.types.SEQUENCER_MT_strip.remove(menu_func)
    bpy.utils.unregister_class(SEQUENCER_OT_auto_sound_crossfade)

