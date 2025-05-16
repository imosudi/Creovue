#export FLASK_APP=main.py
import config
#from Creovue import app
from Creovue import app

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)

