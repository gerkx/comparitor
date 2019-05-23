import ffmpeg, re, os
import os.path as path


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

    def extract_shot_components(self, shot):
        se = re.search(r'S\d{2}E\d{2}', shot, re.IGNORECASE)
        sq = re.search(r'SQ\d{4}', shot, re.IGNORECASE)
        sh = re.search(r'SH\d{4}', shot, re.IGNORECASE)
        _ver = re.search(r'v\d{1}', shot, re.IGNORECASE)

        if not se or not sq or not sh:
            return None

        if _ver:
            ver_start = _ver.end(0)-1
            ver = ""
            idx = 0
            while str.isdigit(shot[ver_start + idx]):                
                ver += shot[ver_start + idx]
                idx += 1
            ver = int(ver)
        else:
            ver = 1
    
        return {
            "season": shot[se.start(0)+1:se.start(0)+3],
            "episode": shot[se.start(0)+4:se.start(0)+6],
            "sequence": shot[sq.start(0)+2:sq.start(0)+6],
            "shot": shot[sh.start(0)+2:sh.start(0)+6],
            "ver": ver,
            "filename": path.join(self.dir, shot),
            "stream": ffmpeg.input(path.join(self.dir, shot)).filter("scale", size="hd1080"),
        }

    def fill_gaps(self, ref_obj):
        _dict = self.shot_dict
        ref_dict = ref_obj.shot_dict
        for key in ref_dict:
            if key not in self.shot_dict:
                missing_dict = ref_dict[key]
                # print(missing_dict.keys())
                # missing_shot = ffmpeg.probe(
                #     missing_dict["filename"])["streams"][0]
                # dur = missing_shot["duration"]
                # width = missing_shot["width"]
                # height = missing_shot["height"]
                # filler = ffmpeg.input(slug, t=dur)
                fill_dict = {
                    "season": missing_dict["season"],
                    "episode": missing_dict["episode"],
                    "sequence": missing_dict["sequence"],
                    "shot": missing_dict["shot"],
                    "ver": 0,
                    "filename": missing_dict["filename"],
                    "stream": ffmpeg.input(missing_dict["filename"])
                        .filter("scale", size="hd1080")
                        .drawbox(0,0,1920,1080, color="black@.9", thickness=1920)
                        .drawtext(text="Plano Pendiente", fontcolor="white@.35", x=720, y=540, fontsize=64, fontfile=font)
                }
                # fill_dict["stream"]
                # print(fill_dict["stream"])
                _dict[key] = fill_dict
                # print(ref_dict[key]["stream"])
                # print("==============================")
                # print(_dict[key]["stream"])

        
        
        
        sorted_dict = {}
        for key in sorted(_dict.keys()):
            sorted_dict[key] = _dict[key]
        self.shot_dict = sorted_dict
        return self

    def latest_list(self, key):
        _dict = self.shot_dict
        _list = []
        for dict_key in _dict:
            _list.append(_dict[dict_key][key])
        return _list
    
    def latest_ver_dict(self):
        _dir = self.dir_list
        _dict = {}
        for shot in _dir:
            shot_dict = self.extract_shot_components(shot)
            if not shot_dict:
                continue
            shot_key = f'{shot_dict["season"]}_{shot_dict["episode"]}_{shot_dict["shot"]}'
            if not shot_key in _dict:
                _dict[shot_key] = shot_dict
            if shot_dict["ver"] > _dict[shot_key]["ver"]:
                _dict[shot_key].update(shot_dict)        
        return _dict
    
    def set_stream_specs(self):
        for key in self.shot_dict:
            self.shot_dict[key]["specs"] = ffmpeg.probe(
                self.shot_dict[key]["filename"]
                )
        return self

    def trim_excess(self, ref):
        dict_keys = self.shot_dict.keys()
        ref_shots = self.key_shot_num(ref.shot_dict.keys())
        first_shot = ref_shots[0]
        ult_shot = ref_shots[len(ref_shots)-1]
        excess_keys = []
        for i, key in enumerate(dict_keys):
            curr_shot = self.key_shot_num(dict_keys)[i]
            if curr_shot < first_shot or curr_shot > ult_shot:
                excess_keys.append(key)
        for key in excess_keys:
            self.shot_dict.pop(key)
        return self

    def file_list(self):
        return self.latest_list("filename")

    def stream_list(self):
        return self.latest_list("stream")
    
    @staticmethod
    def key_shot_num(key_list):
        shots = []
        for key in key_list:
            shots.append(int(key.split("_")[2]))

        return sorted(shots)


'''
Testing implementations below
'''
if __name__ == "__main__":
    clip_dir = path.relpath("..\\tripartito\\clips")

    animatic_dir = path.join(clip_dir, "animatic")
    animation_dir = path.join(clip_dir, "animation")

    font = path.relpath(".\\fonts\\ProximaNova-Regular.otf")

    output = path.join(clip_dir, 'boop.mp4')

    slug = path.relpath(".\\img\\slug.mp4")

    animation_bin = Bin(animation_dir)
    animatic_bin = (
        Bin(animatic_dir)
        .trim_excess(animation_bin)
    )

    animation_bin = (
        animation_bin
        .fill_gaps(animatic_bin)
        .set_stream_specs()
        .stream_list()
    )

    animatic_bin = animatic_bin.stream_list()

    print("animatic list:  ", animatic_bin)
    print("=========================")
    print("animation list: ", animation_bin)

    ffmpeg.concat(*animation_bin).output(output).run()

# ffmpeg.input(slug, t="30", s="1920x1080").output(output).run()
# test = ffmpeg.input(slug, t=2).filter("scale", 640, 360).output(output).run()

# ffmpeg.input(color="blue", width=640, t=20).output(output).run()


# def create_shot_string(shot):
#     return  f'monster_S{shot["season"]}E{shot["episode"]}_SQ{shot["sequence"]}_SH{shot["shot"]}'


# def breakdown_name(dir):
#     dir_list = os.listdir(dir)
#     shots = []
#     for vid in dir_list:
#         if os.path.isdir(vid):
#             continue

#         se = re.search(r'S\d{2}E\d{2}', vid, re.IGNORECASE)
#         sq = re.search(r'SQ\d{4}', vid, re.IGNORECASE)
#         sh = re.search(r'SH\d{4}', vid, re.IGNORECASE)
#         ver = re.search(r'V\d{3}', vid, re.IGNORECASE)
        
#         if not se or not sq or not sh:
#             continue
        
#         pcs = {
#             "ext": vid.split(".")[len(vid.split("."))-1],
#             "season": vid[se.start(0)+1:se.start(0)+3],
#             "episode": vid[se.start(0)+4:se.start(0)+6],
#             "sequence": vid[sq.start(0)+2:sq.start(0)+6],
#             "shot": vid[sh.start(0)+2:sh.start(0)+6],
#             "filename": vid
#         }

#         if ver:
#             pcs["version"] = vid[ver.start(0)+1:ver.end(0)]

#         shots.append(pcs)
    
#     return shots


# def find_ult_ver(dir_list):
#     latest_ver = {}
#     for item in dir_list:
#         if "season" not in item:
#             continue
#         key = create_shot_string(item)
#         if key not in latest_ver:
#             latest_ver[key] = {
#                 "version": item["version"],
#                 "extension": item["ext"]
#             }
#         elif int(item["version"]) > int(latest_ver[key]["version"]):
#             latest_ver[key]["version"] = item["version"]
#             latest_ver[key]["extension"] = item["ext"]
#         else:
#             continue    

#     return latest_ver


# def create_file_list(ver_dict):
#     shot_list = []
#     for key, value in ver_dict.items():
#         ver = pad_zero(value["version"], 3)
#         ext = value["extension"]
#         shot_list.append(
#             f'{key}_V{ver}.{ext}'
#         )
#     return shot_list


# def create_concat_stream(shot_list):
#     input_list = []
#     for shot in shot_list:
#         shot_path = path.join(vid_dir01, shot)
#         input_list.append(ffmpeg.input(shot_path))
#     return ffmpeg.concat(*input_list)

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
