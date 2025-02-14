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


def generate_smoking(user_input_text):
    system_content = """
        日本語で応答してください。systemはホテルの予約受付担当です。userは予約に関して部屋タイプの問い合わせをしてきます。ご用意できる部屋タイプは以下の3つです。
        シングル
        エコノミーダブル
        ダブル
        お客様には、以下の部屋タイプの略称のみをお答えください。それ以外の回答はすべて "None" を返してください。
        ---
        応答例：
        # シングルの応答例
        user: シングルの部屋が空いていますか？
        system: シングル
        ---
        user: シングルに宿泊したいのですが、空いてますか？
        system: シングル
        ---
        user: シングルを2泊でお願いしたい。
        system: シングル
        ---
        user: シングルの空き状況を教えてください。
        system: シングル
        ---
        # エコノミーダブルの応答例
        user: エコノミーダブルの部屋を希望しています。
        system: エコノミーダブル
        ---
        user: エコノミーダブルの予約をしたいです。
        system: エコノミーダブル
        ---
        user: エコノミーダブルの空きはありますか？
        system: エコノミーダブル
        ---
        # ダブルの応答例
        user: ダブルルームを予約したいです。
        system: ダブル
        ---
        user: ダブルの部屋に宿泊できますか？
        system: ダブル
        ---
        user: ダブルの空き状況を教えてください。
        system: ダブル
        ---
        # その他の問い合わせ
        user: その他の部屋タイプを希望します。
        system: None
        ---
        user: スイートルームはありますか？
        system: None
        ---
        user: もっと広い部屋はありますか？
        system: None
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
    if invalid_attempts >= 5:
        return response_elicit_session(
            intent_name,
            slots,
            "RoomType",
            "無効な入力が続いたため、予約の受付を終了します。",
            "Fulfilled",
            "Close",
            invalid_attempts
        )
    return response_elicit_session(
        intent_name,
        slots,
        "RoomType",
        "入力された値が無効です。有効な部屋タイプを入力してください。例: シングル,エコノミーダブル,ダブル",
        "InProgress",
        "ElicitSlot",
        invalid_attempts
    )


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


def process_smoking(event):
    session_state = event.get("sessionState", {})
    intent = session_state.get("intent", {})
    intent_name = intent.get("name", "")
    slots = intent.get("slots", {})
    user_input_text = event.get("inputTranscript", "")
    # logger.info(f"intent_name: {intent_name}")
    # logger.info(f"slots: {slots}")
    # logger.info(f"user_input_text: {user_input_text}")

    if event.get("invocationSource") == "DialogCodeHook":
        try:
            gpt_smoking = generate_smoking(user_input_text)
            print("gpt_smoking", gpt_smoking)
            if gpt_smoking == "None":
                gpt_smoking = None
            if gpt_smoking is None:
                return handle_invalid_attempts(intent_name, slots, event)
            else:
                if slots:
                    smoking_slot = slots.get("RoomType", {})
                    if smoking_slot:
                        smoking_value = smoking_slot.get("value", {})
                        if smoking_value:
                            lex_smoking = smoking_value.get("interpretedValue", None)
                if lex_smoking == "None":
                    lex_smoking = None
                if lex_smoking is None:
                    return handle_invalid_attempts(intent_name, slots, event)
                else:
                    return response_elicit_session(
                        intent_name,
                        slots,
                        "Smoking",
                        f" {lex_smoking} を受けたまりました。続きまして禁煙か喫煙かの希望を教えてください",
                    )
        except ValueError:
            return response_elicit_session(
                intent_name,
                slots,
                "Smoking",
                "正しい部屋タイプを入力してください。例: シングル,エコノミーダブル,ダブル",
            )
    else:
        return response_elicit_session(
            intent_name,
            slots,
            "Smoking",
            "正しい部屋タイプを入力してください。例: シングル,エコノミーダブル,ダブル",
        )

