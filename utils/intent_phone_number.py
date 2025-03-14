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


def generate_phone_number(user_input_text):
    system_content = """
あなたの役割は、ユーザーのメッセージから電話番号のみを抽出することです。

- ユーザーのメッセージには、前後に不要な語句（「私の電話番号は」「です」「連絡先」など）が含まれることがあります。
- メッセージ内に **10桁または11桁の数字の組み合わせがある場合、それを電話番号として抽出してください**。
- 数字以外の文字（「の」「-」「+」「です」など）は無視し、**電話番号の形式に正しく整えて返してください**。
- **「090-1234-5678」→「09012345678」** のように、ハイフンやスペースを削除して数値のみを返してください。
- **電話番号が複数ある場合は、すべてをリストとして出力してください（例: ["09012345678", "08098765432"]）。**
- **電話番号が見つからない場合は、"None" を返してください。**

**出力例**:
追加の例文（20個）
一般的な発話
user：私の電話番号は08022223333です。
system：10または11桁の電話番号を取得します
assistant：08022223333

user：連絡先は070-3333-4444になります。
system：10または11桁の電話番号を取得します
assistant：07033334444

user：電話は03-5678-1234です。
system：10または11桁の電話番号を取得します
assistant：0356781234

user：携帯の番号は090 8765 4321です。
system：10または11桁の電話番号を取得します
assistant：09087654321

user：080-9999-8888が私の番号です。
system：10または11桁の電話番号を取得します
assistant：08099998888

助詞が混じる発話
user：電話番号は090の1234の5678です。
system：10または11桁の電話番号を取得します
assistant：09012345678

user：自宅の連絡先は03の4321の8765です。
system：10または11桁の電話番号を取得します
assistant：0343218765

user：連絡は080の7777で5555です。
system：10または11桁の電話番号を取得します
assistant：08077775555

user：070の6543で2109が連絡先です。
system：10または11桁の電話番号を取得します
assistant：07065432109

user：私の電話番号は03の2468の1357ですよ。
system：10または11桁の電話番号を取得します
assistant：0324681357

カジュアルな発話
user：09055556666が僕の番号だよ！
system：10または11桁の電話番号を取得します
assistant：09055556666

user：07033332222って番号にかけてね。
system：10または11桁の電話番号を取得します
assistant：07033332222

user：あ、080-7777-6666が私の携帯ね。
system：10または11桁の電話番号を取得します
assistant：08077776666

user：電話なら03 2222 3333によろしく！
system：10または11桁の電話番号を取得します
assistant：0322223333

user：090-8888-7777が自分の番号です。
system：10または11桁の電話番号を取得します
assistant：09088887777

曖昧な発話
user：09012341234だったかな、たぶん。
system：10または11桁の電話番号を取得します
assistant：09012341234

user：たしか連絡は03-3333-4444でできるはず。
system：10または11桁の電話番号を取得します
assistant：0333334444

user：連絡先は…08055556666かな？
system：10または11桁の電話番号を取得します
assistant：08055556666

user：たぶん070-2222-1111だったと思う。
system：10または11桁の電話番号を取得します
assistant：07022221111

user：確認してないけど、090-4444-3333だったはず！
system：10または11桁の電話番号を取得します
assistant：09044443333

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


def handle_invalid_attempts(intent_name, slots, event):
    session_attributes = event.get("sessionState", {}).get("sessionAttributes", {})
    invalid_attempts = int(session_attributes.get("invalidAttempts", "0"))
    invalid_attempts += 1
    print("無効データ入力回数", invalid_attempts)
    if invalid_attempts >= 4:
        return response_elicit_session(
            intent_name,
            slots,
            "PhoneNumber",
            "無効な入力が続いたため、予約の受付を終了します。",
            "Fulfilled",
            "Close",
            invalid_attempts
        )
    return response_elicit_session(
        intent_name,
        slots,
        "PhoneNumber",
        "入力された値が無効です。当日連絡可能の電話番号を入力してください。",
        "InProgress",
        "ElicitSlot",
        invalid_attempts
    )


def check_number_length(phone_number, min_length=10, max_length=11):
    """
    Checks if the phone number length is valid.
    """
    phone_number_length = len(phone_number)
    return min_length <= phone_number_length <= max_length


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
        }
    }


def confirm_intent_session(
        intent_name,
        slots=None,
        slot_to_elicit=None,
        message=None,
        state="InProgress",
       type="Delegate",
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
                "type": "ConfirmIntent"  # インテントの確認に移行
            },
            "intent": {
                "confirmationState": "None",  # 確認待ちの状態
                "name": intent_name,
                "slots": slots,
                "state": state  # スロット入力が完了した状態
            }
        }
    }


def process_phone_number(event):
    session_state = event.get("sessionState", {})
    intent = session_state.get("intent", {})
    intent_name = intent.get("name", "")
    slots = intent.get("slots", {})
    user_input_text = event.get("inputTranscript", "")
    logger.info(f"intent_name: {intent_name}")
    logger.info(f"slots: {slots}")
    logger.info(f"user_input_text: {user_input_text}")

    if event.get("invocationSource") == "DialogCodeHook":
        try:
            gpt_phone_number = generate_phone_number(user_input_text)
            print("gpt_phone_number", gpt_phone_number)

            if not gpt_phone_number:
                gpt_phone_number = None
            if gpt_phone_number is None or not check_number_length(gpt_phone_number):
                return handle_invalid_attempts(intent_name, slots, event)
            else:
                lex_phone_number = None
                if slots:
                    phone_number_slot = slots.get("PhoneNumber", {})
                    if phone_number_slot:
                        phone_number_value = phone_number_slot.get("value", {})
                        if phone_number_value:
                            lex_phone_number = phone_number_value.get("interpretedValue", None)
                print("lex_phone_number", lex_phone_number)
                if not lex_phone_number:
                    lex_phone_number = None
                if lex_phone_number is None or not check_number_length(lex_phone_number):
                    if gpt_phone_number:
                        slots["PhoneNumber"] = {
                            "value": {
                                "originalValue": user_input_text,
                                "resolvedValues": [gpt_phone_number],
                                "interpretedValue": gpt_phone_number
                            }
                        }
                        return confirm_intent_session(
                            intent_name,
                            slots,
                            "PhoneNumber",
                        )
                    return handle_invalid_attempts(intent_name, slots, event)
                else:
                    return confirm_intent_session(
                        intent_name,
                        slots,
                        "PhoneNumber",
                    )
        except ValueError:
            return response_elicit_session(
                intent_name,
                slots,
                "PhoneNumber",
                "当日連絡可能の電話番号を入力してください。",
            )
    else:
        return response_elicit_session(
            intent_name,
            slots,
            "PhoneNumber",
            "当日連絡可能の電話番号を入力してください。",
        )

