import os
import re
import dl_translate as dlt
from datetime import datetime
from translate_string import translate_string
import torch
import json


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
        translate_type = ''
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
                if line.startswith('# type:'):
                    translate_type = line[7:-1]
                continue
            if line.startswith('translate'):
                # 找到句子标记
                translate_type = ''
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
                if translate_type == '' and translate.__len__() > 0:
                    translate_type = "Human_translation"
                self.seq_dict.update(
                    {
                        seq_hash: translate_string(
                            translate.__len__() > 0,
                            translate_type,
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

    def write_rpy_file(self, file_path: str, model_name: str = 'mbart-large-50-one-to-many-mmt', over_write: bool = False):
        """
        将文件对象写到指定的位置

        可指定使用的模型名字

        :param over_write: 是否覆写文件
        :param file_path: 指定的文件位置及文件名
        :param model_name: 模型名字
        :return: None
        """
        if os.path.exists(file_path) and not over_write:
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
            w_file.write('    # type:' + v.type + '\n')
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

    def translate_strs_with_batch(self, origins, mt: dlt.TranslationModel):
        """
        批量翻译 针对显存溢出优化

        :param origins: 字符串list
        :param mt: 模型
        :return: 翻译结果list
        """
        split_translate = False
        try:
            translate_results = mt.translate(origins, source=dlt.lang.ENGLISH, target=dlt.lang.CHINESE)
        except torch.cuda.OutOfMemoryError:
            # mbaet50模型在批量翻译时可能会导致某句出现超长导致显存溢出
            # 改为逐条翻译
            split_translate = True
            translate_results = []
        finally:
            pass
        if split_translate:
            for single in origins:
                result = mt.translate(single, source=dlt.lang.ENGLISH, target=dlt.lang.CHINESE)
                translate_results.append(result)
                result = ''
        return translate_results

    def translate_with_batch(self, mt: dlt.TranslationModel, batch_size: int = 64):
        """
        管理批量翻译 调整batch_size,每次翻译batch_size条句子

        ps: 8GB显存下, 推荐batch_size=64

        :param mt: 指定的模型,由调用者提供
        :param batch_size: batch-size
        :return: None
        """
        batch_ready_to_translate = {}
        ready_size = 0
        for k, v in self.seq_dict.items():
            v: translate_string
            v.type = "DL_translation"
            if not v.is_translated:
                batch_ready_to_translate.update({k: v.origin})
                print('translate: {}'.format(k))
                ready_size += 1
            if ready_size == batch_size:
                origins = list(batch_ready_to_translate.values())
                translate_results = self.translate_strs_with_batch(origins, mt)
                for i in range(ready_size):
                    batch_keys = list(batch_ready_to_translate.keys())
                    self.seq_dict[batch_keys[i]].translate = translate_results[i]
                batch_ready_to_translate.clear()
                batch_ready_to_translate = {}
                ready_size = 0
        origins = list(batch_ready_to_translate.values())
        translate_results = self.translate_strs_with_batch(origins, mt)
        for i in range(ready_size):
            batch_keys = list(batch_ready_to_translate.keys())
            self.seq_dict[batch_keys[i]].translate = translate_results[i]

    def translation_fix(self, replace_dict: dict):
        """
        根据提供的翻译替换json文件进行翻译替换

        :param replace_dict: 翻译替换字典
        :return: None
        """
        for k, v in self.seq_dict.items():
            # 对于所有翻译
            if v.type == 'DL_translation':
                v: translate_string
                for name_k, name_v in replace_dict.items():
                    # 对于所有角色名
                    if v.origin.find(name_k) != -1:
                        for ai_name in name_v:
                            # 对于所有可能的ai翻译角色名 进行替换
                            v.translate = v.translate.replace(ai_name, name_k)
