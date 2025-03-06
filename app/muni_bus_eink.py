from time import sleep
import requests
import json
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
from waveshare_epd import epd7in5_V2  # Adjust for your display model
from PIL import Image, ImageDraw, ImageFont

# Load API keys from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")
StopID1 = os.getenv("STOPID1")
StopID2 = os.getenv("STOPID2")
StopID3 = os.getenv("STOPID3")
StopID4 = os.getenv("STOPID4")
W_API_KEY = os.getenv("W_API_KEY")
LAT = os.getenv("LAT")
LONG = os.getenv("LONG")
# Configuration
AGENCY = "SF"
STOP_IDS = [StopID1, StopID2, StopID3, StopID4]
LOCAL_TZ = pytz.timezone("America/Los_Angeles")
REFRESH_INTERVAL = 60  # Refresh every 60 seconds

# Custom stop titles
STOP_TITLES = {
    "14411": "30 - North Beach",
    "15273": "28 - Presidio",
    "15272": "43 - Panhandle",
    "13858": "1 - California",
}

# Initialize e-ink display
epd = epd7in5_V2.EPD()
epd.init()
epd.Clear()

# Load fonts
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_LARGE = ImageFont.truetype(FONT_PATH, 42)  # Increased for better readability
FONT_MEDIUM = ImageFont.truetype(FONT_PATH, 28)  # For stop titles
FONT_SMALL = ImageFont.truetype(FONT_PATH, 24)  # For arrivals

def get_bus_arrivals(stop_id):
    """Fetch next bus arrivals for a given stop."""
    url = f"https://api.511.org/transit/StopMonitoring?api_key={API_KEY}&agency={AGENCY}&stopcode={stop_id}&format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = json.loads(response.content.decode('utf-8-sig'))

        arrivals = []
        for item in data["ServiceDelivery"]["StopMonitoringDelivery"]["MonitoredStopVisit"]:
            arrival_time_utc = item["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"]

            # Convert to local time
            arrival_time_local = datetime.strptime(arrival_time_utc, "%Y-%m-%dT%H:%M:%SZ")
            arrival_time_local = arrival_time_local.replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)
            arrival_time_str = arrival_time_local.strftime("%I:%M %p")  # e.g., "09:33 AM"

            arrivals.append(arrival_time_str)  # Only show time, not route name

        return arrivals if arrivals else ["No arrivals found"]

    except Exception as e:
        return [f"Error: {e}"]

def get_current_weather():
    """Fetch current weather data for San Francisco, CA using WeatherAPI.com."""
    url = f"https://api.weatherapi.com/v1/current.json?key={W_API_KEY}&q={LAT},{LONG}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()

        # Extract real-time temperature & weather description
        temperature = int(weather_data["current"]["temp_f"])
        description = weather_data["current"]["condition"]["text"]

        return temperature, description

    except requests.exceptions.RequestException as e:
        return None, f"Error: {e}"


def display_info():
    """Fetch data for all stops and update the e-ink display in a 2x2 grid."""
    now = datetime.now(LOCAL_TZ).strftime("%I:%M %p")  # 12-hour format
    temperature, description = get_current_weather()

    # Handle possible weather API failure
    if temperature is None:
        weather_text = f"{now} | Weather unavailable"
    else:
        weather_text = f"{now} | {temperature}°F {description}"

    # Create a blank image
    image = Image.new("1", (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(image)

    # --- Display Current Time & Weather ---
    draw.text((epd.width // 2, 40), weather_text, font=FONT_LARGE, fill=0, anchor="mm")

    # --- Layout Grid Variables ---
    col_count = 2  # Number of columns
    row_count = 2  # Number of rows
    cell_width = epd.width // col_count
    cell_height = (epd.height - 100) // row_count  # Leaving space for time/weather

    # --- Loop through stops & arrange in a grid ---
    for i, stop_id in enumerate(STOP_IDS):
        row = i // col_count
        col = i % col_count

        x_offset = col * cell_width
        y_offset = 100 + (row * cell_height)  # Offset below time/weather

        # Get bus arrivals
        arrivals = get_bus_arrivals(stop_id)

        # Get stop title
        stop_title = STOP_TITLES.get(stop_id, f"Stop {stop_id}")

        # --- Inverted Title Section for Stop Name ---
        title_height = 40
        draw.rectangle([(x_offset, y_offset), (x_offset + cell_width, y_offset + title_height)], fill=0)
        draw.text((x_offset + cell_width // 2, y_offset + 20), stop_title, font=FONT_MEDIUM, fill=255, anchor="mm")

        # --- Display Bus Times ---
        y_position = y_offset + title_height + 5
        for arrival in arrivals[:3]:  # Show up to 3 arrivals per stop
            draw.text((x_offset + 10, y_position), arrival, font=FONT_SMALL, fill=0)
            y_position += 30  # Line spacing

    # Update e-ink display
    epd.display(epd.getbuffer(image))

def main():
    display_info()

if __name__ == "__main__":
    main()

