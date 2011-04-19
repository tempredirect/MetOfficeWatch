from flask import Flask
import settings

app = Flask('webapp')
app.debug = True
app.config.from_object('webapp.settings')

import views
import filters