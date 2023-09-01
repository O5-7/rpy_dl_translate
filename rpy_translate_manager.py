import os
from tqdm import tqdm
from rpy_file import rpy_file
import dl_translate as dlt
from translate_string import translate_string
# TODO: 还原角色名
# TODO: 还原替换字符


class rpy_translate_manager:
    def __init__(self, model_or_path: str = '', model_family: str = 'mbart50', device: str = "auto"):
        self.model_or_path = model_or_path
        self.model_family = model_family
        self.device = device
        self.mt: dlt.TranslationModel = None

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

    def quick_translate(self):
        """
        对未翻译的进行翻译

        未载入时会载入模型

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
            self.target_files_dict[file_name].translate(self.mt)
        return

    def full_translate(self):
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
                    translate_result = self.mt.translate(v.origin, source=dlt.lang.ENGLISH, target=dlt.lang.CHINESE)
                    v.type = 'DL_translation'
                    v.translate = translate_result
                    self.target_files_dict[file_name].update({k, v})
        return

    def set_mt(self, mt_: dlt.TranslationModel):
        """
        手动设置dlt.TranslationModel对象

        :param mt_: TranslationModel
        :return: None
        """

        self.mt = mt_

    def write_translate_result(self):
        """
        将内存中的文件写到指定的文件夹中

        :return: None
        """
        for file_name in self.target_files_names:
            result_file_path = os.path.join(self.result_folder, file_name)
            self.target_files_dict[file_name].write_rpy_file(result_file_path, self.mt.model_family if self.mt is not None else 'None')

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

        rm.scan_files()
        rm.transfer()
        rm.quick_translate()
        rm.write_translate_result()


if __name__ == '__main__':
    rm = rpy_translate_manager(r'E:\PycharmProjects\dl_models\mbart-large-50-one-to-many-mmt')
    rm.set_source_folder('./s_test_folder')
    rm.set_target_folder('./t_test_folder')
    rm.set_result_folder('./r_test_folder')
    rm.scan_files()
    rm.transfer()
    # rm.quick_translate()
    rm.write_translate_result()
