from flask import Flask, render_template, redirect, request
import requests

app = Flask(__name__)

default_stop_ids = [
    472,
    1804,
]
stops_endpoint = "http://www.theride.org/DesktopModules/AATA.Endpoint/proxy.ashx?method=predictionsforstop&stpid={}"


@app.route("/")
def home():
    return redirect("/show?stops={}".format(",".join(map(str, default_stop_ids))))


@app.route("/show")
def show_schedules():
    if "stops" not in request.args:
        return redirect("/")

    stops = []
    for stop_id in map(int, request.args["stops"].split(",")):
        url = stops_endpoint.format(stop_id)
        r = requests.get(url)

        if r.status_code != 200:
            return "Request for {} failed with code {}: {}".format(url, r.status_code, r.text)

        arrivals = []
        schedule = r.json()["bustime-response"]

        if "error" in schedule:
            return "Got error for stop {}: {}".format(stop_id, schedule["error"]["msg"])

        predictions = schedule["prd"]

        # If there is a single prediction it is given directly, not in a list with one element.
        if isinstance(predictions, dict):
            stop_name = predictions["stpnm"]
            arrivals.append(parse_arrival(predictions))
        else:
            assert isinstance(predictions, list)
            assert len(predictions) > 0
            stop_name = predictions[0]["stpnm"]
            for arrival in predictions:
                arrivals.append(parse_arrival(arrival))

        stops.append({
                      "name": stop_name,
                      "arrivals": arrivals,
        })

    return render_template("bus.html", stops=stops)


def parse_arrival(arrival):
    return {
        "route": arrival["rt"] + arrival["des"],
        "predicted": arrival["prdtm"],
        "scheduled": arrival["schdtm"],
    }
