# Securypi - Simple Home Security System built around Raspberry Pi

This software was created as part of a bachelor's thesis *Home Security System* by Filip Weissensteiner.


## What you need:
- **Raspberry Pi** 4 / 5, 2+GB RAM, running Raspbery Pi OS
- **SSD** storage recommended
- **Debian Bookworm** (or newer versions, but there may be limited compatibility with some sensors - QMP6988)
- **Raspberry Pi Camera v3** / v3 wide
- optionally **temperature, humidity, pressure sensors** (recommended humidity sensors: adafruit **sht30, sht40**; pressure sensor: **BMP388**; (DHT22 teperature sensor has poor reliability and QMP6988 pressure sensor has limitted compatibility, requiring outdated pigpiod daemon))

It is possible to run the app on any system, but only for testing purpouses (sensor data will be mocked).


## Setup:
### 0. Connect hardware sensors:
I.) Raspberry Pi Camera to CSI port.

II.) Optionally connect desired environmental sensors based on manufacturer documentation:
- SHT40: https://learn.adafruit.com/adafruit-sht40-temperature-humidity-sensor/python-circuitpython
- SHT30 / SHT31D: https://learn.adafruit.com/adafruit-sht31-d-temperature-and-humidity-sensor-breakout/python-circuitpython
- BMP388: https://learn.adafruit.com/adafruit-bmp388-bmp390-bmp3xx/python-circuitpython

III.) After connecting environmental sensors, enable them in *app_config.json*, for example:
      "use_sht40": true,
      "use_bmp388": true,



### 1. Create virtual environment and install pip dependencies

a.) Recommended: Use bash **venv install script** located in *scripts/* directory:

    ./scripts/venv_install.sh

b.) or manually create venv and install requirements:
    
    # I. Create virtual env with --system-site-packages needed for built in libcamera
    python -m venv .venv --system-site-packages

    # II. Activate the created virtual environment
    source .venv/bin/activate

    # note: activating .venv is needed for all future python / flask / pytest calls,
    #       otherwise include path in call: .venv/bin/python / .venv/bin/flask / .venv/bin/pytest

    # II. Install universal requirements:
    python -m pip install -r requirements.txt

    # III. Install Raspberry Pi platform-specific requirements:
    python -m pip install -r rpi_requirements.txt



### 2. Initialize database

a.) Recommended: use bash **init db script** located in *scripts/* directory:

    ./scripts/init_db.sh


b.) or *manually* execute *flask command* for db initialization *in virtual environment*:

    .venv/bin/python -m flask --app securypi_app init-db

- Initialize the database.
- Ask to create default user '**admin**'
- There will now be a '**securypi_app.sqlite**' file in the ./instance folder


### 3. Run the app:

a.) Recommended: use bash **app run script** located in *scripts/* directory:

    ./scripts/app_run.sh


b.) or *manually* execute *flask command* for db initialization after *activating virtual environment*:

    .venv/bin/python -m flask --app securypi_app run -h localhost -p 5555

- now you can access the app at http://localhost:5555

- change '*-h localhost*' to '**-h 0.0.0.0**' to make it visible on all networks - unsafe!
- you should use VPN tunel for remote access (e.g. Tailscale)



### To manually add another user using cli:
- Run the register-user command:

    .venv/bin/python -m flask --app securypi_app register-user [username] [password] ['admin' | 'standard']



## License

This project is licensed under the MIT License — see [LICENSE.txt](LICENSE.txt) for details.