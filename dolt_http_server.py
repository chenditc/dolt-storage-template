import os
import json
import pymysql
import pandas as pd
from sqlalchemy import create_engine
from functools import wraps
from flask import Flask, request, g

app = Flask(__name__)

AUTH_TOKEN = os.environ.get("DOLT_HTTP_TOKEN", "token")
DB_NAME = os.environ.get("DOLT_DB_NAME", "")

def check_prerequisite(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.data = json.loads(request.data)
        if g.data.get("token") != AUTH_TOKEN:
            return {"error": "token error"}

        sql_engine = create_engine(f'mysql+pymysql://root:@127.0.0.1/{DB_NAME}', pool_recycle=3600)
        with sql_engine.connect() as db_connection:
            g.db_connection = db_connection
            return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def heart_beat():
    return "<p>Dolt Http Server</p>"

@app.route("/dml", methods=['POST'])
@check_prerequisite
def run_dml_sql():
    """
    Example:
    response = requests.post("http://localhost:5001/dml", 
        json={"sql": "delete from positions where 1=1", "token" : "token"})

    response = requests.post("http://localhost:5001/dml", 
        json={"sql": "call dolt_commit('-a', '-m', 'daily update')", "token" : "token"})

    response = requests.post("http://localhost:5001/dml", 
        json={"sql": "call dolt_push()", "token" : "token"})
    """
    sql = g.data.get("sql")
    if sql is None:
        return {"error": "No sql"}

    try:
        g.db_connection.execute(sql)
    except Exception as e:
        print(e)
        return {"error": "Exception"}
    return {"error": ""}

@app.route("/dql", methods=['POST'])
@check_prerequisite
def run_dql_sql():
    """
    Example:
        curl -X POST -H "Content-type: application/json" 
            -d "{\"sql\" : \"SHOW TABLES;\", \"orient\": \"records\", \"token\" : \"token\"}" 
            "localhost:5001/dql"

        response = requests.post("http://localhost:5001/dql", 
            json={"sql": "show tables", "orient": "records", "token" : "token"})
    """
    sql = g.data.get("sql")
    if sql is None:
        return {"error": "No sql"}

    orient = g.data.get("orient", "tight")
    df = pd.read_sql(sql, g.db_connection)
    result = df.to_dict(orient=orient)
    return {"error": "", "result": result}

@app.route("/upsert_df", methods=['POST'])
@check_prerequisite
def upsert_df():
    """
    Example:

    data = [{
        'source': 'gtja',
        'instrument': 'SH000300',
        'currency': "CNY",
        'amount': 200,
        'value': 5000.32,
        'update_time': '2023-05-27 10:30:00',
        'platform': 'gtja'
    }]
    df = pd.DataFrame(data)
    response = requests.post("http://localhost:5001/upsert_df", 
            json={"df": df.to_dict("tight"), "table": "positions", "token" : "token"})
    """
    if g.data.get("df") is None:
        return {"error": "No df"}

    table = g.data.get("table")
    if table is None:
        return {"error": "No table"}

    orient = g.data.get("orient", "tight")
    df = pd.DataFrame.from_dict(g.data.get("df"), orient=orient)
    df.to_sql(table, con=g.db_connection, if_exists='append', index=False)
    return {"error": ""}



