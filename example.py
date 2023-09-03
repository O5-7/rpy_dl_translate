from rpy_translate_manager import rpy_translate_manager

rm = rpy_translate_manager(r'E:\PycharmProjects\dl_models\mbart-large-50-one-to-many-mmt')

rm.set_source_folder(r'./s_test_folder')
rm.set_result_folder(r'./r_test_folder')
rm.set_target_folder(r'./t_test_folder')

rm.scan_files()
rm.transfer()
rm.quick_translate()
rm.write_translate_result()
