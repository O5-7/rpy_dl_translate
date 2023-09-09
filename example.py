from rpy_translate_manager import rpy_translate_manager
import json


rm = rpy_translate_manager(r'E:\PycharmProjects\dl_models\mbart-large-50-one-to-many-mmt', './replace.json')

rm.set_source_folder(r'./s_test_folder')
rm.set_result_folder(r'./r_test_folder')
rm.set_target_folder(r'./t_test_folder')

rm.scan_files()
rm.transfer()
# rm.quick_translate(64)
# rm.full_translate()
rm.translation_fix()
rm.write_translate_result(over_write=True)
#
# with open('./replace.json', encoding='utf-8') as replace_json_file:
#     replace_dict = json.load(replace_json_file)
#     print(replace_dict)
#     for k,v in replace_dict.items():
#         print(v)

