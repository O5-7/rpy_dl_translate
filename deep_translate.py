import dl_translate as dlt
import time

text_hi = "I have a red apple"
test = 'Again, I have no idea why this is happening. Nao shouldn’t even know where I live. And she definitely shouldn’t be wandering around Kumon-mi unsupervised.'
print('origin:'.ljust(7), test)


mt = dlt.TranslationModel(
    model_or_path=r'E:\PycharmProjects\dl_models\mbart-large-50-one-to-many-mmt',
    model_family='mbart50',
    device="gpu"
)
result = mt.translate(test, source=dlt.lang.ENGLISH, target=dlt.lang.CHINESE, verbose=True)
print('mbert:'.ljust(7), result)

print('qq:'.ljust(7), '{i}再说一次，{/i}我不知道为什么会发生这种情况。Nao根本不应该知道我住在哪里。而且她绝对不应该在无人看管的情况下在库蒙米附近闲逛。')
for _ in range(10):
    t_start = time.time()
    mt.translate(test, source=dlt.lang.ENGLISH, target=dlt.lang.CHINESE)
    print(time.time() - t_start)