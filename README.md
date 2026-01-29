# Securypi - Simple Home Security System built around Raspberry Pi

# Setup:
## 1. Create virtual environment and install pip dependencies

a.) Use bash install script:

    ./scripts/venv_install.sh

b.) or manually create venv and install requirements:
    
    # virtual env with --system-site-packages needed for built in libcamera
    python -m venv .venv --system-site-packages
    source .venv/bin/activate

    # universal requirements:
    python -m pip install -r requirements.txt

    # Raspberry Pi platform-specific requirements:
    python -m pip install -r rpi_requirements.txt


## 2. Initialize db

1.) Activate virtual environment:

    source .venv/bin/activate

2.) Run the init-db command in a terminal:

    python -m flask --app securypi_app init-db

- Initialize the database.
- Ask to create default user '**admin**'
- There will now be a '**securypi_app.sqlite**' file in the ./instance folder


## 3. Run the app:

    .venv/bin/python -m flask --app securypi_app run -h localhost -p 5555 --debugger

- now you can access the app at http://localhost:5555

- change '*-h localhost*' to '**-h 0.0.0.0**' to server on all networks - unsafe!
- you should use VPN tunel for remote access




## To manually add another user:
- Run the register-user command:

    .venv/bin/python -m flask --app securypi_app register-user [username] [password] ['admin' | 'standard']

