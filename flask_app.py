"""Main application file."""

import os
import sys

from flask import Flask, Response as FlaskResponse, redirect, url_for, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import setup # pylint: disable = W0611

from app.utils.api_responses import APIResponse
from app.utils.logging_config import setup_logging, get_logger
from app.routes import (
    AuthenticationRoute as AuthRoute,
    MiscRoute,
    StripeRoute,
    TransactionRoute,
    UserRoute
)



app = Flask(__name__)
CORS(app, resources = {"/*": {"origins": "*"}})

limiter = Limiter(
    app = app,
    key_func = lambda: request.headers.get(os.getenv("AUTHORIZATION_HEADER"), get_remote_address()),
    default_limits = [os.getenv("RATE_LIMIT")]
)

setup_logging("ERROR", os.path.join("app", "logs", "error.log"), service_name = "app")
logger = get_logger("app")

# Log startup information
logger.info("=" * 50)
logger.info("Starting Crazi Co Flask Application")
logger.info("Python version: %s", sys.version)
logger.info("API_BASE: %s", os.getenv("API_BASE", "/api/v1"))
logger.info("PORT: %s", os.getenv("PORT", "5000"))
logger.info("=" * 50)


@app.errorhandler(404)
def route_not_found(error) -> FlaskResponse: # pylint: disable = W0613
    """Route not found error."""

    return APIResponse.route_not_found_error()

@app.errorhandler(405)
def method_not_allowed(error) -> FlaskResponse: # pylint: disable = W0613
    """Method not allowed error."""

    return APIResponse.method_not_allowed_error()

@app.errorhandler(429)
def rate_limit(error) -> FlaskResponse: # pylint: disable = W0613
    """Rate limit error."""

    return APIResponse.rate_limit_error()

@app.errorhandler(Exception)
def something_went_wrong(error) -> FlaskResponse:
    """Something went wrong error."""

    logger.error("An error occurred: %s", error)

    return APIResponse.unidentified_error()

@app.before_request
def allow_only_https() -> FlaskResponse:
    """Allow only HTTPS requests."""

    # Skip HTTPS redirect for health and version endpoints (needed for healthchecks)
    if request.endpoint in ["health", "version"]:
        return None
   
    if not request.is_secure and os.getenv("ENVIRONMENT") == "production":
        return redirect(url_for(request.endpoint, _external = True, _scheme = "https"))


API_BASE = os.getenv("API_BASE", "/api/v1")


app.add_url_rule(f"{API_BASE}/auth/register", "register", view_func = AuthRoute.register, methods = ["POST"])
app.add_url_rule(f"{API_BASE}/auth/google", "google_oauth", view_func = AuthRoute.google_oauth, methods = ["POST"])
app.add_url_rule(f"{API_BASE}/auth/session", "login", view_func = AuthRoute.login, methods = ["POST"])
app.add_url_rule(f"{API_BASE}/auth/session", "logout", view_func = AuthRoute.logout, methods = ["DELETE"])
app.add_url_rule(f"{API_BASE}/users/<user_email>/password", "change_password", view_func = AuthRoute.change_password, methods = ["PATCH"])
app.add_url_rule(f"{API_BASE}/users/<user_email>/otp/<otp_type>", "send_otp", view_func = AuthRoute.send_otp, methods = ["POST"])
app.add_url_rule(f"{API_BASE}/users/<user_email>/activate", "activate", view_func = AuthRoute.activate, methods = ["POST"])
app.add_url_rule(f"{API_BASE}/users/<user_id>/2fa", "enable_2fa", view_func = AuthRoute.enable_2fa, methods = ["POST"])
app.add_url_rule(f"{API_BASE}/users/<user_id>/2fa", "disable_2fa", view_func = AuthRoute.disable_2fa, methods = ["DELETE"])

app.add_url_rule(f"{API_BASE}/users", "user.view_all", view_func = UserRoute.view_all, methods = ["GET"])
app.add_url_rule(f"{API_BASE}/users/<user_id>", "user.view", view_func = UserRoute.view, methods = ["GET"])
app.add_url_rule(f"{API_BASE}/users/<user_id>", "user.update", view_func = UserRoute.update, methods = ["PATCH"])
app.add_url_rule(f"{API_BASE}/users/<user_id>/credits", "user.update_credits", view_func = UserRoute.update_credits, methods = ["PUT"])
app.add_url_rule(f"{API_BASE}/users/<user_id>", "user.delete", view_func = UserRoute.delete, methods = ["DELETE"])

app.add_url_rule(f"{API_BASE}/users/<user_id>/transactions", "transactions.create", view_func = TransactionRoute.create, methods = ["POST"])
app.add_url_rule(f"{API_BASE}/users/<user_id>/transactions", "transactions.view_all", view_func = TransactionRoute.view_all, methods = ["GET"])
app.add_url_rule(f"{API_BASE}/users/<user_id>/transactions/<transaction_id>", "transactions.view", view_func = TransactionRoute.view, methods = ["GET"])
app.add_url_rule(f"{API_BASE}/users/<user_id>/transactions/<transaction_id>", "transactions.update", view_func = TransactionRoute.update, methods = ["PATCH"])
app.add_url_rule(f"{API_BASE}/users/<user_id>/transactions/<transaction_id>", "transactions.delete", view_func = TransactionRoute.delete, methods = ["DELETE"])

app.add_url_rule(f"{API_BASE}/stripe/rate", "stripe.rate", view_func = StripeRoute.rate, methods = ["GET"])
app.add_url_rule(f"{API_BASE}/stripe/buy", "stripe.buy", view_func = StripeRoute.buy, methods = ["POST"])
app.add_url_rule(f"{API_BASE}/stripe/portal", "stripe.portal", view_func = StripeRoute.portal, methods = ["POST"])
app.add_url_rule(f"{API_BASE}/stripe/settle", "stripe.settle", view_func = StripeRoute.settle, methods = ["POST"])

app.add_url_rule(f"{API_BASE}/health", "health", view_func = MiscRoute.health, methods = ["GET"])
app.add_url_rule(f"{API_BASE}/version", "version", view_func = MiscRoute.version, methods = ["GET"])
