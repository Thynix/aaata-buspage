from flask import Flask, render_template
import requests
import json

app = Flask(__name__)

stop_ids = [
472,
1804,
]
stops_endpoint = "http://www.theride.org/DesktopModules/AATA.Endpoint/proxy.ashx?method=predictionsforstop&stpid={}"

@app.route("/")
def showSchedules():
    stops = []
    for stop_id in stop_ids:
        url = stops_endpoint.format(stop_id)
        r = requests.get(url)

        if r.status_code != 200:
            return "Request for {} failed with code {}: {}".format(url, r.status_code, r.text)

        schedule = r.json()
        arrivals = []
        for arrival in schedule["bustime-response"]["prd"]:
            arrivals.append({
                             "number": arrival["rt"],
                             "route": arrival["typ"],
                             "predicted": arrival["prdtm"],
                             "scheduled": arrival["schdtm"],
            })

        stops.append(arrivals)

    return render_template("bus.html", stops=stops)