from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.dist import use_library
from admin import app

import fix_path

use_library('django', '0.96')

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
