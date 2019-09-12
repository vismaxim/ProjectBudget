import os
class Configuration(object):
    DEBUG = True
    db_path = os.path.abspath('budget.db')
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
