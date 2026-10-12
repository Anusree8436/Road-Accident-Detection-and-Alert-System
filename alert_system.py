
import os
import smtplib
import requests

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_location():
    try:
        response = requests.get(
            "https://ipinfo.io/json",
            timeout=5
        )
        response.raise_for_status()

        data = response.json()

        loc = data.get("loc", "")
        city = data.get("city", "")
        region = data.get("region", "")
        country = data.get("country", "")

        return loc, f"{city}, {region}, {country}"

    except Exception:
        return "", "Location unavailable"


def send_emergency_mail():
    sender = os.environ.get("ALERT_EMAIL")
    password = os.environ.get("ALERT_EMAIL_PASSWORD")
    receiver = os.environ.get("RECEIVER_EMAIL")

    if not sender or not password or not receiver:
        print("Email settings are missing.")
        return

    loc, place = get_location()

    map_link = (
        f"https://www.google.com/maps?q={loc}"
        if loc else "Location unavailable"
    )

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = "ROAD ACCIDENT ALERT"

    body = f"""
Potential road accident detected!

Approximate location:
{place}

Google Maps:
{map_link}

Please verify the situation and contact emergency services if needed.
"""

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        print("Emergency email sent.")

    except Exception as error:
        print("Email could not be sent:", error)
if __name__ == "__main__":
    send_emergency_mail()