# See http://www.theride.org/AboutUs/For-Developers for how to get an API key
API_KEY = YOUR_API_KEY

# Generate a password for triggering reload of the transit file.
RELOAD_PASSWORD =

# To avoid the need for system-level service re start privileges, the transit
# file update script triggers a reload by posting the password to this URI.
RELOAD_URI = "https://example.com/bus/reload"
