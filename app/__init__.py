from flask import Flask
import os

application = Flask(__name__)
from app import views
