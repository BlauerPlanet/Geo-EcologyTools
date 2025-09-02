#uses the multilingual list of the Worlds International Ornithological Congress (IOC) Bird List: https://worldbirdnames.org/Multiling%20IOC%2015.1_c.xlsx
# it should correspond well to the bird net taxons because they use the ebird taxonomy which is based on the IOC taxonomy

import pandas as pd

file = pd.read_excel("TÖP\Multiling IOC 15.1_c.xlsx")
lex = file[["Order","Family","IOC_15.1","English","German"]]
lex.set_index('IOC_15.1', inplace=True)
#lex_dict = lex.to_dict(orient="index", index=True)
#print(lex_dict["Tangara velia"])
lex.to_excel("lat-dts.xlsx", header=True)
#only problem: since it is an World List --> creating dataframe and searching for one species takes around 15 s (on my hardware)