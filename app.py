import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from function import apology, login_required, lookup, usdt, chart

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usdt"] = usdt

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///trade.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio"""

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    # catch username, cash from users
    username = rows[0]["username"]
    cash = float(rows[0]["cash"])

    # get value for each row in track table
    values = db.execute("SELECT * FROM track WHERE username = ?", username)

    # update price for each coin
    for value in values:
        symbol = value["symbol"]
        price = float(lookup(value["symbol"])["price"])
        total_p = float(value["shares"] * price)
        db.execute("UPDATE track SET price =:price, total_p =:total_p WHERE symbol = :symbol AND username =:username",
                   price=price, symbol=symbol, total_p=total_p, username=username)

    # get total price for all transaction
    total = db.execute("SELECT SUM(shares*price) FROM track WHERE username = ? GROUP BY username", username)
    # get first attribute from total list then get value of dict
    if len(total) != 0:
        subtotal = float(total[0]['SUM(shares*price)'])
    else:
        subtotal = 0
    grandtotal = cash + subtotal

    # render index page
    return render_template("index.html", values=values, cash=cash, grandtotal=grandtotal)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy coin"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        share = request.form.get("shares")

        # if user input blank symbol
        if not symbol:
            return apology("Missing symbol")

        quote = lookup(symbol)
        # if user input invalid symbol
        if quote == None:
            return apology("Invalid symbol")

        # if user input blank share
        if not share:
            return apology("Missing shares")

        if not share.isdigit():
            return apology("Can not purchase share in fractional, negative, and non-numeric")

        # get total price
        total = float(share)*quote["price"]

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # catch username, cash from users
        username = rows[0]["username"]
        cash = rows[0]["cash"]

        # if total price > cash
        if total > cash:
            return apology("Not enough cash")

        # get value for each row in track table

        track = db.execute("SELECT * FROM track WHERE username = ?", username)
        symbols = []
        for sb in track:
            symbols.append(sb["symbol"])

        if symbol not in symbols:
            # track buying amount into database
            db.execute("INSERT INTO track (username, symbol, name, shares, price, total_p) VALUES ( ?, ?, ?, ?, ?, ?)",
                       username, symbol, quote["name"], share, quote["price"], total)
        else:
            update_track = db.execute("SELECT SUM(shares) AS shares FROM track WHERE username = ? AND symbol = ?", username, symbol)
            update_share = update_track[0]["shares"] + int(share)
            update_total = update_share * quote["price"]
            db.execute("UPDATE track SET shares=:update_share, total_p=:update_total WHERE username =:username AND symbol =:symbol",
                       update_share=update_share, update_total=update_total, username=username, symbol=symbol)
        db.execute("INSERT INTO trans (username, symbol, shares, price) VALUES ( ?, ?, ?, ?)",
                   username, symbol, share, quote["price"])

        # update left cash amount into "users" table
        cash = cash - total
        db.execute("UPDATE users SET cash =:cash WHERE id = :id", cash=cash, id=session["user_id"])
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    # catch username from users
    username = rows[0]["username"]

    # get value for each row in track table
    values = db.execute("SELECT * FROM trans WHERE username = ?", username)

    # render index page
    return render_template("history.html", values=values)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get coin quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")

        # if user input blank symbol
        if not symbol:
            return apology("Missing symbol")
        quote = lookup(symbol)

        # get the name of coin then visualize history data
        coin_name = quote["name"].lower()
        charted = chart(coin_name)

        # if user input invalid symbol
        if quote == None:
            return apology("Invalid symbol")

        if charted == None:
            charted = "Cannot find name id of this coin"

        return render_template("quoted.html", quote=quote, charted=charted)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # if any field is left blank, return an apology
        if not username or not password:
            return apology("Do not leave the field blank")

        # if password and confirmation don't match, return an apology
        elif password != request.form.get("confirmation"):
            return apology("Password is not match")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # if the username is already taken, return an apology
        if len(rows) != 0:
            return apology("Username is already taken")

        # register new user into database
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO users (username,hash) VALUES(?, ?)", username, hash)
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        symbol = request.form.get("symbol")
        share = request.form.get("shares")

        # if user input blank symbol
        if not symbol:
            return apology("Missing symbol")

        # if user input blank share
        if not share:
            return apology("Missing shares")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # catch username, cash from users
        username = rows[0]["username"]
        cash = rows[0]["cash"]

        # get symbol from database then check if user own it or not
        symbols_list = db.execute("SELECT symbol FROM track WHERE username = ?", username)
        symbols = []
        for sb in symbols_list:
            symbols.append(sb["symbol"])
        if symbol not in symbols:
            return apology("You don't own that symbol")

        # get value for each row in track table
        values = db.execute("SELECT * FROM track WHERE username = ? AND symbol = ?", username, symbol)

        if int(share) > values[0]["shares"]:
            return apology("You don't have enough shares")

        # get total price
        total = int(share)*values[0]["price"]

        # update cash amount into "users" table
        cash = cash + total
        db.execute("UPDATE users SET cash =:cash WHERE id = :id", cash=cash, id=session["user_id"])

        # update remain shares into track table
        remain_share = values[0]["shares"] - int(share)
        remain_total = values[0]["total_p"] - total
        if remain_share > 0:
            db.execute("UPDATE track SET shares =:remain_share, total_p =:remain_total WHERE symbol =:symbol AND username =:username",
                       remain_share=remain_share, remain_total=remain_total, symbol=symbol, username=username)
        else:
            db.execute("DELETE FROM track WHERE symbol =:symbol AND username =:username", symbol=symbol, username=username)

        # update transaction buy
        sell_share = -int(share)
        price = values[0]["price"]
        db.execute("INSERT INTO trans (username, symbol, shares, price) VALUES ( ?, ?, ?, ?)", username, symbol, sell_share, price)

        return redirect("/")

    else:
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        username = rows[0]["username"]

        # get symbol of user
        symbols = db.execute("SELECT symbol FROM track WHERE username = ?", username)

        return render_template("sell.html", symbols=symbols)


@app.route("/favorites", methods=["GET", "POST"])
@login_required
def favorites():
    """List of favorite coins"""
    if request.method == "POST":
        symbol = request.form.get("symbol")

        # if user input blank symbol
        if not symbol:
            return apology("Missing symbol")

        quote = lookup(symbol)
        # if user input invalid symbol
        if quote == None:
            return apology("Invalid symbol")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # catch username from users
        username = rows[0]["username"]

        # get value for each row in favor table
        track = db.execute("SELECT * FROM favorite WHERE username = ?", username)
        symbols = []
        for sb in track:
            symbols.append(sb["symbol"])

        if symbol not in symbols:
            # add coin into favorites
            db.execute("INSERT INTO favorite (username, symbol, name, price, volumne, marketcap, fdv) VALUES ( ?, ?, ?, ?, ?, ?, ?)",
                        username, symbol, quote["name"], quote["price"], quote["volumne"], quote["marketcap"], quote["fdv"])

        return redirect("/favorites")
    else:
        """Show list of favorite"""

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        username = rows[0]["username"]

        # get value for each row in favor table
        values = db.execute("SELECT * FROM favorite WHERE username = ?", username)

        # render favorites page
        return render_template("favorites.html", values=values)


@app.route("/about")
@login_required
def about():
    """Introduction"""

    # render about page
    return render_template("about.html")