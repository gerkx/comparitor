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

class Bin:

    def __init__(self, dir):
        self.dir = dir
        self.dir_list = os.listdir(self.dir)
        self.shot_dict = self.latest_ver_dict()
        

    @staticmethod
    def extract_shot_components(shot):
        se = re.search(r'S\d{2}E\d{2}', shot, re.IGNORECASE)
        sq = re.search(r'SQ\d{4}', shot, re.IGNORECASE)
        sh = re.search(r'SH\d{4}', shot, re.IGNORECASE)
        _ver = re.search(r'v\d{1}', shot, re.IGNORECASE)



        if _ver:
            ver_start = shot[_ver.end(0)]
            ver = ver_start
            idx = 0
            # while str.isdigit(shot[ver_start + idx]):
            #     ver += shot[ver_start + idx]
            #     idx += 1
            # ver = int(ver)
        else:
            ver = 1

        if not se or not sq or not sh:
            return
     
        else:
            return {
                "season": shot[se.start(0)+1:se.start(0)+3],
                "episode": shot[se.start(0)+4:se.start(0)+6],
                "sequence": shot[sq.start(0)+2:sq.start(0)+6],
                "shot": shot[sh.start(0)+2:sh.start(0)+6],
                "ver": ver
            }

    
    def latest_ver_dict(self):
        _dir = self.dir_list
        _dict = {}
        for shot in _dir:
            shot_dict = self.extract_shot_components(shot)
            shot_key = f'{shot_dict["season"]}_{shot_dict["episode"]}_{shot_dict["shot"]}'
            if not shot_key in _dict:
                _dict[shot_key] = shot_dict
            if shot_dict["ver"] > _dict[shot_key]["ver"]:
                _dict[shot_key]["ver"] = shot_dict["ver"]
        return _dict


    # class Shot:

    #     # stream = None

    #     def __init__(self, sea, epi, seq, shot, ver=None):
    #         self.sea = sea
    #         self.epi = epi
    #         self.seq = seq
    #         self.shot = shot
    #         if ver:
    #             self.ver = ver
    #         else:
    #             self.ver = 1

    #     @classmethod
    #     def from_shot_dict(cls, shot_dict):
    #         sea = shot_dict["season"]
    #         epi = shot_dict["episode"]
    #         seq = shot_dict["sequence"]
    #         shot = shot_dict["shot"]
    #         ver = shot_dict["ver"]

    #         return cls(sea, epi, seq, shot, ver)


bin = Bin(vid_dir)
# list = bin.latest_shot_ver()

print(bin.shot_dict)



    


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

# concat_stream = (
#     create_concat_stream(
#     create_file_list(
#     find_ult_ver(
#     breakdown_name(
#     vid_dir    
# )))))

# (
#     concat_stream
#     .output(output)
#     .run()
# )


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
