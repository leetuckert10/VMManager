# mini_project.py
import subprocess
from subprocess import Popen, PIPE
from subprocess import check_output
from flask import Flask, render_template, request, session, flash
from flask_bootstrap import Bootstrap
from typing import List, Tuple
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import paramiko
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

# Configure paramiko
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

host_list: Tuple = ()
user_list: Tuple = ()
host_name = ""
message = ""


@app.route('/')
def home() -> str:
    return render_template('index.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        global host_list
        global user_list
        try:
            form = request.form
            login_id = form["login_id"]
            password = form["password"]
            cursor = mysql.connection.cursor()
            query = f"SELECT * FROM user WHERE login_id = '{login_id}'" \
                    f" AND password = '{password}'"
            result = cursor.execute(query)
            print(query)
            if result == 0:
                flash("Login failed!", 'danger')
                return render_template('login.html')
            else:
                print("**************LOADING ACTIONS*****************")
                user_list = cursor.fetchall()
                cursor.close()
                host_list = get_database_data()
                print(host_list)
                return render_template('actions.html', hosts=host_list)
        except mysql.connection.Error as err:
            print(err)
            flash("Login failed!", 'danger')
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route("/redirect", methods=["GET", "POST"])
def redirect():
    global message
    global host_name
    if request.method == "POST":
        host_name = request.form.get("host_name")
        message = f"Executing commands on {host_name}..."
        print(f"***{message}***")

    return render_template('actions.html', hosts=host_list, message=message)


@app.route('/actions', methods=["GET", "POST"])
def actions(hosts):
    print("*****************IN ACTIONS*********************")
    if request.medhod == "POST":
        value = request.form.get['vm_host']
        print(f"******************{value}************************")
    else:
        return render_template('actions.html', hosts=hosts)


@app.route('/disk_usage')
def disk_usage():
    try:
        connect_host()
    except:
        exception_str = "Authentication Error!"
        return render_template('ifconfig.html', output=exception_str)

    stdin, stdout, stderr = ssh_client.exec_command("df -H")
    retstr = f"HOST: {host_name}\n{format_output(stdout, stderr)}"
    return render_template('disk_usage.html', output=retstr)


@app.route('/processes')
def processes():
    try:
        connect_host()
    except:
        exception_str = "Authentication Error!"
        return render_template('ifconfig.html', output=exception_str)

    stdin, stdout, stderr = ssh_client.exec_command("ps uwax")
    retstr = f"HOST: {host_name}\n{format_output(stdout, stderr)}"
    return render_template('processes.html', output=retstr)


@app.route('/netstat_i')
def netstat_i():
    try:
        connect_host()
    except:
        exception_str = "Authentication Error!"
        return render_template('ifconfig.html', output=exception_str)

    stdin, stdout, stderr = ssh_client.exec_command("netstat -i")
    retstr = f"HOST: {host_name}\n{format_output(stdout, stderr)}"
    return render_template('netstat_i.html', output=retstr)


@app.route('/netstat_r')
def netstat_r():
    try:
        connect_host()
    except:
        exception_str = "Authentication Error!"
        return render_template('ifconfig.html', output=exception_str)

    stdin, stdout, stderr = ssh_client.exec_command("netstat -r")
    retstr = f"HOST: {host_name}\n{format_output(stdout, stderr)}"
    return render_template('netstat_r.html', output=retstr)


@app.route('/ifconfig')
def ifconfig():
    try:
        connect_host()
    except:
        exception_str = "Authentication Error!"
        return render_template('ifconfig.html', output=exception_str)

    stdin, stdout, stderr = ssh_client.exec_command("ifconfig")
    retstr = f"HOST: {host_name}\n{format_output(stdout, stderr)}"
    return render_template('ifconfig.html', output=retstr)


@app.route('/passwd')
def passwd():
    try:
        connect_host()
    except:
        exception_str = "Authentication Error!"
        return render_template('ifconfig.html', output=exception_str)

    stdin, stdout, stderr = ssh_client.exec_command("cat /etc/passwd")

    retstr = f"HOST: {host_name}\n{format_output(stdout, stderr)}"
    return render_template('passwd.html', output=retstr)


@app.route("/about")
def about():
    return render_template('about.html')


def get_database_data():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM vm_data"
    print(query)
    result = cursor.execute(query)
    if result > 0:
        return cursor.fetchall()

    return None


def format_output(output, error):
    error_list = error.readlines()
    output_list = output.readlines()
    retstr = ""

    if error_list:
        for line in error_list:
            retstr = retstr + line
    else:
        for line in output_list:
            retstr = retstr + line
    return retstr


def connect_host():
    ip_address: str = ""
    for data in host_list:
        if data.get("host_name") == host_name:
            ip_address = data.get("ip_address")
            break

    ssh_client.connect(
        hostname=ip_address,
        username=user_list[0].get('login_id'),
        password=user_list[0].get('password'))


if __name__ == '__main__':
    app.run(debug=True)
