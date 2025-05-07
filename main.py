# Weather App with API for real-time weather data in PyQt5
import sys

import requests # for api communication

from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import (QApplication,
                             QWidget, QLabel,
                             QPushButton,QVBoxLayout,
                             QLineEdit)
from PyQt5.QtCore import Qt

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather",self) # When we click on this button we'll make a request to an API
        self.temperature_label = QLabel(self) # We use this just as a placeholder to see what are we doing when applying CSS styling
        self.emoji_label = QLabel(self) # Also just a placeholder for testing
        self.description_label = QLabel(self) # Als another placeholder, will be deleted for the final run
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle("Weather App")
        self.setWindowIcon(QIcon("cloudy.png"))
        # adding a placeholder for textbox
        self.city_input.setPlaceholderText("...")
        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label") # adding the obj name for easier CSS access (by #id)
        self.city_input.setObjectName("city_input")
        self.description_label.setObjectName("description_label")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.get_weather_button.setObjectName("get_weather_button")

        # with name like QLabel and then {} we access the whole class, and with #obj_name we access the object by its id
        # we use Segoe UI emoji font-family to have colorful emojis and styled as well
        self.setStyleSheet("""
        QLabel, QPushButton{
        font-family: calibri;
        }
        
        QLabel#city_label{
        font-size:40px;
        font-style:italic;
        }
        QLineEdit#city_input{
        font-size:40px;
        }
        QPushButton#get_weather_button{
        font-size: 30px;
        font-weight: bold;
        }
        QLabel#temperature_label{
        font-size: 40px;
        font-weight: bold;
        }
        QLabel#emoji_label{
        font-size: 100px;
        font-family: Segoe UI emoji;
        }
        QLabel#description_label{
        font-size: 50px;
        }
        
        """)

        # SIGNAL/SLOT
        self.get_weather_button.clicked.connect(self.get_weather)


    def get_weather(self):
        api_key = "1757ab1d62c38a94a60253faaebf39fd"
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            data = response.json()
            response.raise_for_status() # in order to detect HTTP error between 400 and 500, and since our try/catch block doesn't cover that, we'll have to use raise_to_status() to rais the exception

            # print(data) - we are searching for 'cod': 200 or HTTP 200 OK it means that everything works fine and that we have response from server

            if data["cod"] == 200:
                self.display_weather(data)

        # EXCEPTION HANDLING
        except requests.exceptions.HTTPError as http_error: # this catches exceptions or HTTP errors between 400 and 500, like 404
            match response.status_code:
                case 400:
                    self.display_error("Bad request:\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized:\nInvalid API key")
                case 403:
                    self.display_error("Forbidden:\nAccess is denied")
                case 404:
                    self.display_error("Not found:\nCity not found")
                case 500:
                    self.display_error("Internal server error:\nPlease try again later")
                case 502:
                    self.display_error("Bad Gateway:\nInvalid response from the server")
                case 503:
                    self.display_error("Server Unavailable:\nServer is down")
                case 504:
                    self.display_error("Gateway Timeout:\nNo response from the server")
                case _:
                    self.display_error(f"HTTP error occurred:\n {http_error} ")
        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck the URL")
        except requests.exceptions.RequestException as req_error: # used for detecting Network problems, invalid urls and so on...
            self.display_error(f"Request Error:\n{req_error}")

        # match definition:
        # Match is similar to switch statements in other languages, but with greater flexibility
        # It enables pattern matching for sequences, mappings, and objects
        # Can be used with logical operators like OR
        # Is generally cheaper than chains of if-elif statements due to compiler optimizations

    def display_error(self, message):
        self.temperature_label.setText(message) # we can change style for our label while calling the function/changing inside some function,
        # but we need to reset it later in other functions: because it will stay changed
        self.temperature_label.setStyleSheet("font-size: 30px;" "color:red;" "font-style: italic")

        # to remove any leftovers from when the app worked like emoji and description
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
       temperature_k = data["main"]["temp"]
       temperature_c = temperature_k-273.15
       # temperature_f = (temperature_c*9/5) + 32 # From C to F and from F to C is just (F-32)*9/5
       self.temperature_label.setText(f"{temperature_c:.0f}°C") # for no decimals we can go with round() or :.0f no decimals
       self.temperature_label.setStyleSheet("font-size: 65px; " "color: black;" "font-style: normal;") # just to reset style for our temperature_label (it's been changed in display_error())
       weather_id = data["weather"][0]["id"]
       self.emoji_label.setText(self.get_weather_emoji(weather_id)) # This way we will now what emoji to put to our label based on our weather_id
       weather_desc = data["weather"][0]["description"] # we use [0] because it's a list access when we access dictionary, and then we access specific value
       self.description_label.setText(f"{weather_desc}")

    @staticmethod # these methods belong to a class but don't require any instance data
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "⛅"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "🌨️"
        elif 701 <= weather_id <= 741:
            return "🌫️"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return ""

    # Basically our weather_id is a three-digit number located in weather dictionary within data from response
    # And we can precisely know what kind of emoji to put based on the id correspondence to the weather
    # Which can be found on https://openweathermap.org/weather-conditions this link

def main():
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
