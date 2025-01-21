
# A very simple Flask Hello World app for you to get started with...
import datetime as dt
from db import add_player, add_ctp, get_ctp, get_ctp_wrap, get_players, update_player_place, update_tag_out, wrap_up
from flask import Flask, flash, render_template, request, redirect, Response, url_for
import os
import pytz
from payout import payout_manager

app = Flask(__name__)
app.secret_key = os.getenv("secret_key")
USERNAME =os.getenv("site_user")
PASSWORD = os.getenv("site_pw")

def check_auth(username, password):
    """Checks if the provided username and password are valid."""
    return username == USERNAME and password == PASSWORD

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    """Decorator to enforce authentication."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


MOUNTAIN_TZ = pytz.timezone('America/Denver')

@app.route('/', methods=["GET", "POST"])
@requires_auth
def inputUser():
    if request.method == "POST":
        name = request.form.get("name")  # Get data from the form
        tag = request.form.get("tag")
        if tag:
            tag_number = request.form.get("tagNumber")
        else:
            tag_number = None
        payout = request.form.get("payout") is not None #check if box is checked
        ctp1 = request.form.get("ctp1") is not None
        ctp2 = request.form.get("ctp2") is not None
        ace_pot = request.form.get("ace_pot") is not None
        player = {
            "date": dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d"),
            "name": name,
            "tag_in": tag_number if tag_number else None,
            "tag_out": None,
            "payout_in": 2 if payout else 0,
            "CTP1": 1 if ctp1 else 0,
            "CTP2": 1 if ctp2 else 0,
            "ace_pot": 1 if ace_pot else 0,
            "place": None,
            "payout_dollars": None
        }
        p = add_player(player)
        if p[0]:
            flash(f"you've entered for {name} successfully")
        else:
            flash(p[1])
        return redirect(url_for("inputUser"))

    else:
        return render_template("input.html")

@app.route('/data', methods=["GET", "POST"])
def data_parse():
    if request.method == "POST":
        pass
    else:
        return render_template("dataparse.html")


@app.route('/scoreentry', methods=["GET", "POST"])
@requires_auth
def place_entry():
    data = []
    results = get_players(dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d"))
    if results[0]:
        for result in results[0]:
            player = {
                "id" : result[0],
                "name" : result[1],
                "place" : None
                }
            data.append(player)

    if request.method == "POST":
        updated_data = []
        for item in data:
            new_value = request.form.get(f"value_{item['id']}")
            try:
                item["place"] = int(new_value) if new_value is not None else item["value"]
            except ValueError:
                print(f"Invalid input for item {item['id']}")
            updated_data.append(item)
        data = updated_data
        upd = update_player_place(data)
        if upd[0]:
            upd_tag = update_tag_out(dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d"))
            if not upd_tag[0]:
                return upd_tag[1]
        pay = payout_manager(dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d"))
        if not pay[0]:
            return pay[1]

        return redirect(url_for("wrap_up_view"))
    else:
        return render_template("entry.html", data=data)


@app.route('/wrapup', methods=["GET"])
@requires_auth
def wrap_up_view():
    # add logic to retrieve users and get payout data
    data, err = wrap_up(dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d"))
    if data:
        return render_template("postround.html", data=data)
    else:
        if err:
            return err
        else:
            return "maybe trying checking in some players first?"


@app.route('/ctp/<ctp>', methods=["GET", "POST"])
def ctp_entry(ctp):
    if request.method == "POST":
        name = request.form.get("new_name")
        ctp = request.form.get("ctp")
        ctp_update, error = add_ctp(name, ctp, dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d"))
        if error:
            return error
        else:
            flash(f"you've updated ctp {ctp} to {name} successfully")
            return redirect(url_for("ctp_entry", ctp=ctp))
    else:
        try:
            ctp = int(ctp)
        except ValueError:
            return "Nope."
        if ctp < 1 or ctp > 18:
            return "Also Nope."
        current_ctp, error = get_ctp(dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d"), ctp)
        if error:
            return error
        else:
            try:
                ctp_holder = current_ctp[0][0]
                ctp_holder_idx = current_ctp[0][1]
            except IndexError:
                ctp_holder = "Open"
                ctp_holder_idx = ""
            data = [{"ctp": ctp, "name" : ctp_holder, "id" : ctp_holder_idx}]
            return render_template("ctp.html", data=data)



@app.route('/ctpwrap')
@requires_auth
def ctp_wrap_up():
    today = dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d")
    ctp_data, error = get_ctp_wrap(today)
    if error:
        return error
    else:
        data_list = []
        for record in ctp_data:
            data_list.append({"name": record[1], "player": record[0]})
        return render_template("ctpwrap.html", data=data_list)




