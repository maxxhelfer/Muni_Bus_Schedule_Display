# Muni Bus Schedule Display

Based off of the idea from [singapore-bus-timing-edisplay](https://github.com/awesomelionel/singapore-bus-timing-edisplay/tree/main) but for San Francisco Muni (SFMTA).

This project creates an E-Ink display that shows real-time San Francisco Muni bus arrival times and current weather conditions. It uses data from the [511.org](https://511.org/developer-resources/transit) API for bus arrival times and [WeatherAPI.com](https://www.weatherapi.com/) for live weather updates. The display is powered by a Raspberry Pi Zero 2W and a Waveshare 7.5-inch E-Ink screen.
![Frame-28-04-2025-01-34-51](https://github.com/user-attachments/assets/4b7f41ef-f286-4b20-bf1d-ecb6762c2101)

## Features
- Displays real-time Muni bus arrival times for selected stops.
- Shows live temperature and weather conditions.
- Automatically refreshes data at a set interval using cron jobs.
- Runs on a Raspberry Pi with a Waveshare E-Ink display.

## Hardware Requirements
1. Raspberry Pi Zero 2W (or any Raspberry Pi model with internet access)
2. Waveshare 7.5-inch E-Ink Display (EPD 7in5 V2)
3. 40-pin GPIO headers (if using a Pi Zero, you may need to solder these)
4. 5V 3A power supply
5. Micro USB flat cable
6. 4GB or larger SD card

## Setup

### 1. Clone the Repository
SSH into your Raspberry Pi and clone the repository:
```bash
cd ~
git clone https://github.com/maxxhelfer/Muni_Bus_Schedule_Display.git
cd Muni_Bus_Schedule_Display
```

### 2. Install Required Packages
Install dependencies using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Rename `.env.example` to `.env` and edit it with your API keys and stop IDs:
```bash
mv .env_example .env
nano .env
```
Modify the file to include:
```env
API_KEY=your_511_api_key
W_API_KEY=your_weatherapi_key
LAT=your_latitude
LONG=your_longitude
STOPID1=stop_id_1
STOPID2=stop_id_2
STOPID3=stop_id_3
STOPID4=stop_id_4
```
- **API_KEY**: Get from [511.org](https://511.org/developer-resources/transit)
- **W_API_KEY**: Get from [WeatherAPI.com](https://www.weatherapi.com/)
- **LAT, LONG**: Coordinates for weather data
- **STOPID**: Find your local stop id from [511.org](https://511.org/transit/agencies/stop-id)

### 4. Set Up a Cron Job for Automatic Updates
Instead of using `systemd`, we use cron jobs to refresh the display periodically:
```bash
crontab -e
```
Add the following line at the bottom to run the script every minute:
```cron
* * * * * /usr/bin/python3 /home/pi/Muni_Bus_Schedule_Display/muni_bus_eink.py
```
Save and exit.

### 5. Run the Script Manually (for testing)
```bash
python3 muni_bus_eink.py
```

## Usage
The script will automatically update the bus times and weather display based on the cron job schedule. If needed, you can manually restart the process by running the script.

## Troubleshooting
- If the display doesn’t update, check if the script is running:
  ```bash
  ps aux | grep muni_bus_eink.py
  ```
- Check the logs for errors:
  ```bash
  cat /var/log/syslog | grep cron
  ```
- Manually test the APIs:
  ```bash
  curl -H "User-Agent: MuniBusEink/1.0" "https://api.weatherapi.com/v1/current.json?key=your_api_key&q=your_lat,your_long"
  ```

## Future Improvements
- Improve error handling for API failures.
- Adjust the cron jobs to only run 6am-10pm 
- Run a goodnight script @ 10pm to display weather and calendar events for tomorrow
- Create an app for TRMNL E-Ink display  

## Dependencies
Ensure the following dependencies are installed:
```bash
pip install -r requirements.txt
```

A `requirements.txt` file is included in the repository with the necessary Python packages:
```
requests
waveshare-epd
python-dotenv
pillow
```

---


