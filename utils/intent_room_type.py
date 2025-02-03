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

def generate_room_type(user_input_text):
    system_content = """
        「日本語で応答してください。systemはホテルの予約受付担当です。userは予約に関して部屋タイプの問い合わせをしてきます。ご用意できる部屋タイプは以下の3つです。
        シングル(S)
        エコノミーダブル(WA)
        ダブル(W)
        お客様には、以下の部屋タイプの略称のみをお答えください。それ以外の回答はすべて "None" を返してください。
        ---
        応答例：
        # シングル(S)の応答例
        user: シングルの部屋が空いていますか？
        system: シングル(S)
        ---
        user: シングルに宿泊したいのですが、空いてますか？
        system: シングル(S)
        ---
        user: 一人用のシングルを希望しています。
        system: シングル(S)
        ---
        user: シングルルームに変更できますか？
        system: シングル(S)
        ---
        user: 一番安いシングルを予約したいです。
        system: シングル(S)
        ---
        user: シングルを2泊でお願いしたい。
        system: シングル(S)
        ---
        user: シングルの空き状況を教えてください。
        system: シングル(S)
        ---
        user: シングルルーム
        system: シングル(S)
        ---
        user: シングルの部屋タイプを希望します。
        system: シングル(S)
        ---
        user: シングルで泊まれる部屋はありますか？
        system: シングル(S)
        ---
        # エコノミーダブル(WA)の応答例
        user: エコノミーダブルの部屋を希望しています。
        system: エコノミーダブル(WA)
        ---
        user: エコノミーダブルは空いていますか？
        system: エコノミーダブル(WA)
        ---
        user: 二人で泊まるエコノミーダブルはありますか？
        system: エコノミーダブル(WA)
        ---
        user: エコノミーダブルの予約をしたいです。
        system: エコノミーダブル(WA)
        ---
        user: お得なエコノミーダブルに変更できますか？
        system: エコノミーダブル(WA)
        ---
        user: エコノミーダブルは禁煙ですか？
        system: エコノミーダブル(WA)
        ---
        user: エコノミーダブルでの宿泊を希望しています。
        system: エコノミーダブル(WA)
        ---
        user: エコノミーダブル
        system: エコノミーダブル(WA)
        ---
        user: エコノミーダブルの空きはありますか？
        system: エコノミーダブル(WA)
        ---
        user: エコノミーダブルを予約したい。
        system: エコノミーダブル(WA)
        ---
        # ダブル(W)の応答例
        user: ダブルの部屋に変更できますか？
        system: ダブル(W)
        ---
        user: ダブルルームの空き状況を教えてください。
        system: ダブル(W)
        ---
        user: ダブルルームを予約したいです。
        system: ダブル(W)
        ---
        user: ダブルは空いてますか？
        system: ダブル(W)
        ---
        user: ダブルの部屋で泊まれますか？
        system: ダブル(W)
        ---
        user: ダブルの禁煙ルームを希望します。
        system: ダブル(W)
        ---
        user: ダブルルームに泊まりたいです。
        system: ダブル(W)
        ---
        user: ダブル
        system: ダブル(W)
        ---
        user: ダブルルームを2泊でお願いします。
        system: ダブル(W)
        ---
        user: ダブルの部屋に宿泊できますか？
        system: ダブル(W)
        ---
        user: その他の部屋タイプを希望します。
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


def process_room_type(event):
    session_state = event.get("sessionState", {})
    intent = session_state.get("intent", {})
    intent_name = intent.get("name", "")
    slots = intent.get("slots", {})
    user_input_text = event.get("inputTranscript", "")
    logger.info(f"intent_name: {intent_name}")
    logger.info(f"slots: {slots}")
    logger.info(f"user_input_text: {user_input_text}")
    if event.get("invocationSource") == "DialogCodeHook":
        room_type = None
        if slots:
            logger.info(f"slots: {slots}")
            room_type_slot = slots.get("RoomType", {})
            if room_type_slot:
                room_type_value = room_type_slot.get("value", {})
                if room_type_value:
                    room_type = room_type_value.get("interpretedValue", None)

        print("room_type", room_type)
        print("room_type type", type(room_type))

        if room_type is None:
            print("room_type_null", room_type)
            try:
                room_type = generate_room_type(user_input_text)
                if room_type == "None":
                    room_type = None
                print("generate_room_type", room_type)
                print("generate_room_type type", type(room_type))
                if room_type is None:
                    session_attributes = event.get("sessionState", {}).get(
                        "sessionAttributes", {}
                    )
                    invalid_attempts = int(
                        session_attributes.get("invalidAttempts", "0")
                    )
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
                    else:
                        return response_elicit_session(
                            intent_name,
                            slots,
                            "RoomType",
                            "入力された値が無効です。有効な部屋タイプを入力してください。例: シングル,エコノミーダブル,ダブル",
                            "InProgress",
                            "ElicitSlot",
                            invalid_attempts
                        )
                else:
                    response = response_elicit_session(
                        intent_name,
                        slots,
                        "RoomType",
                        f" {room_type} を受けたまりました。続きまして禁煙か喫煙かの希望を教えてください",
                    )
            except ValueError:
                return response_elicit_session(
                    intent_name,
                    slots,
                    "RoomType",
                    "正しい部屋タイプを入力してください。例: シングル,エコノミーダブル,ダブル",
                )
        else:
            print("room_type", room_type)
            print("room_type type", type(room_type))
            response = response_elicit_session(
                intent_name,
                slots,
                "RoomType",
                f" {room_type} を受けたまりました。続きまして禁煙か喫煙かの希望を教えてください",
            )
            return response

