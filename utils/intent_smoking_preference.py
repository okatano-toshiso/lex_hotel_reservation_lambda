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
日本語で応答してください。
systemはホテルの予約受付担当です。userは禁煙（きんえん）または喫煙（きつえん）のどちらかを選択して部屋タイプを答えています。
関係ない内容が送られてくるかもしれませんが、喫煙者かどうかを尋ねた結果のメッセージが送られてくるので、必ず「喫煙者かどうか」の回答をしてきているのだと認識してください。

### 条件:
1. userが「喫煙（きつえん）」「喫煙希望」「煙草を吸う」「喫煙室」「タバコを吸いたい」などと回答された場合は、喫煙 と **括弧や記号を一切付けず** に返してください。
2. userが「禁煙（きんえん）」「禁煙希望」「煙草を吸わない」「煙草を吸いません」「禁煙室」「タバコの匂いが苦手」などと回答された場合も、禁煙 と **括弧や記号を一切付けず** に返してください。
3. userの回答が禁煙または喫煙と全く関係ない場合（例：「トイレはどこですか？」など）は、None を返してください。

### 誤字対応:
userが「近縁」「近年」「喫煙」「禁煙」など音声認識の誤字パターンに基づく間違いを含む場合、それらも正確に解釈して以下のように処理してください：
1. 「近年」「きんねん」「近縁」「きんえん」などが「禁煙」と誤認された場合も「禁煙」と解釈し、禁煙と返答してください。
2. 「きつえん」と読みが同じでで感じが異なる場合も「喫煙」と解釈し、喫煙と返答してください。

### 応答形式:
「喫煙」「禁煙」いずれかの文字列を **括弧や記号なし** で返答してください。
回答は純粋な文字列型で、引用符や括弧を付けないようにしてください（例: 「喫煙」ではなく 喫煙）。

### 応答例:
userのメッセージ：「煙草を吸うので喫煙室をお願いします」
systemのレスポンス：喫煙

userのメッセージ：「タバコの匂いが苦手なので禁煙室をお願いします」
systemのレスポンス：禁煙

userのメッセージ：「タバコを吸いません」
systemのレスポンス：禁煙

userのメッセージ：「喫煙希望です」
systemのレスポンス：喫煙

userのメッセージ：「禁煙希望です」
systemのレスポンス：禁煙

userのメッセージ：「トイレはどこですか？」
systemのレスポンス：None

userのメッセージ：「近縁（きんえん）ですか？」
systemのレスポンス：禁煙

userのメッセージ：「きんねんですか？」
systemのレスポンス：禁煙

userのメッセージ：「近年（きつえん）ですか？」
systemのレスポンス：喫煙
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
            "SmokingPreference",
            "無効な入力が続いたため、予約の受付を終了します。",
            "Fulfilled",
            "Close",
            invalid_attempts
        )
    return response_elicit_session(
        intent_name,
        slots,
        "SmokingPreference",
        "入力された値が無効です。喫煙か禁煙かのご希望を入力してください。",
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


def process_smoking_preference(event):
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
            gpt_smoking = generate_smoking(user_input_text)
            print("gpt_smoking", gpt_smoking)
            if gpt_smoking == "None":
                gpt_smoking = None
            if gpt_smoking is None:
                return handle_invalid_attempts(intent_name, slots, event)
            else:
                lex_smoking = None
                if slots:
                    smoking_slot = slots.get("SmokingPreference", {})
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
                        "UserName",
                        f" {gpt_smoking} を受けたまりました。予約に関する情報の取得は以上です。続きまして代表者様のお名前を教えてくてください。",
                    )
        except ValueError:
            return response_elicit_session(
                intent_name,
                slots,
                "SmokingPreference",
                "喫煙か禁煙かのご希望を入力してください。",
            )
    else:
        return response_elicit_session(
            intent_name,
            slots,
            "SmokingPreference",
            "喫煙か禁煙かのご希望を入力してください。",
        )

