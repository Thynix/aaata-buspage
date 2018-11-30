# Bus Stop Page

This exists to reduce the number of steps to find when the bus will arrive. Instead of having to select the stop or
route again to get updated times, one need only refresh the page.

*NOTE*: This doesn't yet provide an automated method for keeping the transit data up-to-date, which is required by AAATA's ToS.

## Screenshot

![Screenshot](/screenshot.png)

## Setup

Requires [`Flask`](https://pypi.org/project/Flask/1.0.2/), [`requests`](https://pypi.org/project/requests/),
[`transitfeed`](https://pypi.org/project/transitfeed/), and Python 2 (because `transitfeed` does). Install these
in a virtualenv with (after activating the virtualenv)`pip install -r requirements.txt`.

`google_transit.zip` must exist - fetch it from [https://www.theride.org/google/google_transit.zip](here). An
[associated page](https://www.theride.org/AboutUs/For-Developers/Developer-Files) notes in part:

> You have an obligation to keep schedule information up to date. Our customers depend on accurate information. Outdated
> schedules can mean missed buses or poorly timed connections. We require developers to update their data within three
> business days of a new file becoming available. You're not allowed to use AAATA/TheRide logos or other intellectual
> property. While the schedule data is provided free for your use, our logo and other registered service marks and
> trademarks remain the property of AAATA/TheRide.

Setting up a periodic job to check for updates is therefore a good idea. The `bus_update_service` directory contains a
script and associated systemd configuration to check for modifications to the file and reload the file when it changes.
To set up the timer, copy FIXME

To deploy this, copy `bus.wsgi` to somewhere in your webroot, then set up the Flask WSGI app. The example configuration
assumes this project is cloned to a `aaata-buspage` directory under a `buspage` user. Copy `sample_config.py` to
`config.py`, and set its values.

For Apache 2 on Debian, `mod_wgsi` for Python 2 is packaged as `libapache2-mod-wsgi`, and the necessary additions
within the relevant `VirtualHost` look something like:

        WSGIDaemonProcess buspage user=buspage python-home=/home/buspage/venv home=/home/buspage/aaata-buspage
        WSGIScriptAlias /bus /var/www/bus/bus.wsgi process-group=buspage application-group=buspage

## Testing

Run from the root of this repository with something like `env FLASK_APP=bus FLASK_DEBUG=1 flask run`
