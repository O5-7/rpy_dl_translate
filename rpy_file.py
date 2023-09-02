import os
import re
import dl_translate as dlt
from datetime import datetime
from translate_string import translate_string


class rpy_file:
    def __init__(self, rpy_path: str):
        self.seq_dict = {}
        self.read_rpy_file(rpy_path)

    def remove_font_flag(self, seq: str):
        """
        移除字体格式标志

        包括斜体,加粗,字体大小等

        :param seq: 源字符串
        :return: 处理后的字符串
        """
        seq = seq.replace('{i}', '').replace('{/i}', '')
        seq = seq.replace('{b}', '').replace('{/b}', '')
        seq = seq.replace('{s}', '').replace('{/s}', '')
        seq = re.sub(r'{size=[-+]?\d+}', '', seq).replace('{/size}', '')
        return seq

    def read_rpy_file(self, file_path: str):
        """
        读取rpy文件, 加载到字典中

        只会读取translate开头的台词语句

        记录了原文,处理后的原文,翻译后结果

        :param file_path:
        :return:
        """

        # print(file_path + ' load')
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
                self.seq_dict.update(
                    {
                        seq_hash: translate_string(
                            translate.__len__() > 0,
                            'Human_translation',
                            speaker,
                            origin_raw,
                            origin,
                            translate)
                    })
                # self.seq_dict.update({seq_hash: [translate.__len__() > 0,
                #                                  speaker,
                #                                  origin_raw,
                #                                  origin,
                #                                  translate]})
                # print(seq_hash)
                # print(origin)
                # print(translate)
                # print('========================================')
                continue
        r_file.close()

    def write_rpy_file(self, file_path: str, model_name: str = 'mbart-large-50-one-to-many-mmt'):
        """
        将文件对象写到指定的位置

        可指定使用的模型名字

        :param file_path: 指定的文件位置及文件名
        :param model_name: 模型名字
        :return: None
        """
        if os.path.exists(file_path):
            print('文件已存在!')
            return
        if self.seq_dict.__len__() == 0:
            print('{}空文件,未检测到要翻译的语句'.format(file_path))
        w_file = open(file_path, mode='w', encoding='utf-8')
        w_file.write('# Translation updated at ' + datetime.now().now().strftime('%Y-%m-%d %H:%M') + '\n')
        w_file.write('# translated by python script, using dl-translate\n')
        w_file.write('# model: {}\n'.format(model_name))
        w_file.write('# github: https://github.com/O5-7/rpy_dl_translate\n\n\n')
        if self.seq_dict.__len__() == 0:
            w_file.write('# 未检测到要翻译的语句,有需要请手动迁移\n')
            w_file.close()
            return
        for k, v in self.seq_dict.items():
            v: translate_string
            w_file.write('translate chinese_dl ' + k + ':\n')
            w_file.write('    # ' + v.speaker + ' "' + v.origin_raw + '"\n')
            # w_file.write('    # ' + v.type + '\n')
            # TODO: 有风险 未经测试 暂时不建议写入翻译类型
            # w_file.write('    ' + v[1] + ' "' + 'test test test' + '"\n\n')
            w_file.write('    ' + v.speaker + ' "' + v.translate + '"\n\n')
        w_file.close()

    def update(self, source_file: 'rpy_file', hard_cover: bool = False):
        """
        将另一个rpy_file对象中已翻译语句转移到此对象中

        :param source_file: 源文件对象
        :param hard_cover: TODO
        :return: None
        """

        for k, v in self.seq_dict.items():
            v: translate_string
            if v.is_translated:
                continue
            # 如果有空翻译 去源翻译寻找
            if k in source_file.seq_dict:
                self.seq_dict.update({k: source_file.seq_dict.get(k)})

    def translate(self, mt: dlt.TranslationModel):
        """
        翻译单个文件内的文本

        :param mt: 指定的模型,由调用者提供
        :return: None
        """

        for k, v in self.seq_dict.items():
            v: translate_string
            if not v.is_translated:
                translate_result = mt.translate(v.origin, source=dlt.lang.ENGLISH, target=dlt.lang.CHINESE)
                print('translate: {}'.format(k))
                v.translate = translate_result
                v.type = "DL_translation"
                self.seq_dict.update({k: v})

    def character_name_restore(self):
        # TODO: 将翻译后的角色名还原为原文
        return


if __name__ == '__main__':
    s_f = rpy_file('./test_s.rpy')
    d = rpy_file('./test_d.rpy')
    d.update(s_f)
    d.write_rpy_file('./test_r.rpy')
    print(1)
