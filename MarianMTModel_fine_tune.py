import torch
from transformers import MarianMTModel, MarianTokenizer
from typing import Union, List


class MarianMTModel_fine_tune():
    def __init__(self, model_or_path: str, device: str):
        self.model: MarianMTModel = MarianMTModel.from_pretrained(model_or_path)
        self.tokenizer = MarianTokenizer.from_pretrained(model_or_path)
        self.model_family = 'MarianMT'

        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        elif device == "cpu":
            self.device = torch.device("cpu")
        elif device == "gpu":
            self.device = torch.device("cuda")

        self.model.to(self.device)

    def translate(self, text: Union[str, List[str]], **kwargs):

        len_limit = int(max([list(cen.split(' ')).__len__() for cen in text]) * 2)
        with torch.no_grad():
            model_inputs = self.tokenizer(text, return_tensors="pt", padding=True)
            model_inputs.to(self.device)

            translated = self.model.generate(**model_inputs, max_new_tokens=len_limit).cpu()
            res = [self.tokenizer.decode(t, skip_special_tokens=True) for t in translated]

            return res
