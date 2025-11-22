# Securypi

## 1. Initialize db

- Activate virtual environment:

    source .venv/bin/activate

- Run the init-db command in a terminal:

    python -m flask --app securypi_app init-db

- \>\> Initialized the database.
- \>\> Default user 'admin' with password: 'admin4321'

- There will now be a securypi_app.sqlite file in the instance folder in your project


## 2. Run the app:

    .venv/bin/python -m flask --app securypi_app run -h 0.0.0.0 --debugger"

    # change "-h [address]" to 0.0.0.0 for all networks - unsafe!
    # use VPN ip




## To manually add another user:
- with source .venv/bin/activate
- Run the register-user command in a terminal:

    flask --app securypi_app register-user [username] [password] [admin / standard]


@TODO Check linences and T&Cs of libraries (requirements.txt)