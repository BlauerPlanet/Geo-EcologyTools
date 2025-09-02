from qgis.utils import iface
import pandas as pd
import os

fields=pd.DataFrame(columns=["Layer","field"])
i = 0
# get active and shown Layer names
for layer in iface.mapCanvas().layers():
    prov = layer.dataProvider()

    field_names = [field.name() for field in prov.fields()]

    for count, f in enumerate(field_names):
        print(f"{layer.name()} - {count} {f}")
        fields.loc[i,"Layer"] = layer.name()
        fields.loc[i,"field"] = f
        i=i+1

path = os.path.join("I:\\", "fields.xlsx")
print(path)
fields.to_excel(path)