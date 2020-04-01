# mini_project.py
import subprocess
from subprocess import Popen, PIPE
from subprocess import check_output
from flask import Flask, render_template, request, session, flash
from flask_bootstrap import Bootstrap
from typing import List, Tuple
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import yaml
import os

app = Flask(__name__)
Bootstrap(app)

# Configure MySql
db = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = os.urandom(24)
mysql = MySQL(app)


@app.route('/')
def home() -> str:
    return render_template('index.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            form = request.form
            login_id = form["login_id"]
            password = form["password"]
            cursor = mysql.connection.cursor()
            query = f"SELECT password FROM user WHERE login_id = '{login_id}'" \
                    f" AND password = '{password}'"
            result = cursor.execute(query)
            print(query)
            if result == 0:
                flash("Login failed!", 'danger')
                return render_template('login.html')
            else:
                print("**************LOADING ACTIONS*****************")
                cursor.close()
                return render_template('actions.html')
        except mysql.connection.Error as err:
            print(err)
            flash("Login failed!", 'danger')
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/actions')
def actions():
    print("*****************IN ACTIONS*********************")
    cursor = mysql.connection.cursor()
    query = "SELECT host_name FROM vm_data"
    print(query)
    result = cursor.execute(query)
    if result > 0:
        host_list = cursor.fetchall()
        print(host_list)
        return render_template('actions.html', hosts=host_list)

    return render_template('actions.html')


@app.route('/disk_usage')
def disk_usage():
    data = subprocess.Popen(["./calvin.sh", "df"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = data.communicate()
    if stderr:
        raise Exception("Error "+str(stderr))
    data_str = stdout.decode('utf-8')
    print(data_str)
    return render_template('disk_usage.html', output=data_str)


@app.route('/processes')
def processes():
    data = subprocess.Popen(["./calvin.sh", "ps"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = data.communicate()
    if stderr:
        raise Exception("Error "+str(stderr))
    data_str = stdout.decode('utf-8')
    print(data_str)
    return render_template('processes.html', output=data_str)


@app.route('/netstat_i')
def netstat_i():
    return render_template('netstat_i.html')


@app.route('/netstat_r')
def netstat_r():
    return render_template('netstat_r.html')


@app.route('/ifconfig')
def ifconig():
    data = subprocess.Popen(["./calvin.sh", "ifconfig"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = data.communicate()
    if stderr:
        raise Exception("Error "+str(stderr))
    data_str = stdout.decode('utf-8')
    print(data_str)
    return render_template('ifconfig.html', output=data_str)


@app.route('/passwd')
def passwd():
    return render_template('passwd.html')


@app.route("/about")
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
