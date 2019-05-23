import ffmpeg, re, os
import os.path as path


if __name__ == "__main__":
    clip_dir = path.relpath("..\\tripartito\\clips")
    clip = path.join(clip_dir, 'set01\\monster_S01E01_SQ0010_SH0010_V001.mp4')
    output = path.join(clip_dir, 'shrinkydink.mp4')

    (
        ffmpeg
            .input(clip)
            .filter('scale', w=960, h=540)
            .output(output)
            .run()
    )