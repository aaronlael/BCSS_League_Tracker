import datetime as dt
from db import add_player, add_ctp, get_ctp, get_ctp_wrap, get_players, get_player_history, get_tag_history, get_tag_holders, update_player_place, update_tag_out, wrap_up, get_players_detailed, delete_player
from flask import Flask, flash, render_template, request, redirect, Response, url_for
import os
import pytz
from payout import payout_manager
from udisc_scrape import scrape_results_page

app = Flask(__name__)
app.secret_key = os.getenv("secret_key")
USERNAME =os.getenv("site_user")
PASSWORD = os.getenv("site_pw")
tz =pytz.timezone('America/Denver')

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


@app.route('/newscoreentry', methods=["GET", "POST"])
@requires_auth
def new_score_entry():
    # participants from entry form today
    participants = []
    results = get_players(dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d"))
    if results[0]:
        for result in results[0]:
            player = {
                "id" : result[0],
                "name" : result[1],
                "place" : None
                }
            participants.append(player)
    # Udisc Results today
    scraped_results = scrape_results_page()
    scraped_data = []
    for sr in scraped_results:
        if "T" in sr[0]:
            player = {
            "name" : sr[1],
            "place" : sr[0][1:]
            }
        else:
            player = {
                "name" : sr[1],
                "place" : sr[0]
                }
        scraped_data.append(player)
    if request.method == "POST":
        updated_data = []
        for i in range(len(participants)):
            new_value = request.form.get(f"value_{i}")
            participant = list(filter(lambda participant: str(participant['id']) == str(new_value), participants))[0]
            participant['name'] = scraped_data[i]['name']
            participant['place'] = scraped_data[i]['place']
            updated_data.append(participant)
        upd = update_player_place(updated_data)
        if upd[0]:
            upd_tag = update_tag_out(dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d"))
            if not upd_tag[0]:
                return upd_tag[1]
        pay = payout_manager(dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d"))
        if not pay[0]:
            return pay[1]
        return redirect(url_for("wrap_up_view"))

    else:
        data = {
            'participants' : participants,
            'scraped_data' : scraped_data
            }
        return render_template("new_entry.html", data=data)

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



@app.route('/ctpwrap', methods=["GET"])
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

@app.route('/ctpstub', methods=["GET"])
def ctp_stub():
    return render_template("ctpstub.html")


@app.route('/tagsummary', methods=["GET"])
@requires_auth
def tag_summary():
    tag_data, error = get_tag_holders()
    if error:
        return error
    else:
        tag_view_data = []
        for td in tag_data:
            tag_view_data.append({"name" : td[0], "tag" : td[1], "date" : td[2]})
        return render_template("tagsummary.html", data=tag_view_data)


@app.route('/tagsummary/player/<player>', methods=["GET"])
@requires_auth
def tag_summary_player(player):
    player = player.replace("_", " ")
    tag_data, error = get_player_history(player)
    if error:
        return error
    else:
        tag_view_data = []
        for td in tag_data:
            tag_view_data.append({"name" : td[0], "tag" : td[1], "date" : td[2]})
        return render_template("history.html", data=tag_view_data)


@app.route('/tagsummary/tag/<tag>', methods=["GET"])
@requires_auth
def tag_summary_tag(tag):
    tag_data, error = get_tag_history(tag)
    if error:
        return error
    else:
        tag_view_data = []
        for td in tag_data:
            tag_view_data.append({"name" : td[0], "tag" : td[1], "date" : td[2]})
        return render_template("history.html", data=tag_view_data)


@app.route('/editplayers', methods=["GET"])
@requires_auth
def day_of_review():
    today = dt.datetime.now(MOUNTAIN_TZ).strftime("%Y-%m-%d")
    players, error = get_players_detailed(today)
    if error:
        return error
    else:
        return render_template('edit_players.html', data=players)



@app.route('/delete_player/<id>', methods=["POST"])
@requires_auth
def delete_registered_player(id):
    player_name = request.form.get("name")
    if player_name:
        delete_player(id)
        flash(f"Player {player_name} has been deleted!")
    else:
        flash(f"You passed a null player, oopsie!")
    return redirect(url_for("day_of_review"))








