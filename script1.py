from flask import Flask, render_template, flash, redirect, request, session, abort
import os
from bokeh.layouts import column
from bokeh.plotting import figure
from pandas_datareader import data
from bokeh.embed import components
from bokeh.resources import CDN
import datetime
from flask_sqlalchemy import SQLAlchemy
from send_email import send_email
from sqlalchemy.sql import func


#TODO HOOK UP SIGNUP PAGE TO SIGNUP.html *DONE
#TODO HOOK UP SUCCESS PAGE TO SUCCESS.HTML *DONE
#TODO FIX SIGNUP.HTML *DONE
#TODO FIX SUCCESS.html *DONE
#TODO attach login function to pull from postgres database *DONE
#TODO FIX SIGNUP FUNCTION *DONE
#TODO FIX SUCCESS FUNCTION *DONE
#TODO WRITE send_email PYTHON SCRIPT AND FIX IT *DONE
#TODO hash passwords
#TODO clean up .css files for login, success, signup pages

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://***********:***********@localhost/userdata'
db = SQLAlchemy(app)


# creates the database
class Data(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key=True)
    email_ = db.Column(db.String(120))
    username_ = db.Column(db.String(30), unique=True)
    password_ = db.Column(db.String(30))

    def __init__(self, email_, username_, password_):
        self.email_ = email_
        self.username_ = username_
        self.password_ = password_


@app.route("/signup")
def signup():
    return render_template("signup.html")


# uses POST method to submit email, username, password information to database
@app.route("/success", methods=["POST"])
def success():
    if request.method == "POST":
        email = request.form["email_name"]
        username = request.form["user_name"]
        password = request.form["password"]
        # if statement to check if username is already in the database
        if db.session.query(Data).filter(Data.username_ == username).count() == 0:
            data = Data(email, username, password)
            db.session.add(data)
            db.session.commit()
            # call send_email function to send user their login data
            send_email(email, username, password)
            return render_template("success.html")
    return render_template("signup.html", text="That username is taken!")


@app.route('/login', methods=['GET', 'POST'])
def do_admin_login():

    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    query = db.session.query(Data).filter(Data.username_ == POST_USERNAME, Data.password_ == POST_PASSWORD )
    result = query.first()
    if result:
        session['logged_in'] = True
        return redirect('/')
    else:
        flash('Incorrect username/password.')
        return render_template('login.html')


@app.route("/logout/")
def logout():
    session['logged_in'] = False
    return redirect('/')


@app.route('/plot/')
def plot():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        """
        Script that uses pandas_datareader library to pull stock price information from Yahoo! Finance,
            then plots it to a candlestick chart using bokeh.plotting. This script compares Google and Apple.
        """

        # stock comparison dates
        start = datetime.datetime(2017, 5, 1)
        end = datetime.datetime(2017, 11, 30)

        # continually tries to pull data from yahoo until it is successful
        while True:
            try:
                # Google dataframe
                dfg = data.DataReader(name="GOOG", data_source='yahoo', start=start, end=end)
                # Apple dataframe
                dfa = data.DataReader(name="AAPL", data_source='yahoo', start=start, end=end)
            except:
                continue
            break

        # convert hours to milliseconds to use datetime
        hours_12 = 12 * 60 * 60 * 1000

        # function to add status column
        def inc_dec(c, o):
            if c > o:
                value = "Increase"
            elif c < o:
                value = "Decrease"
            else:
                value = "Equal"
            return value

        # Add new columns to google dataframe
        dfg["Status"] = [inc_dec(c, o) for c, o in zip(dfg.Close, dfg.Open)]
        dfg["Middle"] = (dfg.Open + dfg.Close) / 2
        dfg["Height"] = abs(dfg.Close - dfg.Open)

        # Add new columns to apple dataframe
        dfa["Status"] = [inc_dec(c, o) for c, o in zip(dfa.Close, dfa.Open)]
        dfa["Middle"] = (dfa.Open + dfa.Close) / 2
        dfa["Height"] = abs(dfa.Close - dfa.Open)

        # Create google candlestick plot
        s1 = figure(x_axis_type='datetime', width=1300, height=300, responsive=True)
        s1.title.text = "Google Stock Performace 2017"
        s1.grid.grid_line_alpha = 0.3

        # segment that plots from high to low point
        s1.segment(dfg.index, dfg.High, dfg.index, dfg.Low, color="black")

        # rectangles that plot open and closing, and color depending on if the day was a net loss or net gain
        s1.rect(dfg.index[dfg.Status == "Increase"], dfg.Middle[dfg.Status == "Increase"], hours_12,
                dfg.Height[dfg.Status == "Increase"], fill_color="#228B22", line_color="black")
        s1.rect(dfg.index[dfg.Status == "Decrease"], dfg.Middle[dfg.Status == "Decrease"], hours_12,
                dfg.Height[dfg.Status == "Decrease"], fill_color="#F08080", line_color="black")

        # Create apple candlestick plot
        s2 = figure(x_axis_type='datetime', width=1300, height=300, responsive=True)
        s2.title.text = "Apple Stock Performace 2017"
        s2.grid.grid_line_alpha = 0.3

        # segment that plots from high to low point
        s2.segment(dfa.index, dfa.High, dfa.index, dfa.Low, color="black")

        # rectangles that plot open and closing, and color depending on if the day was a net loss or net gain
        s2.rect(dfa.index[dfa.Status == "Increase"], dfa.Middle[dfa.Status == "Increase"], hours_12,
                dfa.Height[dfa.Status == "Increase"], fill_color="#228B22", line_color="black")
        s2.rect(dfa.index[dfa.Status == "Decrease"], dfa.Middle[dfa.Status == "Decrease"], hours_12,
                dfa.Height[dfa.Status == "Decrease"], fill_color="#F08080", line_color="black")

        # put plots into column on single html page
        p = column(s1, s2)

        # create necessary embed variables and links
        script1, div1 = components(p)
        cdn_js = CDN.js_files[0]
        cdn_css = CDN.css_files[0]
        return render_template('plot.html', script1=script1, div1=div1, cdn_css=cdn_css, cdn_js=cdn_js)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('home.html')


@app.route('/about/')
def about():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('about.html')


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
