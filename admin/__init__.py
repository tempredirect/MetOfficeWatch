from flask import Flask
import settings

app = Flask('admin')
app.debug = True
app.config.from_object('admin.settings')

import views