import pandas as pd
import pymongo
parameters = pd.read_csv('.\\parameters.csv')
parameters = parameters[['No', 'ID', 'Bvang',
                         'Thickness', 'RtGap', 'probeindx']]
client = pymongo.MongoClient(
    "mongodb+srv://Kriss:Kriss206206@cluster0.rauq32w.mongodb.net/?retryWrites=true&w=majority")
db = client["NDT"]
collection = db["NDT"]

collection.delete_many({})
collection.insert_many(parameters.to_dict('records'))
