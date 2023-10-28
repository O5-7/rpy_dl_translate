from rpy_translate_manager import rpy_translate_manager

# MarianMT模型
# rm = rpy_translate_manager(r'E:\PycharmProjects\opus_fine_tune\model_save',
#                            'MarianMT',
#                            './replace.json',)

# mbart50模型
# rm = rpy_translate_manager(r'../mbart_fine_tune_for_lil/model_save',
#                            'mbart50',
#                            './replace.json', )

# chat_glm2模型
rm = rpy_translate_manager(r'../dl_models/chatglm2-6b-int4',
                           'chat_glm2',
                           './replace.json', )

rm.set_source_folder(r'./s_test_folder')
rm.set_result_folder(r'./r_test_folder')
rm.set_target_folder(r'./t_test_folder')

rm.scan_files()  # 扫描文件夹 读取文件
rm.transfer()  # 转移已翻译的内容
rm.quick_translate(64)  # 翻译
rm.translation_fix()  # 翻译修正
rm.write_translate_result(over_write=True)  # 保存文件
