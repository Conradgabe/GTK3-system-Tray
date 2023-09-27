import requests
import sys
import json
import os
import gi


gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, Gio
from gi.repository import AppIndicator3 as AppIndicator
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_SECRET_KEY = os.environ.get("API_SECRET_KEY")
EXCHANGE_SECRET_KEY = os.environ.get("EXCHANGE_SECRET_KEY")

CURRENT_DATE = datetime.now()

YEAR = CURRENT_DATE.year
MONTH = CURRENT_DATE.month
DAY = CURRENT_DATE.day


class WeatherTrayApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='org.gtk.WeatherTrayApp', flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.create_icon()

    def create_icon(self):
        # Create a status icon
       self.indicator = AppIndicator.Indicator.new(
                "Weather-Indicator",
                "Weather",
                AppIndicator.IndicatorCategory.APPLICATION_STATUS,
            )
       self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

    def do_activate(self):
        # Create a menu with a submenu for Naira exchange value
        self.menu = Gtk.Menu()
        self.menu_item = Gtk.MenuItem(label="Get Naira Exchange Value")
        self.menu.append(self.menu_item)
        self.menu_item = Gtk.MenuItem(label="Get Weather Detail")
        self.menu.append(self.menu_item)
        self.menu_item.connect("activate", self.get_current_naira_value)
        self.menu_item.connect("activate", self.get_weather)

        self.indicator.set_menu(self.menu)

        window = Gtk.ApplicationWindow(application=self, title="Gtk Weather App")
        window.set_default_size(500, 500)

        label = Gtk.Label(label="Gtk Info")
        window.add(label)

        w_data = self.get_weather()
        c_data = self.get_current_naira_value()

        label.set_text(w_data + c_data)

        window.show_all()

    def get_weather(self):
        try:
            response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=Nigeria&appid=" + API_SECRET_KEY)
            response.raise_for_status()
            data = json.loads(response.text)
            weather = data["weather"][0]["description"]
            temperature = data["main"]["temp"]

            if data["weather"][0]["main"] == "Rain":
                result = f"Weather: Its going to rain today: Temperature: {temperature}°C\n"
            else:
                result = f"Weather: {weather}, Temperature: {temperature}°C\n"
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
        return result
    
    def get_current_naira_value(self):
        try:
            header = {"apikey": EXCHANGE_SECRET_KEY}
            response = requests.get(f"https://api.apilayer.com/currency_data/convert?from=USD&to=NGN&amount=1&date={YEAR}-0{MONTH}-{DAY}", headers=header)
            response.raise_for_status()
            data = json.loads(response.text)
            current_price = data["result"]
            
            formatted_price = "{:.2f}".format(current_price)
            result = f"Naira Value: $1 to N{formatted_price}k\n"
        except requests.exceptions.RequestException as e:
            print(f"Error fetching currency data: {e}")
        return result


if __name__ == "__main__":
    app = WeatherTrayApp()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
