import ffmpeg, re, os
import os.path as path

vid_dir = path.relpath(
    "..\\tripartito\\clips"
)

# vid_dir = path.abspath(
#     "Z:\\Cloud\\Dropbox (BigBangBoxSL)\\PROYECTOS\\"
#     "My preschool monster serie\\PRODUCCION\\Editorial\\"
#     "Dev\\tripartito\\clips"
# )

output = path.join(vid_dir, 'test.mp4')

def pad_zero(num, pad):
    num = str(num)
    while len(num) < pad:
        num = "0" + num
    return num


def create_shot_string(shot):
    return  f'monster_S{shot["season"]}E{shot["episode"]}_SQ{shot["sequence"]}_SH{shot["shot"]}'


def breakdown_name(dir):
    dir_list = os.listdir(dir)
    shots = []
    for vid in dir_list:
        if os.path.isdir(vid):
            continue

        se = re.search(r'S\d{2}E\d{2}', vid, re.IGNORECASE)
        sq = re.search(r'SQ\d{4}', vid, re.IGNORECASE)
        sh = re.search(r'SH\d{4}', vid, re.IGNORECASE)
        ver = re.search(r'V\d{3}', vid, re.IGNORECASE)
        
        if not se or not sq or not sh:
            continue
        
        pcs = {
            "ext": vid.split(".")[len(vid.split("."))-1],
            "season": vid[se.start(0)+1:se.start(0)+3],
            "episode": vid[se.start(0)+4:se.start(0)+6],
            "sequence": vid[sq.start(0)+2:sq.start(0)+6],
            "shot": vid[sh.start(0)+2:sh.start(0)+6],
        }

        if ver:
            pcs["version"] = vid[ver.start(0)+1:ver.end(0)]

        shots.append(pcs)
    
    return shots


def find_ult_ver(dir_list):
    latest_ver = {}
    for item in dir_list:
        if "season" not in item:
            continue
        key = create_shot_string(item)
        if key not in latest_ver:
            latest_ver[key] = {
                "version": item["version"],
                "extension": item["ext"]
            }
        elif int(item["version"]) > int(latest_ver[key]["version"]):
            latest_ver[key]["version"] = item["version"]
            latest_ver[key]["extension"] = item["ext"]
        else:
            continue    

    return latest_ver


def create_file_list(ver_dict):
    shot_list = []
    for key, value in ver_dict.items():
        ver = pad_zero(value["version"], 3)
        ext = value["extension"]
        shot_list.append(
            f'{key}_V{ver}.{ext}'
        )
    return shot_list


def create_concat_stream(shot_list):
    input_list = []
    for shot in shot_list:
        shot_path = path.join(vid_dir, shot)
        input_list.append(ffmpeg.input(shot_path))
    return ffmpeg.concat(*input_list)

concat_stream = (
    create_concat_stream(
    create_file_list(
    find_ult_ver(
    breakdown_name(
    vid_dir    
)))))

(
    concat_stream
    .output(output)
    .run()
)


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
