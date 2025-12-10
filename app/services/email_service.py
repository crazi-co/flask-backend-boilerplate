"""Service for email operations."""

import os
import boto3
from botocore.exceptions import ClientError, BotoCoreError, ParamValidationError

from app.error_handing import AWSError



class Email:
    """Email service functions."""

    source = "Crazi Co <noreply@crazi.co>"
    
    welcome_subject = "Welcome to Crazi Co!"
    welcome_text = "Welcome to Crazi Co. To finish setting up your account, confirm your email address by clicking the following link - <url>.\n\nThis code will expire in 10 minutes for your security. If you didn't request this email, there's nothing to worry about, you can safely ignore it."

    otp_subject = "Crazi Co verification code."
    otp_text = "Here's your Crazi Co verification code. Enter it in the app to continue - <url>.\n\nThis code will expire in 10 minutes for your security. If you didn't request this email, there's nothing to worry about, you can safely ignore it."

    password_subject = "Crazi Co password."
    password_text = "Welcome to Crazi Co. Here's your auto-generated password, use it to login to your account - <password>.\n\n For security, please change this password after your first login. If you didn't request this account creation, please write to us at support@crazi.co."

    def __init__(self) -> None:
        self.client = boto3.client(
            "ses",
            region_name = os.getenv("SES_AWS_REGION"),
            aws_access_key_id = os.getenv("SES_AWS_ACCESS_KEY_ID"),
            aws_secret_access_key = os.getenv("SES_AWS_SECRET_ACCESS_KEY")
        )

    def welcome(self, to: str, code: str, user_id: str, user_token: str) -> None:
        """Send a welcome email to the user."""

        try:

            with open(os.path.join("app", "data", "email_templates", "welcome_email.html"), "r", encoding = "utf-8") as file:
                html = file.read()

            html = html.replace("<url>", f"{os.getenv('CLIENT_URL')}/auth/email/activate?email={to}&code={code}&user_id={user_id}&user_token={user_token}").replace("<code>", code)
            text = self.welcome_text.replace("<url>", f"{os.getenv('CLIENT_URL')}/auth/email/activate?email={to}&code={code}&user_id={user_id}&user_token={user_token}").replace("<code>", code)

            response = self.client.send_email(
                Source = self.source,
                Destination = {"ToAddresses": [to],},
                Message = {
                    "Subject": {"Data": self.welcome_subject,},
                    "Body": {
                        "Text": {"Data": text,},
                        "Html": {"Data": html,},
                    },
                }
            )

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:

                raise AWSError(
                    "SES returned non-200 status code",
                    service_name = "ses",
                    operation = "send_welcome_email",
                    recipient = to,
                    error_type = "non_200_response",
                    metadata = {
                        "email_type": "welcome",
                        "http_status": response["ResponseMetadata"]["HTTPStatusCode"],
                        "response": str(response)
                    }
                )
            
        except ClientError as exc:

            error_code = exc.response.get('Error', {}).get('Code', 'Unknown')
            error_message = exc.response.get('Error', {}).get('Message', str(exc))
            
            raise AWSError(
                f"SES send email failed: {error_message}",
                service_name = "ses",
                operation = "send_welcome_email",
                recipient = to,
                error_code = error_code,
                error_type = "client_error",
                metadata = {
                    "email_type": "welcome",
                    "http_status": exc.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
                },
                original_error = exc
            ) from exc

        except (BotoCoreError, ParamValidationError) as exc:

            raise AWSError(
                f"AWS connection or validation error: {str(exc)}",
                service_name = "ses",
                operation = "send_welcome_email",
                recipient = to,
                error_type = type(exc).__name__,
                metadata = {"email_type": "welcome"},
                original_error = exc
            ) from exc

        except Exception as exc: # pylint: disable = W0718

            raise AWSError(
                f"Unexpected error sending welcome email: {str(exc)}",
                service_name = "ses",
                operation = "send_welcome_email",
                recipient = to,
                error_type = "unexpected_error",
                metadata = {"email_type": "welcome"},
                original_error = exc
            ) from exc

    def otp(self, to: str, code: str) -> None:
        """Send a otp email to the user."""

        try:

            with open(os.path.join("app", "data", "email_templates", "otp_email.html"), "r", encoding = "utf-8") as file:
                html = file.read()

            html = html.replace("<code>", code)
            text = self.otp_text.replace("<code>", code)
            
            response = self.client.send_email(
                Source = self.source,
                Destination = {"ToAddresses": [to],},
                Message = {
                    "Subject": {"Data": self.otp_subject,},
                    "Body": {
                        "Text": {"Data": text,},
                        "Html": {"Data": html,},
                    },
                }
            )

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                raise AWSError(
                    "SES returned non-200 status code",
                    service_name = "ses",
                    operation = "send_welcome_email",
                    recipient = to,
                    error_type = "non_200_response",
                    metadata = {
                        "email_type": "welcome",
                        "http_status": response["ResponseMetadata"]["HTTPStatusCode"],
                        "response": str(response)
                    }
                )
            
        except ClientError as exc:

            error_code = exc.response.get('Error', {}).get('Code', 'Unknown')
            error_message = exc.response.get('Error', {}).get('Message', str(exc))
            
            raise AWSError(
                f"SES send email failed: {error_message}",
                service_name = "ses",
                operation = "send_welcome_email",
                recipient = to,
                error_code = error_code,
                error_type = "client_error",
                metadata = {
                    "email_type": "welcome",
                    "http_status": exc.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
                },
                original_error = exc
            ) from exc

        except (BotoCoreError, ParamValidationError) as exc:

            raise AWSError(
                f"AWS connection or validation error: {str(exc)}",
                service_name = "ses",
                operation = "send_welcome_email",
                recipient = to,
                error_type = type(exc).__name__,
                metadata = {"email_type": "welcome"},
                original_error = exc
            ) from exc

        except Exception as exc: # pylint: disable = W0718

            raise AWSError(
                f"Unexpected error sending welcome email: {str(exc)}",
                service_name = "ses",
                operation = "send_welcome_email",
                recipient = to,
                error_type = "unexpected_error",
                metadata = {"email_type": "welcome"},
                original_error = exc
            ) from exc

    def password(self, to: str, password: str) -> None:
        """Send a password email to the user."""

        try:

            with open(os.path.join("app", "data", "email_templates", "password_email.html"), "r", encoding = "utf-8") as file:
                html = file.read()

            html = html.replace("<password>", password)
            text = self.password_text.replace("<password>", password)
            
            response = self.client.send_email(
                Source = self.source,
                Destination = {"ToAddresses": [to],},
                Message = {
                    "Subject": {"Data": self.password_subject,},
                    "Body": {
                        "Text": {"Data": text,},
                        "Html": {"Data": html,},
                    },
                }
            )

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                raise AWSError(
                    "SES returned non-200 status code",
                    service_name = "ses",
                    operation = "send_welcome_email",
                    recipient = to,
                    error_type = "non_200_response",
                    metadata = {
                        "email_type": "welcome",
                        "http_status": response["ResponseMetadata"]["HTTPStatusCode"],
                        "response": str(response)
                    }
                )
            
        except ClientError as exc:

            error_code = exc.response.get('Error', {}).get('Code', 'Unknown')
            error_message = exc.response.get('Error', {}).get('Message', str(exc))
            
            raise AWSError(
                f"SES send email failed: {error_message}",
                service_name = "ses",
                operation = "send_welcome_email",
                recipient = to,
                error_code = error_code,
                error_type = "client_error",
                metadata = {
                    "email_type": "welcome",
                    "http_status": exc.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
                },
                original_error = exc
            ) from exc

        except (BotoCoreError, ParamValidationError) as exc:

            raise AWSError(
                f"AWS connection or validation error: {str(exc)}",
                service_name = "ses",
                operation = "send_welcome_email",
                recipient = to,
                error_type = type(exc).__name__,
                metadata = {"email_type": "welcome"},
                original_error = exc
            ) from exc

        except Exception as exc: # pylint: disable = W0718

            raise AWSError(
                f"Unexpected error sending welcome email: {str(exc)}",
                service_name = "ses",
                operation = "send_welcome_email",
                recipient = to,
                error_type = "unexpected_error",
                metadata = {"email_type": "welcome"},
                original_error = exc
            ) from exc
