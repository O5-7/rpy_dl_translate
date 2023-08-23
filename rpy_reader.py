import os
import time
from tqdm import tqdm
import re
from datetime import datetime


class rpy_file:
    def __init__(self, rpy_path: str):
        self.seq_dict = {}
        r_file = open(rpy_path, mode='r', encoding='utf-8')
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

    def remove_font_flag(self, seq: str):
        seq = seq.replace('{i}', '').replace('{/i}', '')
        seq = seq.replace('{b}', '').replace('{/b}', '')
        seq = seq.replace('{s}', '').replace('{/s}', '')
        seq = re.sub(r'{size=[-+]?\d+}', '', seq).replace('{/size}', '')
        return seq

    def write_rpy_file(self, file_path: str):
        if self.seq_dict.__len__() == 0: return
        w_file = open(file_path, mode='w', encoding='utf-8')
        w_file.write('# TODO: Translation updated at ' + datetime.now().now().strftime('%Y-%m-%d %H:%M') + '\n')
        w_file.write('# translated by python script, using dl-translate\n')
        w_file.write('# model: mbart-large-50-one-to-many-mmt\n')
        w_file.write('# github: NAN\n\n\n')
        for k, v in self.seq_dict.items():
            w_file.write('translate chinese_dl ' + k + ':\n')
            w_file.write('    # ' + v[1] + ' "' + v[2] + '"\n')
            w_file.write('    ' + v[1] + ' "' + 'test test test' + '"\n\n')
            # w_file.write('    ' + v[1] + ' "' + v[3] + '"\n\n')
        w_file.close()


if __name__ == '__main__':
    t = rpy_file('./MayaEvents_tl.rpy')
    t.write_rpy_file('./test.rpy')
    print(1)
