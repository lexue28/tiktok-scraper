
from detoxify import Detoxify

text_array = [
    "7524726168176643350",
    "Eleonora Arcidiacono🩷",
    "eleonora.arcidiacono",
    "Terribile",
    "original sound",
    "IL MASCARA 😭",
    "Mi dispiace dirlo ragazze non mi strucco prima di dormire SCUSATE LA SINCERITÀ VINCE IN CERTI CASI",
    "“Ma chi me l’ha fatto fare di truccarmi”",
    "truccarsi per andare a fa il bagno al fiume",
    "(mi strucco la mattina dopo #i’mjustagirl )",
    "o truccarsi per fare 5 minuti di foto per il curriculum e doversi poi struccare-",
    "got next part?",
    "Dopo essermi tolta il mascara sembro un panda😭",
    "qualcuno mi può dare un consiglio per togliere il mascara delicatamente che ogni me le sfracello?",
    "io in questo esatto momento (sto a scrollare tiktok per posticipare sto momento)",]
# results = Detoxify('original').predict('example text')

# results = Detoxify('unbiased').predict(['example text 1','example text 2'])

results = Detoxify('multilingual').predict(text_array)

# to specify the device the model will be allocated on (defaults to cpu), accepts any torch.device input

# model = Detoxify('original', device='cuda')

# optional to display results nicely (will need to pip install pandas)

import pandas as pd

print(pd.DataFrame(results, index=text_array).round(5))
