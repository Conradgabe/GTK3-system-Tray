import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gio
import requests
import json

class WeatherTrayApp:
    def __init__(self):
        self.icon = Gtk.StatusIcon()
        self.icon.set_from_file("icon.png")
        self.icon.connect("activate", self.on_activate)

    def on_activate(self, icon):
        response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=London&appid=" + API_SECRET_KEY)
        data = json.loads(response.text)
        weather = data["weather"][0]["description"]
        self.icon.set_tooltip_text(f"Weather: {weather}")

if __name__ == "__main__":
    app = WeatherTrayApp()
    Gtk.main()