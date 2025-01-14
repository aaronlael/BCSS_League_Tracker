
# A very simple Flask Hello World app for you to get started with...
import datetime as dt
from db import add_player, get_players, update_player_place, update_tag_out, wrap_up
from flask import Flask, flash, render_template, request, redirect, url_for
import os
from payout import payout_manager

app = Flask(__name__)
app.secret_key = os.getenv("secret_key")


@app.route('/', methods=["GET", "POST"])
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
            "date": dt.date.today().strftime("%Y-%m-%d"),
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
def place_entry():
    data = []
    results = get_players(dt.date.today().strftime("%Y-%m-%d"))
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
            upd_tag = update_tag_out(dt.date.today().strftime("%Y-%m-%d"))
            if not upd_tag[0]:
                return upd_tag[1]
        pay = payout_manager(dt.date.today().strftime("%Y-%m-%d"))
        if not pay[0]:
            return pay[1]

        return redirect(url_for("wrap_up_view"))
    else:
        return render_template("entry.html", data=data)


@app.route('/wrapup', methods=["GET"])
def wrap_up_view():
    # add logic to retrieve users and get payout data
    data, err = wrap_up(dt.date.today().strftime("%Y-%m-%d"))
    if data:
        return render_template("postround.html", data=data)
    else:
        if err:
            return err
        else:
            return "maybe trying checking in some players first?"




