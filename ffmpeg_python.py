import ffmpeg, re, os
import os.path as path

def latest_layout(xport_path):
    xport_dir = os.listdir(xport_path)
    xport_list = []
    for xport in xport_dir:
        _ver = re.search(r'v\d{1}', xport, re.IGNORECASE)
        if _ver:
            ver_start = _ver.end(0)-1
            ver = ""
            idx = 0
            while str.isdigit(xport[ver_start + idx]):                
                ver += xport[ver_start + idx]
                idx += 1
            ver = int(ver)
        else:
            ver = 1
        xport_list.append({'name': xport, 'ver': ver})
    latest_ver = (
        sorted(
            list(map(lambda x: x['ver'], xport_list)),
            reverse=True
        )[0]
    )
    return list(filter(
        lambda x: x['ver'] == latest_ver, xport_list
    ))[0]['name']
    


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

    def build_canvas(self):
        return self.pad_vid(1728,720,0,0)

    def create_audio_streams(self):
        for key in self.shot_dict:
            self.shot_dict[key]['audio'] = (
                self.shot_dict[key]['stream']['a']
            )
        return self

    def create_overlay(self, super_stream, x_pos, y_pos):
        for key in self.shot_dict:
            self.shot_dict[key]['stream'] = (
                self.shot_dict[key]['stream']
                .overlay(super_stream, x_pos, y_pos)
            )
        return self
       
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
            "stream": ffmpeg.input(path.join(self.dir, shot))
        }

    def fill_gaps(self, ref_obj):
        _dict = self.shot_dict
        ref_dict = ref_obj.shot_dict
        for key in ref_dict:
            if key not in self.shot_dict:
                missing_dict = ref_dict[key]
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
                _dict[key] = fill_dict

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

    def pad_vid(self, width, height, x_pos, y_pos):
        for key in self.shot_dict:
            self.shot_dict[key]['stream'] = (
                self.shot_dict[key]['stream'].filter(
                    'pad',
                    w=width,
                    h=height,
                    x=x_pos,
                    y=y_pos
                )
            )
        return self
    
    def scale_animation(self):
        return self.scale_vid(1152, 648)
    
    def scale_vid(self, width, height):
        for key in self.shot_dict:
            self.shot_dict[key]['stream'] = (
                self.shot_dict[key]['stream'].filter(
                    'scale',
                    w=width,
                    h=height
                )
            )
        return self
        
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

    def trim_keys(self, ref):
        dict_keys = self.shot_dict.keys()
        ref_shots = self.key_shot_num(ref.shot_dict.keys())
        first_shot = ref_shots[0]
        ult_shot = ref_shots[len(ref_shots)-1]
        head_keys = []
        tail_keys = []
        body_keys = []
        for i, key in enumerate(dict_keys):
            curr_shot = self.key_shot_num(dict_keys)[i]
            if curr_shot < first_shot:
                head_keys.append(key)
            elif curr_shot > ult_shot:
                tail_keys.append(key)
            else:
                body_keys.append(key)
        return {'head': head_keys, 'tail': tail_keys, 'body': body_keys}
    
    def trim_points(self, keys):
        in_pt = 0
        body_dur = 0
        for key in keys['head']:
            in_pt += float(
                self.shot_dict[key]['specs']
                ['streams'][0]['duration']
            )
        for key in keys['body']:
            body_dur += float(
                self.shot_dict[key]['specs']
                ['streams'][0]['duration']
            )
        return {'in': in_pt, 'out': in_pt + body_dur}
        
        
    def file_list(self):
        return self.latest_list("filename")

    def stream_list(self):
        return self.latest_list("stream")

    def audio_list(self):
        return self.latest_list('audio')
    
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
    layout_dir = path.abspath("E:\\Dropbox (BigBangBoxSL)\\PROYECTOS\\My preschool monster serie\\PRODUCCION\\Layout\\Episodios\\EP15\\xport")

    font = path.relpath(".\\fonts\\ProximaNova-Regular.otf")

    output = path.join(clip_dir, 'trifecta.mp4')

    layout = path.join(layout_dir, latest_layout(layout_dir))
    
    animation_bin = Bin(animation_dir)
    animatic_bin = (
        Bin(animatic_dir)
        .trim_excess(animation_bin)
        .scale_vid(576,324)
    )
    audio_bin = (
        Bin(animatic_dir)
        .trim_excess(animation_bin)
        .create_audio_streams()
        .audio_list()
    )


    animation_bin = (
        animation_bin
        .fill_gaps(animatic_bin)
        .set_stream_specs()
        .scale_animation()
        .pad_vid(1728,720,0,0)
        .stream_list()
    )

    animatic_bin = (
        animatic_bin
        .stream_list()
    )

    animatic_stream = ffmpeg.concat(*animatic_bin, v=1, a=0)


    pic_ref = Bin(animatic_dir)
    excess_shots = pic_ref.trim_keys(Bin(animation_dir))
    trim = (
        pic_ref
        .set_stream_specs()
        .trim_points(excess_shots)
    )
    layout_stream = (
        ffmpeg
        .input(layout)
        .filter('crop', w=1257, h=707, x=6, y=186)
        .filter('scale', w=576, h=324)
        .trim(start=trim['in'], end=trim['out'])
        .filter('setpts', 0)
    )

    animation_stream = (
        ffmpeg
        .concat(*animation_bin, v=1, a=0)
        .overlay(animatic_stream, x=1152, y=0)
    )

    combo_stream = (
        animation_stream
        .overlay(layout_stream, x=1152, y=325)
    )
    
    audio_stream = ffmpeg.concat(*audio_bin, v=0, a=1)
    vid_stream = combo_stream
    
    out = ffmpeg.output(vid_stream, audio_stream, output)
    out.run()
