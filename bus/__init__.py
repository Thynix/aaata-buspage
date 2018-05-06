from flask import Flask, render_template
import requests

app = Flask(__name__)

stop_ids = [
    472,
    1804,
]
stops_endpoint = "http://www.theride.org/DesktopModules/AATA.Endpoint/proxy.ashx?method=predictionsforstop&stpid={}"


@app.route("/")
def show_schedules():
    stops = []
    for stop_id in stop_ids:
        url = stops_endpoint.format(stop_id)
        r = requests.get(url)

        if r.status_code != 200:
            return "Request for {} failed with code {}: {}".format(url, r.status_code, r.text)

        schedule = r.json()
        predictions = schedule["bustime-response"]["prd"]
        arrivals = []
        # If there is a single prediction it is given directly, not in a list with one element.
        if isinstance(predictions, dict):
            arrival = predictions
            arrivals.append(parse_arrival(arrival))
        else:
            assert isinstance(predictions, list)
            assert len(predictions) > 0
            for arrival in predictions:
                arrivals.append(parse_arrival(arrival))

        stops.append({
                      "name": arrival["stpnm"],
                      "arrivals": arrivals,
        })

    return render_template("bus.html", stops=stops)


def parse_arrival(arrival):
    return {
        "route": arrival["rt"] + arrival["des"],
        "predicted": arrival["prdtm"],
        "scheduled": arrival["schdtm"],
    }
