import csv

from pymongo import MongoClient

# mogodb dabase connection
conn = MongoClient(
    'mongodb+srv://npa_chart_data_db:t3WLKFbUFg1zF2Nz@cluster0.cdlbaub.mongodb.net/?retryWrites=true&w=majority')
db = conn['npa_data']
collection = db['charts']

header = ['name', 'date', 'chart_type', 'overdue_days', 'outstanding_amount', 'recovery_amount']
csvfile = open('data.csv', 'r')
reader = csv.DictReader( csvfile )

for each in reader:
    row={}
    for field in header:
        if field != 'date' and (each[field]).isdigit():
            each[field]=int(each[field])
        row[field]=each[field] if len(str(each[field])) >0 else None
    collection.insert_one(row)