import wtforms.fields
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.form import Form
from wtforms.validators import DataRequired, URL, ValidationError
from flask_wtf import FlaskForm
import sqlite3


# Create the app using Flask
app = Flask(__name__)
Bootstrap(app)


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

conn = None


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


def to_dict(self):
    dictionary = {}
    for column in self.__table__.columns:
        dictionary[column.name] = getattr(self, column.name)
    return dictionary


def list_to_dict(self):
    list = {}
    dictionary = {}
    for row in range(0, len(self)):
        for column in self[row].__table__.columns:
            print(self[row].__table__.columns)
            print(column)
            dictionary[column.name] = getattr(self[row], column.name)
        list[row] = dictionary
    return list


def updateprice(cafe_id,coffee_price):
    global conn
    try:
        conn = sqlite3.connect('cafes.db')
        cursor = conn.cursor()
        print("Connected to SQLLite")
        sql_update_query = """UPDATE cafe SET coffee_price = ? WHERE id = ?"""
        data = (coffee_price, cafe_id)
        cursor.execute(sql_update_query, data)
        conn.commit()
        print("Record Updated Successfully")
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to update the coffee price", error)
    finally:
        if conn:
            conn.close()
            print("The sqlite is closed")


def delete_cafe(cafe_id):
    print(cafe_id)
    selected_cafe = Cafe.query.filter_by(id = cafe_id).first()
    db.session.delete(selected_cafe)
    db.session.commit()


# Create form
class MyTable(FlaskForm):
    app.secret_key = "YOUR_CSFR_TOKEN"
    name = StringField(label='Cafe name', validators=[DataRequired()])
    map_url = StringField(label='Maps (URL)', validators=[URL(message='Must be a valid URL'),DataRequired()])
    img_url = StringField(label='Photo', validators=[URL(message='Must be a valid URL'),DataRequired()])
    location = StringField(label='Location', validators=[DataRequired()])
    has_sockets = BooleanField(label='Has Sockets')
    has_toilet = BooleanField(label='Has Toilet')
    has_wifi = BooleanField(label='Has Wifi')
    can_take_calls = BooleanField(label='Can Take Calls')
    seats = SelectField(label='Seats', choices=["0-10", "10-20", "20-30", "30-40", "40-50", "50+"])
    coffee_price = StringField(label='Coffee Price', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

# Create index
@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/cafes')
def cafes():
    all_cafe = Cafe.query.all()
    return render_template('cafes.html', cafes=all_cafe)


@app.route('/add', methods=['GET','POST'])
def add():
    form = MyTable()
    if form.validate_on_submit():
        add_cafe = Cafe(
            name = form.name.data,
            map_url = form.map_url.data,
            img_url = form.img_url.data,
            location = form.location.data,
            has_sockets = form.has_sockets.data,
            has_toilet = form.has_toilet.data,
            has_wifi = form.has_wifi.data,
            can_take_calls = form.can_take_calls.data,
            seats = form.seats.data,
            coffee_price= form.coffee_price.data,
        )
        db.session.add(add_cafe)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)