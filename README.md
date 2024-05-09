# Mini Wallet
This project requires [Python](https://www.python.org/downloads/) with version higher or equal 3.9.12 and [PIP](https://pip.pypa.io/en/stable/installation/). I recommend to create and activate the virtual environment first ([read here for official python guideline](https://docs.python.org/3/library/venv.html)).

Install all requirements using PIP.
```
pip install -r requirements.txt
```

Database that I used is SQLite, for the sake of simplicity that requires additional database installation. Run the database migration to create the table beforehand.
```
python manage.py migrate
```

Then run the development server at port 80
```
python manage.py runserver 80
```
