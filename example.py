from rpy_translate_manager import rpy_translate_manager

rm = rpy_translate_manager(r'E:\PycharmProjects\dl_models\mbart-large-50-one-to-many-mmt')
rm.scan_files()
rm.transfer()
rm.quick_translate()
rm.write_translate_result()
