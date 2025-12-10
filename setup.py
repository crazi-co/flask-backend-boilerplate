"""Setup file for the app."""

import app.data
from app.services import (
    Authentication,
    Database,
    Email,
    OTP,
    Session,
    Stripe,
    Transaction,
    User
)



Database.initialize()

app.data.ServiceConfig.authentication = Authentication()
app.data.ServiceConfig.email = Email()
app.data.ServiceConfig.otp = OTP()
app.data.ServiceConfig.session = Session()
app.data.ServiceConfig.transaction = Transaction()
app.data.ServiceConfig.user = User()
app.data.ServiceConfig.stripe = Stripe()
