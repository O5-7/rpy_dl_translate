from rpy_translate_manager import rpy_translate_manager

rm = rpy_translate_manager(r'E:\PycharmProjects\opus_fine_tune\model_save',
                           'MarianMT',
                           './replace.json',)

rm.set_source_folder(r'./s_test_folder')
rm.set_result_folder(r'./r_test_folder')
rm.set_target_folder(r'./t_test_folder')


rm.scan_files()  # 扫描文件夹 读取文件
rm.transfer()  # 转移已翻译的内容
rm.quick_translate(64, cover=True)  # 翻译
# rm.translation_fix()  # 翻译修正
rm.write_translate_result(over_write=True)  # 保存文件
