import io

from fastapi import APIRouter, Response, BackgroundTasks
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt

from schemas.npa_schema import serializeList, serializeDict
from config.db import conn
from models.npa import Npa
from bson import ObjectId

chart_fields = ['overdue_days', 'outstanding_amount', 'recovery_amount']
account_types = ['All', 'New NPA Accounts', 'NPA Accounts with recovery', 'New SMA Accounts']

npa = APIRouter()


@npa.get('/accounts', tags=['NPA Data'])
def get_all_accounts(account_type: str = None):
    if account_type in account_types and account_type != 'All':
        return serializeList(conn.npa_data.charts.find({'chart_type': account_type}))
    elif account_type == 'All': 
        return serializeList(conn.npa_data.charts.find())
    return {'error': 'Invalid account type, account type must be one of {}'.format(account_types)}

@npa.post('/npa/', tags=['NPA Data'])
def create_entry(npa: Npa):
    conn.npa_data.charts.insert_one(dict(npa))
    return serializeList(conn.npa_data.charts.find())

@npa.get('/npa/{id}', tags=['NPA Data'])
def get_one_entry(id):
    return serializeDict(conn.npa_data.charts.find_one({"_id": ObjectId(id)}))

@npa.put('/npa/{id}', tags=['NPA Data'])
def update_entry(id, npa: Npa):
    conn.npadb.npa.find_one_and_update(
        {"id": id}, {"$set": dict(npa)})
    return serializeDict(conn.npa_data.charts.find_one({"_id": ObjectId(id)}))

@npa.delete('/npa/{id}', tags=['NPA Data'])
def delete_npa(id):
    return serializeDict(conn.npa_data.charts.find_one_and_delete({"_id": ObjectId(id)}))


@npa.get('/charts', tags=['NPA Charts'])
def get_all_charts(chart_field: str):
    if chart_field in chart_fields:
        return serializeList(conn.npa_data.charts.find({}, {'date': 1, '{}'.format(chart_field): 1}))
    return {'error': 'Invalid chart field, chart field must be one of {}'.format(chart_fields)}

@npa.get("/analytics", tags=['NPA Analytics'])
def get_analytics():
    gnpa, gnpar, sma, recovery=0,0,0,0
    npa = serializeList(conn.npa_data.charts.find({}, {'outstanding_amount': 1, 'chart_type': 1, 'recovery_amount': 1}))
    for each in npa:
        if each['chart_type'] == 'New NPA Accounts' and each['outstanding_amount']:
            gnpa = gnpa + each['outstanding_amount']
        if each['chart_type'] == 'NPA Accounts with recovery' and each['outstanding_amount']:
            gnpar = gnpar + each['outstanding_amount']
        if each['chart_type'] == 'New SMA Accounts' and each['outstanding_amount']:
            sma = sma + each['outstanding_amount']
        if each['recovery_amount']:
            recovery = recovery + each['recovery_amount']
    return {'GNPA': gnpa, 'SMA1': gnpar, 'SMA2': sma, 'Recovery': recovery}


def create_img(chart_field: str):
    data = get_all_charts(chart_field)
    chart_data = {}
    for d in data:
        if d[chart_field]:
            chart_data[d['date']] = d[chart_field]
    courses = list(chart_data.keys())
    values = list(chart_data.values())
    plt.rcParams['figure.figsize'] = [7.50, 3.50]
    plt.rcParams['figure.autolayout'] = True
    plt.bar(courses, values, color ='maroon',
            width = 0.4)
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close()
    return img_buf
    
@npa.get('/get_chart_img', tags=['NPA Charts'])
def get_chart_img(chart_field: str ,background_tasks: BackgroundTasks):
    if chart_field in chart_fields:
        img_buf = create_img(chart_field)
        bufContents: bytes = img_buf.getvalue()
        background_tasks.add_task(img_buf.close)
        headers = {'Content-Disposition': 'inline; filename="{}.png"'.format(chart_field)}
        return Response(bufContents, headers=headers, media_type='image/png')
    return {'error': 'Invalid chart field, chart field must be one of {}'.format(chart_fields)}
