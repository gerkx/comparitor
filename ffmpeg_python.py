import ffmpeg, re, os
import os.path as path
# import os.listdir as listdir

vid_dir = path.relpath(
    "..\\tripartito\\clips"
)
# vid_dir = path.abspath(
#     "Z:\\Cloud\\Dropbox (BigBangBoxSL)\\PROYECTOS\\"
#     "My preschool monster serie\\PRODUCCION\\Editorial\\"
#     "Dev\\tripartito\\clips"
# )

vid_list = os.listdir(vid_dir)

def pad_zero(num, pad):
    num = str(num)
    while len(num) < pad:
        num = "0" + num
    return num

def dir_dict(dir_list):
    shots = {}
    for vid in dir_list:
        se = re.search(r'S\d{2}E\d{2}', vid, re.IGNORECASE)
        sq = re.search(r'SQ\d{4}', vid, re.IGNORECASE)
        sh = re.search(r'SH\d{4}', vid, re.IGNORECASE)
        ver = re.search(r'V\d{3}', vid, re.IGNORECASE)
        
        if not se or not sq or not sh or not ver:
            continue
        
        show = vid.split("_")[0]
        ext = vid.split(".")[len(vid.split("."))-1]
        season= vid[se.start(0)+1:se.start(0)+3]
        episode = vid[se.start(0)+4:se.start(0)+6]
        sequence = vid[sq.start(0)+2:sq.start(0)+6]
        shot = vid[sh.start(0)+2:sh.start(0)+6] 
        version = int(vid[ver.start(0)+1:ver.end(0)])
        shot_string = f'S{season}E{episode}_SQ{sequence}_SH{shot}'
        
        if shot_string not in shots:
            shots[shot_string] = [version]
        else:
            shots[shot_string].append(version)
    
    return shots

def latest_ver(shot_dict):
    shot_vers = []
    for shot, ver in shot_dict.items():
        ult_ver = f'{shot}_V{pad_zero(sorted(ver)[len(ver)-1],3)}'
        shot_vers.append(ult_ver)


    
    return shot_vers



print(latest_ver(dir_dict(vid_list)))






# vid001 = ffmpeg.input(path.join(vid_dir, "Clip002_V002.mp4"))
# vid002 = (
#     ffmpeg
#     .input(path.join(vid_dir, "Clip002.mp4"))
#     .filter("scale", w=960, h=540)
#     )


# vid001_probe = ffmpeg.probe(vid001, cmd='ffprobe')

# print(vid001_probe)


# vid_out = path.join(vid_dir, "Concat_Clip.mp4")

# def vid_concat():
#     (
#         vid001
#         .filter("scale", w=960, h=540)
#         .filter("pad", w=1920)
#         .overlay(
#             vid002,
#             x=960
#         )
#         .output(vid_out)
#         .run()
#     )

# vid_concat()
