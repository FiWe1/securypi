# Securypi

## 1. Initialize db
- with source .venv/bin/activate
- Run the init-db command in a terminal:

    flask --app flaskurypi init-db

- \>\> Initialized the database.
- \>\> Default user 'admin' with password: 'admin4321'

- There will now be a flaskurypi.sqlite file in the instance folder in your project


## 2. Run the app:

    .venv/bin/python -m flask --app flaskurypi run -h 0.0.0.0 --debugger"

    # change "-h [address]" to 0.0.0.0 for all networks - unsafe!
    # use VPN ip




## To manually add another user:
- with source .venv/bin/activate
- Run the register-user command in a terminal:

    flask --app flaskurypi register-user [username] [password] [admin / standard]

