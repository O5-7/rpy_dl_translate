class translate_string:
    def __init__(self, is_translated, s_type, speaker, origin_raw, origin_escape, origin, translate):
        self.is_translated: bool = is_translated
        self.type: str = s_type
        # "DL_translation" ai翻译
        # "Human_Translation" 人工润色翻译
        # "None" 无翻译
        self.speaker: str = speaker
        self.origin_raw: str = origin_raw
        self.origin_escape: str = origin_escape
        self.origin_flag: str = origin
        self.translate: str = translate
