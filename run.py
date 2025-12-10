"""Run the application."""

import os
from dotenv import load_dotenv

load_dotenv()

from flask_app import app # pylint: disable = C0413



if __name__ == '__main__':

    os.environ["ENVIRONMENT"] = "production"
    app.run(port = os.getenv("API_PORT"))
