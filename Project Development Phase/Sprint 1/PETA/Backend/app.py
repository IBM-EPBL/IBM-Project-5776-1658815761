# from curses import flash
from flask import Flask, render_template, request
from flask_restful import Api, Resource, reqparse, abort

import ibm_db

app = Flask(__name__)
api = Api(app)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31198;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=wsk70349;PWD=iVNcAyUqR4Py2Aw0",'','')

account_put_args = reqparse.RequestParser()
account_put_args.add_argument("name", type=str, help="Name of the Account is required", required=True)
account_put_args.add_argument("email", type=str, help="Email of the Account is required", required=True)
account_put_args.add_argument("password", type=str, help="Password of the Account is required", required=True)

Accounts = {}

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/addAccount',methods = ['POST', 'GET'])
def addAccount():
  if request.method == 'POST':

    name = request.form['reg-name']
    email = request.form['reg-email']
    password = request.form['reg-password']

    sql = "SELECT * FROM account order by id desc limit 1"
    stmt = ibm_db.prepare(conn, sql)
    # ibm_db.bind_param(stmt,1,name)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    
    id = 0
    while account != False:
        id = account.get("ID")
        account = ibm_db.fetch_assoc(stmt)
    id = id + 1

    # if account:
    #   return render_template('list.html', msg="You are already a member, please login using your details")
    # else:
    insert_sql = "INSERT INTO account VALUES (?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, id)
    ibm_db.bind_param(prep_stmt, 2, name)
    ibm_db.bind_param(prep_stmt, 3, email)
    ibm_db.bind_param(prep_stmt, 4, password)
    ibm_db.bind_param(prep_stmt, 5, 1)
    ibm_db.execute(prep_stmt)
    
    print( "Account Data saved successfuly..")
    return render_template('index.html')

@app.route('/loginAccount',methods = ['POST', 'GET'])
def loginAccount():
  if request.method == 'POST':

    email = request.form['login-email']
    password = request.form['login-password']

    sql = "SELECT * FROM account WHERE email = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    check = 0
    while account != False:
        id = account.get("ID")
        password_db = account.get("PASSWORD")
        if password == password_db:
            check = 1
            print("Success")
        account = ibm_db.fetch_assoc(stmt)
    
    if check == 1:
        print( "Login successfull..")
        return render_template('homepage.html')
    print( "Login failed..")

def abort_if_account_id_doesnt_exist(account_id):
    if account_id not in Accounts:
        abort(404, message="account_id is not valid....")

def abort_if_account_exist(account_id):
    if account_id in Accounts:
        abort(409, message="Account already exist with same account_id ......")


class Account(Resource):
    def get(self, account_id):
        abort_if_account_id_doesnt_exist(account_id)
        return Accounts[account_id]
    
    def put(self,account_id):
        abort_if_account_exist(account_id)
        args = account_put_args.parse_args()
        Accounts[account_id] = args
        return Accounts[account_id], 201

    def delete(self, account_id):
        abort_if_account_id_doesnt_exist(account_id)
        del Accounts[account_id]
        return '', 204

        

api.add_resource(Account, "/account/<int:account_id>")

if __name__ == "__main__":
    app.run(debug=True)


























# BASIC GET API

# class HelloWorld(Resource):
#     def get(self):
#         return {"data" : "Hello World"}

# api.add_resource(HelloWorld, "/helloworld")