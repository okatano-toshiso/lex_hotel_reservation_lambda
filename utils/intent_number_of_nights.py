import json
import os
import logging
import re
from datetime import datetime, timedelta
from openai import OpenAI

logger = logging.getLogger()
logger.setLevel(logging.INFO)
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(
    api_key=OPENAI_API_KEY,
)


def parse_date_without_year(check_in_date):
    """
    Parses date expressions without a year into the closest future date.
    Args:
        user_input_text (str): The user input text.
    Returns:
        str: The parsed date in 'YYYY-MM-DD' format, or None if the input is not a valid date.
    """
    today = datetime.today()
    try:
        date_without_year = datetime.strptime(check_in_date, "%m-%d")
        date_with_current_year = date_without_year.replace(year=today.year)
        if date_with_current_year < today:
            date_with_current_year = date_with_current_year.replace(year=today.year + 1)
        else:
            date_with_current_year = date_with_current_year.replace(year=today.year)
        return date_with_current_year.strftime("%Y-%m-%d")
    except ValueError:
        return None


def response_elicit_session(intent_name, slots, slot_to_elicit, message=None):
    dialog_action = {
        "type": "ElicitSlot",
        "slotToElicit": slot_to_elicit,
    }
    if message:
        dialog_action["message"] = {"contentType": "PlainText", "content": message}
    return {
        "sessionState": {
            "dialogAction": dialog_action,
            "intent": {"name": intent_name, "slots": slots, "state": "InProgress"},
        }
    }


def response_close_session(message, intent_name, slots):
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {"contentType": "PlainText", "content": message},
            },
            "intent": {
                "name": intent_name,
                "slots": slots,
                "state": "Fulfilled",
            },
        }
    }


def response_invalid_date_session(
    intent_name, slots, invalid_attempts, slotToElicit, message
):
    return {
        "sessionState": {
            "sessionAttributes": {"invalidAttempts": str(invalid_attempts)},
            "dialogAction": {
                "type": "ElicitSlot",
                "slotToElicit": slotToElicit,
            },
            "intent": {
                "confirmationState": "Denied",
                "name": intent_name,
                "slots": {"CheckInDate": None},
                "state": "InProgress",
            },
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message,
            }
        ],
    }


def process_number_of_nights(event):
    print("there")
