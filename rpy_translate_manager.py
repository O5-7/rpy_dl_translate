import os
from tqdm import tqdm
from rpy_file import rpy_file
import dl_translate as dlt
from translate_string import translate_string
import json
from MarianMTModel_fine_tune import MarianMTModel_fine_tune
from chat_glm2_LIL import chat_glm2_LIL
import warnings
from baidu_translate import baidu_translate


class rpy_translate_manager:
    def __init__(self, model_or_path: str = '', model_family: str = 'mbart50', replace_json_path: str = './replace.json', device: str = "auto"):
        """
        rpy翻译器管理类
        :param model_or_path: 本地模型地址
        :param model_family: 模型名称 mbart50 MarianMT chatglm2
        :param replace_json_path: 替换json路径
        :param device: 设备
        """
        self.model_or_path = model_or_path
        self.model_family = model_family
        self.device = device
        self.mt = None

        self.replace_json_path = replace_json_path

        self.source_folder = ''
        self.target_folder = ''
        self.result_folder = ''

        self.source_files_names = []
        self.target_files_names = []
        self.matching_files = []

        self.source_files_dict = dict()
        self.target_files_dict = dict()

        return

    def scan_files(self):
        """
         扫描指定文件夹 加载到字典中

        :return: None
        """
        s_files_names = os.listdir(self.source_folder)
        t_files_names = os.listdir(self.target_folder)
        self.source_files_names = [i for i in s_files_names if i.endswith('.rpy')]
        self.target_files_names = [i for i in t_files_names if i.endswith('.rpy')]

        self.matching_files = list(set(s_files_names) & set(t_files_names))
        # print(self.matching_files)
        for file_name in tqdm(self.matching_files, ncols=120):
            s_file_path = os.path.join(self.source_folder, file_name)
            self.source_files_dict.update({file_name: rpy_file(s_file_path)})

        for file_name in tqdm(t_files_names, ncols=120):
            t_file_path = os.path.join(self.target_folder, file_name)
            self.target_files_dict.update({file_name: rpy_file(t_file_path)})

    def transfer(self):
        """
        将已翻译的内容覆盖到要翻译的文件

        :return: None
        """
        for file_name in tqdm(self.matching_files):
            self.target_files_dict[file_name].update(self.source_files_dict[file_name])

    def quick_translate(self, batch_size: int = 64, cover: bool = False):
        """
        对未翻译的进行翻译

        未载入时会载入模型

        :return: None
        """
        if self.mt is None:
            print('加载模型中...')
            if self.model_family not in ['mbart50', 'MarianMT', 'chat_glm2']:
                print('模型名错误!')
                exit(0)
            if self.model_family == 'chat_glm2':
                self.mt = chat_glm2_LIL(
                    model_or_path=self.model_or_path,
                    device=self.device
                )
            if self.model_family == 'mbart50':
                self.mt = dlt.TranslationModel(
                    model_or_path=self.model_or_path,
                    model_family=self.model_family,
                    device=self.device
                )
            if self.model_family == 'MarianMT':
                self.mt = MarianMTModel_fine_tune(
                    model_or_path=self.model_or_path,
                    device=self.device
                )
            print('模型加载成功:{}'.format(self.model_family))
        for file_name in self.target_files_names:
            # self.target_files_dict[file_name].translate(self.mt)
            self.target_files_dict[file_name].translate_with_batch(self.mt, cover, batch_size)
        return

    def full_translate(self):
        warnings.warn("废弃, 不再维护", DeprecationWarning)
        """
        全翻译, 忽略未翻译的和人工翻译的

        :return: None
        """
        if self.mt is None:
            print('加载模型中...')
            self.mt = dlt.TranslationModel(
                model_or_path=self.model_or_path,
                model_family=self.model_family,
                device=self.device
            )
            print('模型加载成功:{}'.format(self.model_family))
            for file_name in self.target_files_names:
                for k, v in self.target_files_dict[file_name].seq_dict.items():
                    v: translate_string
                    translate_result = self.mt.translate(v.origin_flag, source=dlt.lang.ENGLISH, target=dlt.lang.CHINESE)
                    v.type = 'DL_translation'
                    v.translate = translate_result
                    self.target_files_dict[file_name].update({k, v})
        return

    def translation_fix(self):
        """
        根据提供的翻译替换json文件进行翻译替换

        :return: None
        """
        if not os.path.exists(self.replace_json_path) and self.replace_json_path.endswith('.json'):
            return
        with open(self.replace_json_path, encoding='utf-8') as file_p:
            replace_dict = json.load(file_p)
            for file_name in tqdm(self.target_files_names, ncols=120):
                self.target_files_dict[file_name].translation_fix(replace_dict)

    def set_mt(self, mt_: dlt.TranslationModel):
        """
        手动设置dlt.TranslationModel对象

        :param mt_: TranslationModel
        :return: None
        """

        self.mt = mt_

    def write_translate_result(self, over_write: bool = False):
        """
        将内存中的文件写到指定的文件夹中

        :return: None
        """
        for file_name in self.target_files_names:
            result_file_path = os.path.join(self.result_folder, file_name)
            self.target_files_dict[file_name].write_rpy_file(result_file_path, self.mt.model_family if self.mt is not None else 'None', over_write=over_write)

    def set_source_folder(self, s_f):
        if os.path.isdir(s_f):
            self.source_folder = s_f

    def set_target_folder(self, t_f):
        if os.path.isdir(t_f):
            self.target_folder = t_f

    def set_result_folder(self, r_f):
        if not os.path.isdir(r_f):
            os.makedirs(r_f)
            print('已创建文件夹' + r_f)
        self.result_folder = r_f

    def STQW(self):
        """
        快速实现扫描,迁移,翻译,写文件

        :return: None
        """

        self.scan_files()
        self.transfer()
        self.quick_translate()
        self.write_translate_result()

    def baidu_translate(self, app_id, appkey):
        mt = baidu_translate(app_id, appkey)
