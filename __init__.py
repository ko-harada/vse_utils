bl_info = {
    "name": "VSE Utilities",
    "author": "Ko Harada",
    "version": (1, 0),
    "blender": (4, 5, 0),
    "location": "Sequencer > Strip Menu",
    "description": "Provides several utilities for the Video Sequence Editor",
    "category": "Sequencer",
}

import importlib
from . import trim_strips, sound_crossfade


modules = [trim_strips, sound_crossfade]


def register():
    for m in modules:
        importlib.reload(m)  # 開発中のホットリロード用
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()

