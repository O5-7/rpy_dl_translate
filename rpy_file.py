import os
import time
from tqdm import tqdm
import re
import dl_translate as dlt
from datetime import datetime


class rpy_file:
    def __init__(self, rpy_path: str):
        self.mt = None
        self.seq_dict = {}
        self.read_rpy_file(rpy_path)

    def remove_font_flag(self, seq: str):
        seq = seq.replace('{i}', '').replace('{/i}', '')
        seq = seq.replace('{b}', '').replace('{/b}', '')
        seq = seq.replace('{s}', '').replace('{/s}', '')
        seq = re.sub(r'{size=[-+]?\d+}', '', seq).replace('{/size}', '')
        return seq

    def read_rpy_file(self, file_path: str):
        self.seq_dict = {}
        r_file = open(file_path, mode='r', encoding='utf-8')
        seq_hash = ''
        speaker = ''
        origin = ''
        origin_raw = ''
        translate = ''
        for line in r_file.readlines():
            line = line.lstrip()
            if line == '' or line[0] == '#' or line == '\n':
                if line.find('"') != -1:
                    # 找到原句
                    seq_start = line.index('"')
                    speaker = line[2:seq_start - 1]
                    origin_raw = line[seq_start + 1: -2]
                    origin = self.remove_font_flag(origin_raw)
                continue
            if line.startswith('translate'):
                # 找到句子标记
                seq_hash = line[10:].split(' ')[1][:-2]
                continue
            if line.find('"') != -1:
                seq_start = line.index('"')
                if line.startswith('old'):
                    # 实际没啥用, 先保留
                    origin = self.remove_font_flag(line[seq_start + 1: -2])
                    continue
                translate = line[seq_start + 1:-2]
                if seq_hash == 'strings':
                    # 跳过strings, 不更新到dict
                    continue
                self.seq_dict.update({seq_hash: [translate.__len__() > 0,
                                                 speaker,
                                                 origin_raw,
                                                 origin,
                                                 translate]})
                # print(seq_hash)
                # print(origin)
                # print(translate)
                # print('========================================')
                continue
        r_file.close()

    def write_rpy_file(self, file_path: str):
        if os.path.exists(file_path):
            print('文件已存在,如需覆盖请手动覆盖')
            return
        if self.seq_dict.__len__() == 0: return
        w_file = open(file_path, mode='w', encoding='utf-8')
        w_file.write('# TODO: Translation updated at ' + datetime.now().now().strftime('%Y-%m-%d %H:%M') + '\n')
        w_file.write('# translated by python script, using dl-translate\n')
        w_file.write('# model: mbart-large-50-one-to-many-mmt\n')
        w_file.write('# github: https://github.com/O5-7/rpy_dl_translate\n\n\n')
        for k, v in self.seq_dict.items():
            w_file.write('translate chinese_dl ' + k + ':\n')
            w_file.write('    # ' + v[1] + ' "' + v[2] + '"\n')
            # w_file.write('    ' + v[1] + ' "' + 'test test test' + '"\n\n')
            w_file.write('    ' + v[1] + ' "' + v[4] + '"\n\n')
        w_file.close()

    def update(self, source_file: 'rpy_file', hard_cover: bool = False):
        for k, v in self.seq_dict.items():
            if v[0]:
                continue
            # 如果有空翻译 去源翻译寻找
            if k in source_file.seq_dict:
                self.seq_dict.update({k: source_file.seq_dict.get(k)})

    def translate(self, ):
        if self.mt is None:
            self.mt = dlt.TranslationModel(
                model_or_path=r'E:\PycharmProjects\dl_models\mbart-large-50-one-to-many-mmt',
                model_family='mbart50',
                device="gpu"
            )
        for k, v in self.seq_dict.items():
            if not k[0]:
                translate_result = self.mt.translate(v[3], source=dlt.lang.ENGLISH, target=dlt.lang.CHINESE)
                v[4] = translate_result
                self.seq_dict.update({k, v})


if __name__ == '__main__':
    s_f = rpy_file('./test_s.rpy')
    d = rpy_file('./test_d.rpy')
    d.update(s_f)
    d.write_rpy_file('./test_r.rpy')
    print(1)
