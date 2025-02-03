import json
import os
import logging
import re
from datetime import datetime, timezone, timedelta
from openai import OpenAI

logger = logging.getLogger()
logger.setLevel(logging.INFO)
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(
    api_key=OPENAI_API_KEY,
)


def parse_relative_date(user_input_text):
    """
    Parses relative date expressions using OpenAI's GPT model.
    Args:
        user_input_text (str): The user input text.
    Returns:
        str: The parsed date in 'YYYY-MM-DD' format, or None if no relative date expression is found.
    """
    JST = timezone(timedelta(hours=9))
    current_time = datetime.now(JST)

    current_day = current_time.day
    tomorrow = (current_time + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after_tomorrow = (current_time + timedelta(days=2)).strftime("%Y-%m-%d")
    three_days_later = (current_time + timedelta(days=3)).strftime("%Y-%m-%d")
    next_week = (current_time + timedelta(weeks=1)).strftime("%Y-%m-%d")
    two_weeks_later = (current_time + timedelta(weeks=2)).strftime("%Y-%m-%d")
    next_month = current_time.month % 12 + 1
    next_year_value = current_time.year + (current_time.month // 12)
    try:
        next_month = current_time.replace(year=next_year_value, month=next_month, day=current_day)
    except ValueError:
        next_month = current_time.replace(year=next_year_value, month=next_month, day=1) + timedelta(days=current_day - 1)
    next_month = next_month.strftime("%Y-%m-%d")

    month_after_next = current_time.month % 12 + 2
    try:
        month_after_next = current_time.replace(year=next_year_value, month=month_after_next, day=current_day)
    except ValueError:
        month_after_next = current_time.replace(year=next_year_value, month=month_after_next, day=1) + timedelta(days=current_day - 1)
    month_after_next = month_after_next.strftime("%Y-%m-%d")

    next_year = current_time.replace(year=current_time.year + 1)
    next_year = next_year.strftime("%Y-%m-%d")
    yesterday = (current_time - timedelta(days=1)).strftime("%Y-%m-%d")
    day_before_yesterday = (current_time - timedelta(days=2)).strftime("%Y-%m-%d")
    three_days_ago = (current_time - timedelta(days=3)).strftime("%Y-%m-%d")
    last_week = (current_time - timedelta(weeks=1)).strftime("%Y-%m-%d")
    last_month = (current_time.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
    last_year = current_time.replace(year=current_time.year - 1).strftime("%Y-%m-%d")

    system_content = f"""
        現在時刻{current_time}を基準に、ユーザーのメッセージ「{user_input_text}」を以下の条件で解析してください。
        1. メッセージに以下の相対日付表現が含まれる場合、有効と判断します:
        - シンプルな相対表現:
        「明日」「明後日」「明々後日」「来週」「再来週」「来月」「再来月」「来年」
            - 今日は{current_day}です。
            - 明日は{tomorrow}です。
            - 明後日は {day_after_tomorrow}です。
            - 明々後日は {three_days_later}です。
            - 来週は{next_week}です。
            - 再来週は{two_weeks_later}です。
            - 来月は{next_month}です。
            - 再来月は {month_after_next}です。
            - 来年は{next_year}です。
        - 過去を示す表現:
        「昨日」「一昨日」「先週」「先月」「去年」「三日前」
            - 昨日は{yesterday}です。
            - 一昨日は{day_before_yesterday}です。
            - 三日前は{three_days_ago}です。
            - 先週は{last_week}です。
            - 先月は{last_month}です。
            - 去年は{last_year}です。                                        - 日数・週数を指定する表現:
        「今日から3日後」「今日から2週間後」「四日後」「5週間後」など
        - その他の柔軟な表現:
        「今週の金曜日」「来月の15日」「次の土曜日」「次の月曜日」
    - その他の日数指定: 「今日から3日後」などは対応可能です。
        2. 以下の表現を含む場合は無効（`None`）と判断します:
        - イベントや行事を示す表現:
        - 季節や国民的なイベント: ハロウィン、クリスマス、大晦日、元日、節分、ひな祭り、七夕、夏祭り、お盆、敬老の日、紅葉狩り
        - 年間イベント: バレンタインデー、ホワイトデー、エイプリルフール、ゴールデンウィーク
        - 行事・祝祭: 成人の日、建国記念の日、勤労感謝の日、憲法記念日
        - その他: スポーツ大会（オリンピック、ワールドカップなど）、記念日（父の日、母の日、こどもの日）
        3. 出力形式:
        - 有効な相対日付表現の場合は、該当する日付を「YYYY-MM-DD」の形式で出力してください。
        - 無効な場合は、`None` を返してください。
        4. 出力は「YYYY-MM-DD」形式または `None` のみで行い、余計な説明やテキストは含めないでください。
        【メッセージ例】：
        - ユーザー入力「明日」
        -> 出力「2025-01-18」
        - ユーザー入力「今日から3日後」
        -> 出力「2025-01-20」
        - ユーザー入力「再来月」
        -> 出力「2025-03-01」
        - ユーザー入力「去年のクリスマス」
        -> 出力「None」
    """
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


def parse_date_without_year(check_out_date):
    """
    Parses date expressions without a year into the closest future date.
    Args:
        user_input_text (str): The user input text.
    Returns:
        str: The parsed date in 'YYYY-MM-DD' format, or None if the input is not a valid date.
    """
    today = datetime.today()
    try:
        date_without_year = datetime.strptime(check_out_date, "%m-%d")
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


def response_elicit_session(
        intent_name,
        slots=None,
        slot_to_elicit=None,
        message=None,
        state="InProgress",
        type="ElicitSlot",
        invalid_attempts="0"
    ):
    if slots is None:
        slots = {}
    return {
        "sessionState": {
            "sessionAttributes": {
                "invalidAttempts": str(invalid_attempts)
            },
            "dialogAction": {
                "type": type,
                "slotToElicit": slot_to_elicit,
            },
            "intent": {
                "confirmationState": "None",
                "name": intent_name,
                "slots": slots,
                "state": state,
            },
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message,
            }
        ],
    }


def is_valid_date_format(date_str, date_format="%Y-%m-%d"):
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False


def process_check_out_date(event):
    session_state = event.get("sessionState", {})
    intent = session_state.get("intent", {})
    intent_name = intent.get("name", "")
    slots = intent.get("slots", {})
    user_input_text = event.get("inputTranscript", "")

    if event.get("invocationSource") == "DialogCodeHook":
        check_out_date = None
        if slots:
            logger.info(f"slots: {slots}")
            check_out_date_slot = slots.get("CheckOutDate", {})
            if check_out_date_slot:
                check_out_date_value = check_out_date_slot.get("value", {})
                if check_out_date_value:
                    check_out_date = check_out_date_value.get("originalValue", None)
        if (
            not check_out_date or not is_valid_date_format(check_out_date)
        ) and isinstance(user_input_text, str):
            relative_date = parse_relative_date(user_input_text)
            if relative_date is not None:
                try:
                    datetime.strptime(relative_date, "%Y-%m-%d")
                    check_in_date = slots.get("CheckInDate", {}).get("value", {}).get("originalValue", None)
                    check_in_date = check_in_date if is_valid_date_format(check_in_date) else slots.get("CheckInDate", {}).get("value", {}).get("interpretedValue", None)
                    if check_in_date and datetime.strptime(relative_date, "%Y-%m-%d") < datetime.strptime(check_in_date, "%Y-%m-%d"):
                        return response_elicit_session(
                            intent_name,
                            slots,
                            "CheckOutDate",
                            "チェックアウト日はチェックイン日より後の日付を指定してください。",
                        )
                    else:
                        check_out_date = relative_date
                except ValueError:
                    return response_elicit_session(
                        intent_name,
                        slots,
                        "CheckOutDate",
                        "有効なチェックアウト日を入力してください。",
                    )
            elif relative_date is None:
                check_out_date = parse_special_event(user_input_text)
                if check_out_date is not None:
                    try:
                        datetime.strptime(check_out_date, "%m-%d")
                        check_out_date = parse_date_without_year(check_out_date)
                        check_in_date = slots.get("CheckInDate", {}).get("value", {}).get("originalValue", None)
                        check_in_date = check_in_date if is_valid_date_format(check_in_date) else slots.get("CheckInDate", {}).get("value", {}).get("interpretedValue", None)
                        if check_in_date and datetime.strptime(check_out_date, "%Y-%m-%d") < datetime.strptime(check_in_date, "%Y-%m-%d"):
                            return response_elicit_session(
                                intent_name,
                                slots,
                                "CheckOutDate",
                                "チェックアウト日はチェックイン日より後の日付を指定してください。",
                            )
                    except ValueError:
                        return response_elicit_session(
                            intent_name,
                            slots,
                            "CheckOutDate",
                            "Please provide a valid check-out date.",
                        )
                elif check_out_date is None:
                    session_attributes = event.get("sessionState", {}).get(
                        "sessionAttributes", {}
                    )
                    invalid_attempts = int(
                        session_attributes.get("invalidAttempts", "0")
                    )
                    invalid_attempts += 1
                    if invalid_attempts >= 5:
                        return response_elicit_session(
                            intent_name,
                            slots,
                            "CheckOutDate",
                            "無効な入力が続いたため、予約の受付を終了します。",
                            "Fulfilled",
                            "Close",
                            invalid_attempts
                        )
                    else:
                        return response_elicit_session(
                            intent_name,
                            slots,
                            "CheckOutDate",
                            "入力された値が無効です。正しい日付を入力してください。例: 2025年12月25日など",
                            "InProgress",
                            "ElicitSlot",
                            invalid_attempts
                        )
            if check_out_date:
                slots["CheckOutDate"] = {"value": {"interpretedValue": check_out_date}}
            else:
                return response_elicit_session(
                    intent_name,
                    slots,
                    "CheckOutDate",
                    "入力された値が無効です。正しい日付を入力してください。例: 2024-12-25",
                )
        print("check_out_date_fixed", check_out_date)

        if check_out_date:
            check_out_date_value = datetime.strptime(check_out_date, "%Y-%m-%d").strftime("%Y年%m月%d日")

        response = response_elicit_session(
            intent_name,
            slots,
            "NumberOfGuests",
            f"チェックアウト日 {check_out_date_value} を受けたまりました。続きまして、利用者人数を教えてください",
        )
        return response
    else:
        return response_elicit_session(
            intent_name,
            slots,
            "CheckOutDate",
            "予期せぬエラーが発生しました。予約の受付を終了します。",
            "Close",
            "Fulfilled",
        )
