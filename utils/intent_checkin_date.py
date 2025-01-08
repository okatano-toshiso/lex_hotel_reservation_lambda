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


def parse_relative_date(user_input_text):
    print("parse_relative_date")
    """
    Parses relative date expressions using OpenAI's GPT model.
    Args:
        user_input_text (str): The user input text.
    Returns:
        str: The parsed date in 'YYYY-MM-DD' format, or None if no relative date expression is found.
    """
    current_time = datetime.now().strftime("%Y-%m-%d")
    system_content = "現在時刻{}を基準に、ユーザーのメッセージ「{}」が相対日付を取得するのに有効な日付だった場合、YYYY-MM-DDのDate形式でレスポンスする。有効ではないメッセージだった場合は、Noneを返す。レスポンスの形式はYYYY-MM-DDかNoneかどちらかです。".format(
        current_time, user_input_text
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input_text},
        ],
    )
    result = response.choices[0].message.content
    print("現在の基準値", result)
    if result == "None":
        return None
    else:
        return result


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


def parse_special_event(user_input_text):
    """
    Parses special event expressions like 'Christmas', 'New Year', 'Halloween', 'Valentine's Day', 'Thanksgiving', and 'Independence Day' into actual dates.
    """
    system_content = "{}のメッセージがイベント日時を取得するのに有効な日付だった場合、mm-ddのDate形式でレスポンスする。有効ではないメッセージだった場合は、Noneを返す。レスポンスの形式はmm-ddかNoneかどちらかです。".format(
        user_input_text
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input_text},
        ],
    )
    result = response.choices[0].message.content
    if result == "None":
        return None
    else:
        return result


def response_elicit_session(intent_name, slots, slot_to_elicit, message=None):
    return {
        "sessionState": {
            "dialogAction": {
                "type": "ElicitSlot",
                "slotToElicit": slot_to_elicit,
            },
            "intent": {
                "confirmationState": "None",
                "name": intent_name,
                "slots": slots,
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


def response_close_session(message, intent_name, slots=None):
    if slots is None:
        slots = {}  # 空のスロットをデフォルト値として設定
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
            },
            "intent": {
                "name": intent_name,
                "slots": slots,
                "state": "Fulfilled",
            },
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message,
            }
        ],
    }


def response_invalid_date_session(
    intent_name, slots, invalid_attempts, slotToElicit, message
):
    print("response_invalid_date_session")
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


def process_check_in_date(event):
    session_state = event.get("sessionState", {})
    intent = session_state.get("intent", {})
    intent_name = intent.get("name", "")
    slots = intent.get("slots", {})
    print("slots", slots)
    user_input_text = event.get("inputTranscript", "")

    if event.get("invocationSource") == "DialogCodeHook":
        check_in_date = None
        if slots:
            check_in_date_slot = slots.get("CheckInDate", {})
            if check_in_date_slot:
                check_in_date_value = check_in_date_slot.get("value", {})
                if check_in_date_value:
                    check_in_date = check_in_date_value.get("interpretedValue", None)

        if not check_in_date and isinstance(user_input_text, str):
            print("user_input_text", user_input_text)
            relative_date = parse_relative_date(user_input_text)
            print("relative_date", relative_date)

            if relative_date:
                try:
                    datetime.strptime(relative_date, "%Y-%m-%d")  # フォーマットを修正
                    check_in_date = relative_date
                except ValueError:
                    return response_elicit_session(
                        intent_name,
                        slots,
                        "CheckInDate",
                        "Please provide a valid check-in date.",
                    )
            else:
                check_in_date = parse_special_event(user_input_text)
                print("check_in_date", check_in_date)
                if check_in_date:
                    try:
                        datetime.strptime(check_in_date, "%m-%d")
                        check_in_date = parse_date_without_year(check_in_date)
                    except ValueError:
                        return response_elicit_session(
                            intent_name,
                            slots,
                            "CheckInDate",
                            "Please provide a valid check-in date.",
                        )
                else:
                    print("invalid message")
                    session_attributes = event.get("sessionState", {}).get(
                        "sessionAttributes", {}
                    )
                    invalid_attempts = int(
                        session_attributes.get("invalidAttempts", "0")
                    )
                    invalid_attempts += 1
                    print("invalid_attempts", invalid_attempts)
                    if invalid_attempts >= 5:
                        print("over five times")
                        print("intent_name", intent_name)
                        print("slots", slots)
                        return response_close_session(
                            "入力が繰り返し無効です。セッションを終了します。",
                            intent_name,
                            slots,
                        )
                    else:
                        print("under five times")
                        print("intent_name", intent_name)
                        print("slots", slots)
                        return response_invalid_date_session(
                            intent_name,
                            slots,
                            invalid_attempts,
                            "CheckInDate",
                            "入力された日付が無効です。正しい日付を入力してください。例: 2024-12-25",
                        )
            if check_in_date:
                slots["CheckInDate"] = {"value": {"interpretedValue": check_in_date}}
            else:
                return response_elicit_session(
                    intent_name,
                    slots,
                    "CheckInDate",
                    "Please provide a valid check-in date.",
                )
        print("check_in_date_fixed", check_in_date)

        # 成功メッセージを設定
        response = response_elicit_session(
            intent_name,
            slots,
            "CheckInDate",
            "チェックイン日が正常に受理されました。何泊ご滞在されますか？",
        )
        return response
    else:
        return response_close_session(
            "Thank you for your information.", intent_name, slots
        )
