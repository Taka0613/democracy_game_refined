import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "42e76d8053493a28cc90a625d2315d2666da0c445351d01c5ddb8ba8aaa71f55"  # Replace with a secure key
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        basedir, "deliberative_democracy.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
