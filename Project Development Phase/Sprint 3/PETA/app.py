# from curses import flash
from flask import Flask, render_template, request
from flask_restful import Api, Resource, reqparse, abort
from datetime import date, datetime, timedelta
from flask_mail import Mail, Message

import ibm_db

app = Flask(__name__)
api = Api(app)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31198;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=wsk70349;PWD=iVNcAyUqR4Py2Aw0",'','')

account_put_args = reqparse.RequestParser()
account_put_args.add_argument("name", type=str, help="Name of the Account is required", required=True)
account_put_args.add_argument("email", type=str, help="Email of the Account is required", required=True)
account_put_args.add_argument("password", type=str, help="Password of the Account is required", required=True)

Accounts = {}

# ---------------------------------- HOME ----------------------------------

@app.route('/')
def home():
    return render_template('index.html')

# ---------------------------------- SIGN UP --------------------------------

@app.route('/addAccount',methods = ['POST', 'GET'])
def addAccount():
  if request.method == 'POST':

    name = request.form['reg-name']
    email = request.form['reg-email']
    password = request.form['reg-password']
    predictable_monthly_income = request.form['reg-monthly-income']

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
    # id name email password is_active
    insert_sql = "INSERT INTO account VALUES (?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, id)
    ibm_db.bind_param(prep_stmt, 2, name)
    ibm_db.bind_param(prep_stmt, 3, email)
    ibm_db.bind_param(prep_stmt, 4, password)
    ibm_db.bind_param(prep_stmt, 5, 1)
    ibm_db.execute(prep_stmt)
    
    today = date.today()
    today = today.strftime("%d-%m-%Y")

    insertConfigurations(id, "Expense", "Food & Beverages", predictable_monthly_income * 0.15, today)
    insertConfigurations(id, "Expense", "Groceries", predictable_monthly_income * 0.25, today)
    insertConfigurations(id, "Expense", "Fuel", predictable_monthly_income * 0.15, today)
    insertConfigurations(id, "Expense", "Entertainment", predictable_monthly_income * 0.10, today)
    insertConfigurations(id, "Expense", "Other Expenses", predictable_monthly_income * 0.10, today)
    
    print( "Account Data saved successfuly..")
    return render_template('index.html')

# ---------------------------------- SIGN IN ----------------------------------

@app.route('/loginAccount',methods = ['POST', 'GET'])
def loginAccount():
  if request.method == 'POST':

    email = request.form['login-email']
    password = request.form['login-password']

    sql = "SELECT * FROM account WHERE email = ? AND is_active = 1"
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
    return "Login Failed!"

@app.route('/dashboard',methods = ['POST', 'GET'])
def dashboard():
    return render_template('dashboard.html')

# ---------------------------------- FINANCIAL ACCOUNTS ----------------------------------

@app.route('/addFinancialAccount',methods = ['POST', 'GET'])
def addFinancialAccount():
  if request.method == 'POST':

    user_id = request.form['add_account_user_id']
    holders_name = request.form['add_account_holders_name']
    account_no = request.form['add_account_acc_num']
    # acc_id user_id holders_name account_no is_active

    sql = "SELECT * FROM financial_account order by acc_id desc limit 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    financial_account = ibm_db.fetch_assoc(stmt)
    
    id = 0
    while financial_account != False:
        id = financial_account.get("acc_id")
        financial_account = ibm_db.fetch_assoc(stmt)
    id = id + 1

    insert_sql = "INSERT INTO financial_account VALUES (?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, id)
    ibm_db.bind_param(prep_stmt, 2, user_id)
    ibm_db.bind_param(prep_stmt, 3, holders_name)
    ibm_db.bind_param(prep_stmt, 4, account_no)
    ibm_db.bind_param(prep_stmt, 5, 1)
    ibm_db.execute(prep_stmt)
    
    print( "Financial Account Data saved successfuly..")
    # return render_template('manageExpenses.html')
    return render_template('index.html')

@app.route('/viewFinancialAccount',methods = ['POST', 'GET'])
def viewFinancialAccount():
  if request.method == 'POST':

    user_id = request.form['view_financial_account_user_id']

    sql = "SELECT * FROM financial_account WHERE user_id = ? AND is_active = 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user_id)
    ibm_db.execute(stmt)
    financial_account = ibm_db.fetch_assoc(stmt)

    financial_accounts = []
    while financial_account != False:
        financial_accounts.append(financial_account)
        financial_account = ibm_db.fetch_assoc(stmt)

    print(financial_accounts);
    return financial_account;

@app.route('/deleteFinancialAccount',methods = ['POST', 'GET'])
def deleteFinancialAccount():
  if request.method == 'POST':

    user_id = request.form['delete_financial_account_user_id']
    acc_id = request.form['delete_financial_account_id']

    sql = "SELECT * FROM financial_account WHERE acc_id = ? AND user_id = ? AND is_active = 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,acc_id)
    ibm_db.bind_param(stmt,2,user_id)
    ibm_db.execute(stmt)
    financial_account = ibm_db.fetch_assoc(stmt)

    while financial_account != False:
        update_sql = "UPDATE financial_account SET is_active = 0 WHERE user_id = ? AND acc_id = ? AND is_active = 1"
        prep_stmt = ibm_db.prepare(conn, update_sql)
        ibm_db.bind_param(prep_stmt, 1, user_id)
        ibm_db.bind_param(prep_stmt, 2, acc_id)
        ibm_db.execute(prep_stmt)
        financial_account = ibm_db.fetch_assoc(stmt)

    print("Financial Account removed successfully!");
    # return render_template('manageExpenses.html')
    return "Financial Account removed successfully!";

# ---------------------------------- EXPENSES ----------------------------------

@app.route('/addExpenses',methods = ['POST', 'GET'])
def addExpenses():
  if request.method == 'POST':

    user_id = request.form['add_expense_user_id']
    acc_id = request.form['add_expense_acc_id']
    exp_type = request.form['add_expense_type']
    sub_type = request.form['add_expense_sub_type']
    amount = request.form['add_expense_amount']
    date = request.form['add_expense_date']
    # exp_id user_id acc_id exp_type sub_type amount added_date is_active

    sql = "SELECT * FROM expenses order by exp_id desc limit 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    expenses = ibm_db.fetch_assoc(stmt)
    
    id = 0
    while expenses != False:
        id = expenses.get("exp_id")
        expenses = ibm_db.fetch_assoc(stmt)
    id = id + 1

    insert_sql = "INSERT INTO expenses VALUES (?,?,?,?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, id)
    ibm_db.bind_param(prep_stmt, 2, user_id)
    ibm_db.bind_param(prep_stmt, 3, acc_id)
    ibm_db.bind_param(prep_stmt, 4, exp_type)
    ibm_db.bind_param(prep_stmt, 5, sub_type)
    ibm_db.bind_param(prep_stmt, 6, amount)
    ibm_db.bind_param(prep_stmt, 7, date)
    ibm_db.bind_param(prep_stmt, 8, 1)
    ibm_db.execute(prep_stmt)
    
    print( "Expense Data saved successfuly..")

    if exp_type.lower() == "Expense".lower():

        start_date = first_day_of_month()
        last_date = last_day_of_month()

        sql_sum = "SELECT * FROM expenses WHERE user_id = ? AND exp_type = ? AND sub_type = ? AND added_date BETWEEN(?,?) AND is_active = 1"
        stmt_sum = ibm_db.prepare(conn, sql_sum)
        ibm_db.bind_param(stmt_sum,1,user_id)
        ibm_db.bind_param(stmt_sum,2,exp_type)
        ibm_db.bind_param(stmt_sum,3,sub_type)
        ibm_db.bind_param(stmt_sum,4,start_date)
        ibm_db.bind_param(stmt_sum,5,last_date)
        ibm_db.execute(stmt_sum)
        expenses_sum = ibm_db.fetch_assoc(stmt_sum)
        
        total_sum = 0
        while expenses_sum != False:
            total_sum += int(expenses_sum.get("amount"))
            expenses_sum = ibm_db.fetch_assoc(stmt_sum)
        
        print("total_sum: " + str(total_sum))
        
        sql_conf = "SELECT * FROM configurations WHERE user_id = ? AND conf_type = ? AND conf_name = ? AND is_active = 1"
        stmt_conf = ibm_db.prepare(conn, sql_conf)
        ibm_db.bind_param(stmt_conf,1,user_id)
        ibm_db.bind_param(stmt_conf,2,exp_type)
        ibm_db.bind_param(stmt_conf,3,sub_type)
        ibm_db.execute(stmt_conf)
        expenses_conf = ibm_db.fetch_assoc(stmt_conf)

        conf_amount = 92233720368547000
        while expenses_conf != False:
            conf_amount = int(expenses_conf.get("amount"))
            expenses_conf = ibm_db.fetch_assoc(stmt_sum)

        print("conf_amount: " + str(conf_amount))

        if(total_sum > conf_amount):
            print("Exceeded in insert!")

            sql_notif_id = "SELECT * FROM notifications order by notif_id desc limit 1"
            stmt_notif_id = ibm_db.prepare(conn, sql_notif_id)
            ibm_db.execute(stmt_notif_id)
            notif_id_result = ibm_db.fetch_assoc(stmt_notif_id)

            notif_id = 0
            while notif_id_result != False:
                notif_id = expenses.get("notif_id")
                notif_id_result = ibm_db.fetch_assoc(stmt_notif_id)
            notif_id = notif_id + 1

            today = date.today()
            today = today.strftime("%d-%m-%Y")

            insert_sql_notif = "INSERT INTO notifications VALUES (?,?,?,?,?,?)"
            # notif_id user_id heading body_text date is_active
            prep_stmt_notif = ibm_db.prepare(conn, insert_sql_notif)
            ibm_db.bind_param(prep_stmt_notif, 1, notif_id)
            ibm_db.bind_param(prep_stmt_notif, 2, user_id)
            ibm_db.bind_param(prep_stmt_notif, 3, "Over expenditure alert!")
            ibm_db.bind_param(prep_stmt_notif, 4, "You have exceeded your expenditure limit in '" + sub_type + "' Category!")
            ibm_db.bind_param(prep_stmt_notif, 5, today) # curDate()
            ibm_db.bind_param(prep_stmt_notif, 6, 1)
            ibm_db.execute(prep_stmt_notif)
        else:
            # return render_template('manageExpenses.html')
            return render_template('index.html')
    else:
        # return render_template('manageExpenses.html')
        return render_template('index.html')
    # return render_template('manageExpenses.html')
    return render_template('index.html')

@app.route('/viewExpenses',methods = ['POST', 'GET'])
def viewExpenses():
  if request.method == 'POST':

    user_id = request.form['view_expenses_user_id']
    acc_id = request.form['view_expenses_account_id']

    sql = "SELECT * FROM expenses WHERE user_id = ? AND acc_id = ? AND is_active = 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user_id)
    ibm_db.bind_param(stmt,2,acc_id)
    ibm_db.execute(stmt)
    expenses = ibm_db.fetch_assoc(stmt)

    expenses_list = []
    while expenses != False:
        expenses_list.append(expenses)
        expenses = ibm_db.fetch_assoc(stmt)

    print("expenses_list: " + str(expenses_list));
    return expenses_list;

@app.route('/updateExpense',methods = ['POST', 'GET'])
def updateExpense():
  if request.method == 'POST':

    user_id = request.form['update_expense_user_id']
    exp_id = request.form['update_expense_id']
    acc_id = request.form['add_expense_acc_id']
    exp_type = request.form['add_expense_type']
    sub_type = request.form['add_expense_sub_type']
    amount = request.form['add_expense_amount']
    date = request.form['add_expense_date']

    sql = "SELECT * FROM expenses WHERE user_id = ? AND exp_id = ? AND is_active = 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user_id)
    ibm_db.bind_param(stmt,2,exp_id)
    ibm_db.execute(stmt)
    expenses = ibm_db.fetch_assoc(stmt)

    while expenses != False:
        update_sql = "UPDATE expenses SET acc_id = ?, exp_type = ?, sub_type = ?, amount = ?, date = ? WHERE user_id = ? AND exp_id = ? AND is_active = 1"
        prep_stmt = ibm_db.prepare(conn, update_sql)
        ibm_db.bind_param(prep_stmt, 1, acc_id)
        ibm_db.bind_param(prep_stmt, 2, exp_type)
        ibm_db.bind_param(prep_stmt, 3, sub_type)
        ibm_db.bind_param(prep_stmt, 4, amount)
        ibm_db.bind_param(prep_stmt, 5, date)
        ibm_db.bind_param(prep_stmt, 6, user_id)
        ibm_db.bind_param(prep_stmt, 7, exp_id)
        ibm_db.execute(prep_stmt)
        expenses = ibm_db.fetch_assoc(stmt)

    print("Expense updated successfully!");

    if exp_type.lower() == "Expense".lower():
        
        start_date = first_day_of_month()
        last_date = last_day_of_month()

        sql_sum = "SELECT * FROM expenses WHERE user_id = ? AND exp_type = ? AND sub_type = ? AND added_date BETWEEN(?,?) AND is_active = 1"
        stmt_sum = ibm_db.prepare(conn, sql_sum)
        ibm_db.bind_param(stmt_sum,1,user_id)
        ibm_db.bind_param(stmt_sum,2,exp_type)
        ibm_db.bind_param(stmt_sum,3,sub_type)
        ibm_db.bind_param(stmt_sum,4,start_date)
        ibm_db.bind_param(stmt_sum,5,last_date)
        ibm_db.execute(stmt_sum)
        expenses_sum = ibm_db.fetch_assoc(stmt_sum)
        
        total_sum = 0
        while expenses_sum != False:
            total_sum += int(expenses_sum.get("amount"))
            expenses_sum = ibm_db.fetch_assoc(stmt_sum)
        
        print("total_sum: " + str(total_sum))
        
        sql_conf = "SELECT * FROM configurations WHERE user_id = ? AND conf_type = ? AND conf_name = ? AND is_active = 1"
        stmt_conf = ibm_db.prepare(conn, sql_conf)
        ibm_db.bind_param(stmt_conf,1,user_id)
        ibm_db.bind_param(stmt_conf,2,exp_type)
        ibm_db.bind_param(stmt_conf,3,sub_type)
        ibm_db.execute(stmt_conf)
        expenses_conf = ibm_db.fetch_assoc(stmt_conf)

        conf_amount = 92233720368547000
        while expenses_conf != False:
            conf_amount = int(expenses_conf.get("amount"))
            expenses_conf = ibm_db.fetch_assoc(stmt_sum)

        print("conf_amount: " + str(conf_amount))

        if(total_sum > conf_amount):
            print("Exceeded in update!")

            sql_notif_id = "SELECT * FROM notifications order by notif_id desc limit 1"
            stmt_notif_id = ibm_db.prepare(conn, sql_notif_id)
            ibm_db.execute(stmt_notif_id)
            notif_id_result = ibm_db.fetch_assoc(stmt_notif_id)

            notif_id = 0
            while notif_id_result != False:
                notif_id = expenses.get("notif_id")
                notif_id_result = ibm_db.fetch_assoc(stmt_notif_id)
            notif_id = notif_id + 1
            
            today = date.today()
            today = today.strftime("%d-%m-%Y")

            insert_sql_notif = "INSERT INTO notifications VALUES (?,?,?,?,?,?)"
            # notif_id user_id heading body_text date is_active
            prep_stmt_notif = ibm_db.prepare(conn, insert_sql_notif)
            ibm_db.bind_param(prep_stmt_notif, 1, notif_id)
            ibm_db.bind_param(prep_stmt_notif, 2, user_id)
            ibm_db.bind_param(prep_stmt_notif, 3, "Over expenditure alert!")
            ibm_db.bind_param(prep_stmt_notif, 4, "You have exceeded your expenditure limit in '" + sub_type + "' Category!")
            ibm_db.bind_param(prep_stmt_notif, 5, today) # curDate()
            ibm_db.bind_param(prep_stmt_notif, 6, 1)
            ibm_db.execute(prep_stmt_notif)
        else:
            # return render_template('manageExpenses.html')
            return render_template('index.html')
    else:
        # return render_template('manageExpenses.html')
        return render_template('index.html')
    # return render_template('manageExpenses.html')
    return "Expense updated successfully!";

@app.route('/deleteExpense',methods = ['POST', 'GET'])
def deleteExpense():
  if request.method == 'POST':

    user_id = request.form['delete_expense_user_id']
    acc_id = request.form['delete_expense_acc_id']
    exp_id = request.form['delete_expense_id']

    sql = "SELECT * FROM expenses WHERE user_id = ? AND acc_id = ? AND exp_id = ? AND is_active = 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user_id)
    ibm_db.bind_param(stmt,2,acc_id)
    ibm_db.bind_param(stmt,3,exp_id)
    ibm_db.execute(stmt)
    expenses = ibm_db.fetch_assoc(stmt)

    while expenses != False:
        update_sql = "UPDATE expenses SET is_active = 0 WHERE user_id = ? AND acc_id = ? AND exp_id = ? AND is_active = 1"
        prep_stmt = ibm_db.prepare(conn, update_sql)
        ibm_db.bind_param(prep_stmt, 1, user_id)
        ibm_db.bind_param(prep_stmt, 2, acc_id)
        ibm_db.bind_param(prep_stmt, 3, exp_id)
        ibm_db.execute(prep_stmt)
        expenses = ibm_db.fetch_assoc(stmt)

    print("Expense removed successfully!");
    # return render_template('manageExpenses.html')
    return "Expense removed successfully!";

# ---------------------------------- CONFIGURATIONS ----------------------------------

def insertConfigurations(user_id, conf_type, conf_name, amount, date):

    sql = "SELECT * FROM configurations order by conf_id desc limit 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    configuration = ibm_db.fetch_assoc(stmt)
    
    id = 0
    while configuration != False:
        id = configuration.get("conf_id")
        configuration = ibm_db.fetch_assoc(stmt)
    id = id + 1

    insert_sql = "INSERT INTO configurations VALUES (?,?,?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, id)
    ibm_db.bind_param(prep_stmt, 2, user_id)
    ibm_db.bind_param(prep_stmt, 3, conf_type)
    ibm_db.bind_param(prep_stmt, 4, conf_name)
    ibm_db.bind_param(prep_stmt, 5, amount)
    ibm_db.bind_param(prep_stmt, 6, date)
    ibm_db.bind_param(prep_stmt, 7, 1)
    ibm_db.execute(prep_stmt)

@app.route('/addConfiguration',methods = ['POST', 'GET'])
def addConfiguration():
  if request.method == 'POST':

    user_id = request.form['add_conf_user_id']
    conf_type = request.form['add_conf_type']
    conf_name = request.form['add_conf_name']
    amount = request.form['add_conf_amount']
    date = request.form['add_conf_date']
    # conf_id user_id conf_type conf_name amount added_date is_active

    sql = "SELECT * FROM configurations order by conf_id desc limit 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    configuration = ibm_db.fetch_assoc(stmt)
    
    id = 0
    while configuration != False:
        id = configuration.get("conf_id")
        configuration = ibm_db.fetch_assoc(stmt)
    id = id + 1

    insert_sql = "INSERT INTO configurations VALUES (?,?,?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, id)
    ibm_db.bind_param(prep_stmt, 2, user_id)
    ibm_db.bind_param(prep_stmt, 3, conf_type)
    ibm_db.bind_param(prep_stmt, 4, conf_name)
    ibm_db.bind_param(prep_stmt, 5, amount)
    ibm_db.bind_param(prep_stmt, 6, date)
    ibm_db.bind_param(prep_stmt, 7, 1)
    ibm_db.execute(prep_stmt)
    
    print( "Configuration Data saved successfuly..")
    # return render_template('manageExpenses.html')
    return render_template('index.html')

@app.route('/fetchConfigurations',methods = ['POST', 'GET'])
def fetchConfigurations():
  if request.method == 'POST':

    user_id = request.form['view_conf_user_id']

    sql = "SELECT * FROM configurations WHERE user_id = ? AND is_active = 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user_id)
    ibm_db.execute(stmt)
    configurations = ibm_db.fetch_assoc(stmt)

    configuration_list = []
    while configurations != False:
        configuration_list.append(configurations)
        configurations = ibm_db.fetch_assoc(stmt)

    print("configuration_list: " + str(configuration_list));
    return configuration_list;

@app.route('/updateConfiguration',methods = ['POST', 'GET'])
def updateConfiguration():
  if request.method == 'POST':

    user_id = request.form['update_conf_user_id']
    conf_id = request.form['update_conf_id']
    conf_type = request.form['update_conf_type']
    conf_name = request.form['update_conf_name']
    amount = request.form['update_conf_amount']
    date = request.form['update_conf_date']

    sql = "SELECT * FROM configurations WHERE user_id = ? AND conf_id = ? AND is_active = 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user_id)
    ibm_db.bind_param(stmt,2,conf_id)
    ibm_db.execute(stmt)
    configurations = ibm_db.fetch_assoc(stmt)

    while configurations != False:
        update_sql = "UPDATE configurations SET conf_type = ?, conf_name = ?, amount = ?, date = ? WHERE user_id = ? AND conf_id = ? AND is_active = 1"
        prep_stmt = ibm_db.prepare(conn, update_sql)
        ibm_db.bind_param(prep_stmt, 1, conf_type)
        ibm_db.bind_param(prep_stmt, 2, conf_name)
        ibm_db.bind_param(prep_stmt, 3, amount)
        ibm_db.bind_param(prep_stmt, 4, date)
        ibm_db.bind_param(prep_stmt, 5, user_id)
        ibm_db.bind_param(prep_stmt, 6, conf_id)
        ibm_db.execute(prep_stmt)
        configurations = ibm_db.fetch_assoc(stmt)

    print("Configuration updated successfully!");
    # return render_template('manageExpenses.html')
    return "Configuration updated successfully!";

@app.route('/deleteConfiguration',methods = ['POST', 'GET'])
def deleteConfiguration():
  if request.method == 'POST':

    user_id = request.form['delete_expense_user_id']
    conf_id = request.form['delete_expense_id']

    sql = "SELECT * FROM configurations WHERE user_id = ? AND conf_id = ? AND is_active = 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user_id)
    ibm_db.bind_param(stmt,2,conf_id)
    ibm_db.execute(stmt)
    configurations = ibm_db.fetch_assoc(stmt)

    while configurations != False:
        update_sql = "UPDATE configurations SET is_active = 0 WHERE user_id = ? AND conf_id = ? AND is_active = 1"
        prep_stmt = ibm_db.prepare(conn, update_sql)
        ibm_db.bind_param(prep_stmt, 1, user_id)
        ibm_db.bind_param(prep_stmt, 2, conf_id)
        ibm_db.execute(prep_stmt)
        configurations = ibm_db.fetch_assoc(stmt)

    print("Configuration removed successfully!");
    # return render_template('manageExpenses.html')
    return "Configuration removed successfully!";

# ---------------------------------- NOTIFICATIONS ----------------------------------

@app.route('/viewNotifications',methods = ['POST', 'GET'])
def viewNotifications():
  if request.method == 'POST':

    user_id = request.form['view_notification_user_id']

    sql = "SELECT * FROM notifications WHERE user_id = ? AND is_active = 1 ORDER BY notif_id desc"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user_id)
    ibm_db.execute(stmt)
    notifications = ibm_db.fetch_assoc(stmt)

    notification_list = []
    while notifications != False:
        notification_list.append(notifications)
        notifications = ibm_db.fetch_assoc(stmt)

    print("notification_list: " + str(notification_list));
    return notification_list;

# ---------------------------------- CUSTOMER SUPPORT ----------------------------------

@app.route('/storeReport',methods = ['POST', 'GET'])
def storeReport():
  if request.method == 'POST':

    user_id = request.form['report_user_id']
    title = request.form['report_title']
    report_text = request.form['report_text']

    sql_user = "SELECT * FROM account WHERE id = ? AND is_active = 1"
    stmt_user = ibm_db.prepare(conn, sql_user)
    ibm_db.bind_param(stmt_user,1,user_id)
    ibm_db.execute(stmt_user)
    user_name_result = ibm_db.fetch_assoc(stmt_user)
    
    user_name = ""
    while user_name_result != False:
        user_name.replace(user_name_result.get("name"))
        user_name_result = ibm_db.fetch_assoc(stmt_user)
    
    sql = "SELECT * FROM reports order by report_id desc limit 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    reports = ibm_db.fetch_assoc(stmt)
    
    id = 0
    while reports != False:
        id = reports.get("report_id")
        reports = ibm_db.fetch_assoc(stmt)
    id = id + 1
    
    today = date.today()
    today = today.strftime("%d-%m-%Y")

    # report_id user_id user_name title report_text date is_active
    insert_sql = "INSERT INTO reports VALUES (?,?,?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, id)
    ibm_db.bind_param(prep_stmt, 2, user_id)
    ibm_db.bind_param(prep_stmt, 3, user_name)
    ibm_db.bind_param(prep_stmt, 4, title)
    ibm_db.bind_param(prep_stmt, 5, report_text)
    ibm_db.bind_param(prep_stmt, 6, today) #curDate()
    ibm_db.bind_param(prep_stmt, 7, 1)
    ibm_db.execute(prep_stmt)

    print("Report stored successfully!")

    # to Be mailed
    
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'care.team.peta@gmail.com'
    app.config['MAIL_PASSWORD'] = 'vlxngbyimeqkvphw'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)

    msg = Message(("Concern: " + title), sender = 'care.team.peta@gmail.com', recipients = ['care.team.peta@gmail.com'])
    msg.body = ("Dear PETA Support Team, I am " + user_name + " - " + user_id + ", a PETA Application user. I have the following concern: " + report_text + " Waiting for your quick reply. Thanks & Regards " + user_name + " - " + user_id)
    mail.send(msg)
    print("Mail Sent")
    # return render_template('manageExpenses.html')
    return "Report stored successfully and Mail Sent to Team!";

@app.route('/viewReports',methods = ['POST', 'GET'])
def viewReports():
  if request.method == 'POST':

    user_id = request.form['view_reports_user_id']

    sql = "SELECT * FROM reports WHERE user_id = ? AND is_active = 1 ORDER BY report_id desc"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user_id)
    ibm_db.execute(stmt)
    reports = ibm_db.fetch_assoc(stmt)

    reports_list = []
    while reports != False:
        reports_list.append(reports)
        reports = ibm_db.fetch_assoc(stmt)

    print("reports_list: " + str(reports_list));
    return reports_list;

# ---------------------------------- EXTRAS ----------------------------------

def first_day_of_month():
    today = datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    start_date = datetime(int(year), int(month), 1)
    start_date = start_date.strftime("%d-%m-%Y")
    print(start_date)
    return start_date

def last_day_of_month():
    any_day_params = datetime.now()
    year = any_day_params.strftime("%Y")
    month = any_day_params.strftime("%m")
    any_day = datetime(int(year), int(month), 1)
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return ((next_month - timedelta(days=next_month.day)).strftime("%d-%m-%Y"))

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