from rpy_translate_manager import rpy_translate_manager

rm = rpy_translate_manager(r'E:\PycharmProjects\dl_models\mbart-large-50-one-to-many-mmt',
                           './replace.json')

rm.set_source_folder(r'./s_test_folder')
rm.set_result_folder(r'./r_test_folder')
rm.set_target_folder(r'./t_test_folder')

rm.scan_files()  # 扫描文件夹 读取文件
rm.transfer()  # 转移已翻译的内容
rm.quick_translate(64)  # 翻译
# rm.full_translate()
rm.translation_fix()  # 翻译修正
rm.write_translate_result(over_write=True)  # 保存文件
