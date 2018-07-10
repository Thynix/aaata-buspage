# Bus Stop Page

This exists to reduce the number of steps to find when the bus will arrive. Instead of having to select the stop or
route again to get updated times, one need only refresh the page.

## Screenshot

![Screenshot](/screenshot.png)

## Setup

Requires [`Flask`](https://pypi.org/project/Flask/1.0.2/), [`requests`](https://pypi.org/project/requests/), and
[`transitfeed`](https://pypi.org/project/transitfeed/). Install these (ideally in a virtualenv or at least `--user` to
avoid elevating) with `pip install -r requirements.txt`.

`google_transit.zip` must exist - fetch it from [http://www.theride.org/google/google_transit.zip](here). The
[associated ToS]() notes:

> You have an obligation to keep schedule information up to date. Our customers depend on accurate information. Outdated
> schedules can mean missed buses or poorly timed connections. We require developers to update their data within three
> business days of a new file becoming available. You're not allowed to use AAATA/TheRide logos or other intellectual
> property. While the schedule data is provided free for your use, our logo and other registered service marks and
> trademarks remain the property of AAATA/TheRide.

Setting up a periodic job to check for updates is therefore a good idea. 

To deploy this, copy `bus.wsgi` to somewhere in your webroot, then set up the Flask WSGI app. `bus.wsgi` assumes this
project is cloned to `bus` under a `buspage` user. Copy `sample_config.py` to `config.py`, and set the API key.

On Apache 2, the necessary `VirtualHost` additions look like:

        WSGIDaemonProcess buspage user=buspage
        WSGIScriptReloading On
        WSGIScriptAlias /bus /var/www/bus/bus.wsgi process-group=buspage application-group=%{GLOBAL}

        <Directory /var/www/bus>
                WSGIProcessGroup buspage
                WSGIApplicationGroup %{GLOBAL}
                Require all granted
        </Directory>

## Testing

Run from the root of this repository with something like `env FLASK_APP=bus FLASK_DEBUG=1 flask run`
