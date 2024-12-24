# Define a list of names
""" names = ["Harry", "Ron", "Hermione", "Ginny"]
names.append("Draco")
names.sort()
print(names) """

""" s = set()
s.add(7)
s.add(6)
s.add(7)
s.add(10)

s.remove(6)
print(s) """

from flask import Flask, render_template, redirect, url_for, flash, request
from wtforms import StringField, SelectField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key = "your_secret_key"  # Necessary for Flask-WTF forms

# Track user balance globally (simple implementation for demo purposes)
user_balance = {"current_balance": 0}

class HomeForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    flightnumber = SelectField('Flight Number:', 
                               choices=[('flight101', 'Flight 101'), 
                                        ('flight102', 'Flight 102'), 
                                        ('flight103', 'Flight 103')])
    submit = SubmitField('Book Flight')

class DepositForm(FlaskForm):
    deposit_amount = StringField('Deposit Amount:', validators=[DataRequired()])
    deposit = SubmitField('Deposit')

class Flight:
    def __init__(self, capacity, price):
        self.capacity = capacity
        self.price = price
        self.passengers = []

    def add_passenger(self, name):
        if self.open_seats() > 0:
            self.passengers.append(name)
            return True
        return False

    def open_seats(self):
        return self.capacity - len(self.passengers)

# Define flights and prices
flights = {
    "flight101": Flight(30, 100),  # Example: Capacity 30, Price 100
    "flight102": Flight(40, 150),  # Example: Capacity 40, Price 150
    "flight103": Flight(100, 1200) # Example: Capacity 100, Price 1200
}

@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    form = HomeForm()
    if form.validate_on_submit():
        name = form.name.data
        flight_number = form.flightnumber.data
        flight = flights.get(flight_number)

        # Check if flight exists and user has enough balance
        if flight:
            if user_balance["current_balance"] >= flight.price:
                if flight.add_passenger(name):
                    # Deduct flight price from balance
                    user_balance["current_balance"] -= flight.price
                    flash(f"{name} added to {flight_number} successfully! Remaining balance: ${user_balance['current_balance']}", "success")
                else:
                    flash(f"Flight {flight_number} is full. Please try another flight.", "danger")
            else:
                flash(f"Insufficient balance for {flight_number}. Please deposit more funds.", "warning")
        else:
            flash(f"Invalid flight selected.", "danger")
        return redirect(url_for("home"))

    return render_template("index.html", form=form, balance=user_balance["current_balance"])

@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    form = DepositForm()
    if form.validate_on_submit():
        try:
            deposit_amount = int(form.deposit_amount.data)
            if deposit_amount > 0:
                user_balance["current_balance"] += deposit_amount
                flash(f"Successfully deposited ${deposit_amount}. Current balance: ${user_balance['current_balance']}", "success")
                return redirect(url_for("home"))
            else:
                flash("Deposit amount must be greater than 0.", "warning")
        except ValueError:
            flash("Invalid deposit amount. Please enter a valid number.", "danger")

    return render_template("deposit.html", form=form, balance=user_balance["current_balance"])
print(app.config)
if __name__ == "__main__":
    app.run(debug=True)