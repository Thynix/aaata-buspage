from flask import Flask, render_template, redirect, request, url_for
import collections
import datetime
import requests
import transitfeed


app = Flask(__name__)
app.config.from_object('config')

default_stop_ids = [
    472,
    1804,
]
stops_endpoint = "http://rt.theride.org/bustime/api/v3/getpredictions?key={}&format=json&stpid={{}}".format(
    app.config["API_KEY"]
)

# Lists of stop interpolations keyed by stop_id, keyed by trip_id.
transit_times = dict()


@app.before_first_request
def load():
    # This takes many seconds to load, so it's not appropriate to do on each request.
    # TODO: Could cache result with hash of input file if there's a need to speed up loading.
    app.logger.info("loading transit feed")
    feed = transitfeed.Loader("google_transit.zip")
    transit_schedule = feed.Load()
    app.logger.info("loaded transit feed; processing")

    for trip in transit_schedule.GetTripList():
        trip_times = transit_times[trip.trip_id] = collections.defaultdict(list)

        for interpolated_stop in trip.GetTimeInterpolatedStops():
            stop_seconds, stop, is_timepoint = interpolated_stop
            trip_times[stop.stop_id].append(interpolated_stop)

    app.logger.info("processed transit feed")


@app.route("/")
def home():
    return redirect(url_for("show_schedules") + "?stops={}".format(",".join(map(str, default_stop_ids))))


@app.route("/show")
def show_schedules():
    if "stops" not in request.args:
        return redirect(url_for("home"))

    stops = []
    for stop_id in map(int, request.args["stops"].split(",")):
        url = stops_endpoint.format(stop_id)
        r = requests.get(url)

        if r.status_code != 200:
            stops.append({
                "id": stop_id,
                "msg": "Request failed with code {}: {}".format(r.status_code, r.text),
            })
            continue

        arrivals = []
        schedule = r.json()["bustime-response"]

        if "error" in schedule:
            stops.append({
                "id": stop_id,
                "error": schedule["error"][0]["msg"],
            })
            continue

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
    # It does not appear to be prohibited for a given trip to have multiple arrivals to the same stop, as a loop could,
    # so it's ambiguous which scheduled time the prediction corresponds to. Display all arrivals by the trip referenced
    # by the prediction to the stop. In practice it seems likely that a loop would be broken into multiple route
    # directions.
    scheduled_times = []
    for stop_seconds, stop, is_timepoint in transit_times[arrival["tatripid"]][arrival["stpid"]]:
        # It's ambiguous which day the scheduled arrival time is relative to, as it's not necessarily the same as that
        # of the predicted arrival, so might as well use today.
        today = datetime.date.today()
        scheduled_times.append(datetime.datetime(today.year, today.month, today.day) +
                               datetime.timedelta(seconds=stop_seconds))

    return {
        "route": arrival["rt"] + arrival["des"],
        "predicted": parse_datetime(arrival["prdtm"]),
        "scheduled": ",".join(map(str, scheduled_times)),
    }


def parse_datetime(timestamp):
    return datetime.datetime.strptime(timestamp, "%Y%m%d %H:%M").strftime("%Y-%m-%d %H:%M")
