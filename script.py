import requests
import json
import os
import gi

os.environ["LC_ALL"] = "C"

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf, Gio
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_SECRET_KEY = os.environ.get("API_SECRET_KEY")
EXCHANGE_SECRET_KEY = os.environ.get("EXCHANGE_SECRET_KEY")

CURRENT_DATE = datetime.now()

YEAR = CURRENT_DATE.year
MONTH = CURRENT_DATE.month
DAY = CURRENT_DATE.day


class WeatherTrayApp(Gio.application):
    def __init__(self):
        super().__init__(application_id='org.gtk.WeatherTrayApp', flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.activate)

    def create_icon(self):
        # Create a status icon
        self.icon = Gtk.StatusIcon()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file("./icon.png")
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.icon.set_from_pixbuf(pixbuf)

    def activate(self):
        self.create_icon()
        self.window = Gtk.ApplicationWindow(application=self, title="GTK Weather App")
        self.window.set_default_size(200, 200)

        self.icon.set_from_icon_name("weather-clear")
        self.icon.connect("activate", self.on_activate)
        self.icon.set_visible(True)

        # Create a menu with a submenu for Naira exchange value
        self.menu = Gtk.Menu()
        self.menu_item = Gtk.MenuItem(label="Get Naira Exchange Value")
        self.menu.append(self.menu_item)
        self.menu_item.connect("activate", self.get_current_naira_value)

        self.icon.set_menu(self.menu)

        # Add the status icon to the system tray
        self.tray_manager = Gtk.StatusIconTrayManager()
        self.tray_manager.add_icon(self.icon)

        self.window.show_all()

    def on_activate(self):
        try:
            response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=Nigeria&appid=" + API_SECRET_KEY)
            response.raise_for_status()
            data = json.loads(response.text)
            weather = data["weather"][0]["description"]
            temperature = data["main"]["temp"]

            if data["weather"][0]["main"] == "Rain":
                self.icon.set_tooltip_text(f"Weather: Its going to rain today and the Temperature is {temperature}°C")
            else:
                self.icon.set_tooltip_text(f"Weather: {weather} and the temperature is {temperature}°C")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")

        return data
    
    def get_current_naira_value(self):
        try:
            header = {"apikey": EXCHANGE_SECRET_KEY}
            response = requests.get(f"https://api.apilayer.com/currency_data/convert?from=USD&to=NGN&amount=1&date={YEAR}-0{MONTH}-{DAY}", headers=header)
            response.raise_for_status()
            data = json.loads(response.text)
            current_price = data["result"]

            self.icon.set_tooltip_text(f"Current Naira Exchange value from dollar: $1 to N{current_price}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")

        return data


if __name__ == "__main__":
    app = WeatherTrayApp()
    app.run()