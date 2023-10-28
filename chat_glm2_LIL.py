# -*- coding: utf-8 -*-
from typing import List, Union
import torch
from tqdm import tqdm
from transformers import AutoConfig, AutoModel, AutoTokenizer
import os


class chat_glm2_LIL:
    def __init__(self, model_or_path: str, device: str = 'auto', checkpoint_name: str = 'checkpoint-3000'):
        self.model_family = 'chat_glm2'
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        elif device == "cpu":
            self.device = torch.device("cpu")
        elif device == "gpu":
            self.device = torch.device("cuda")

        self.base_time_out = 5

        self.tokenizer = AutoTokenizer.from_pretrained(model_or_path, trust_remote_code=True)
        self.config = AutoConfig.from_pretrained(model_or_path, pre_seq_len=128, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_or_path, trust_remote_code=True, config=self.config)

        prefix_state_dict = torch.load(os.path.join(model_or_path, 'prefix', checkpoint_name, "pytorch_model.bin"), map_location=self.device)
        new_prefix_state_dict = {}
        for k, v in prefix_state_dict.items():
            if k.startswith("transformer.prefix_encoder."):
                new_prefix_state_dict[k[len("transformer.prefix_encoder."):]] = v
        self.model.transformer.prefix_encoder.load_state_dict(new_prefix_state_dict)
        self.model = self.model.half().to(self.device)
        self.model = self.model.eval()

    def translate(self, text: Union[str, List[str]], **kwargs):
        if type(text) == str:
            text = [text]

        res = []
        text_iter = tqdm(text, ncols=120) if text.__len__() > 3 else text
        for input_text in text_iter:
            input_text_len = len(input_text.split(' ')) * 4
            input_text_len = max(input_text_len, 128)
            response, history = self.model.chat(self.tokenizer, '翻译这个LIL的台词:' + input_text, max_length=input_text_len)
            # response, history = self.chat_recursive(input_text)
            res.append(response)

        if res.__len__() == 1 and type(res) == list:
            res = res[0]
        return res


if __name__ == '__main__':
    mt = chat_glm2_LIL('../dl_models/chatglm2-6b-int4', checkpoint_name='checkpoint-3000')
    test = ['Sure, it may have taken the end of several worlds (Or several ends of one world) for me to {i}be able{/i} to share something like this with you, but...I’m here.',
            'And go where?',
            'Anywhere.Your room.My house.That new apartment you got me.',
            'Am I truly the one you wish to leave here with?',
            '''In the sense that I'm in love with you or something?No.''',
            '''But in the sense that I feel eerily safe whenever I'm with you,yes.I want you by my side until this all boils over.''',
            '''And if it never does,will we remain together forever?''',
            '''I {i}should{/i} say that I feel a little relieved to find out that {i}this{/i} is why you’ve been hanging out with Kaori lately, though. She’s really pretty and I got jealous and...I’m sorry.''']
    for translation in mt.translate(test):
        print(translation)
