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

def convert_guests_to_number(user_input_text):

    system_content = """
        ホテルの予約受付担当者として、お客様からの宿泊人数を受け取り、対応する int 型の数値を返します。
        日本語で応答してください。
        あなたはホテルの予約受付担当です。
        userにご利用者人数に関して問い合わせをします。
        お客様にご利用者人数を聞いています。
        お客様の発言をもとに、ご利用者人数を一桁の数値（int型）として回答してください。
        必ず数値のみを返してください。１人といった「人」単位はつけないでください。絶対に数値のみです。
        ただし、利用者人数と関係ないメッセージを送られてきた場合は、Noneを返してください。

        ### 条件:
        1. お客様が「一」「一人」「1」「1人」「１」「１人」などといえば、int 型の `1` を返してください。
        2. お客様が「二」「二人」「2」「2人」「２」「２人」などといえば、int 型の `2` を返してください。
        3. お客様が「三」「三人」「3」「3人」「３」「３人」などといえば、int 型の `3` を返してください。
        4. お客様が「四」「四人」「4」「4人」「４」「４人」などといえば、int 型の `4` を返してください。
        5. お客様が「五」「五人」「5」「5人」「５」「５人」などといえば、int 型の `5` を返してください。
        6. お客様が「六」「六人」「6」「6人」「６」「６人」などといえば、int 型の `6` を返してください。
        7. お客様が「七」「七人」「7」「7人」「７」「７人」などといえば、int 型の `7` を返してください。
        8. お客様が「八」「八人」「8」「8人」「８」「８人」などといえば、int 型の `8` を返してください。
        9. お客様が「九」「九人」「9」「9人」「９」「９人」などといえば、int 型の `9` を返してください。

        ### 対応可能な入力形式:
        - 半角数字（例: "1", "2", "3"）
        - 全角数字（例: "１", "２", "３"）
        - 漢数字（例: "一", "二", "三"）
        - それらに「人」を組み合わせた表現（例: "1人", "２人", "三人"）
        - 揺らぎを含む表現（例: "ひとり旅", "夫婦で", "カップルで", "両親と子供2人"）

        ### 揺らぎの解釈:
        - 「ひとり」「ひとり旅」「ぼっち旅」「1」「一」など → `1`
        - 「夫婦で」「カップルで」「2」「二」など → `2`
        - 「家族4人」「両親と子供2人」「4」「四」など → `4`

        ### 応答例（INT型を返す）:
        ---
        お客様：一
        応答：**1**  # int 型の `1` を返す
        ---
        お客様：1
        応答：**1**  # int 型の `1` を返す
        ---
        お客様：二人
        応答：**2**  # int 型の `2` を返す
        ---
        お客様：2
        応答：**2**  # int 型の `2` を返す
        ---
        お客様：三
        応答：**3**  # int 型の `3` を返す
        ---
        お客様：3人
        応答：**3**  # int 型の `3` を返す
        ---
        お客様：4
        応答：**4**  # int 型の `4` を返す
        ---
        お客様：家族4人
        応答：**4**  # int 型の `4` を返す
        ---
        お客様：4
        応答：**4**  # int 型の `4` を返す
        ---
        お客様：五人
        応答：**5**  # int 型の `5` を返す
        ---
        お客様：5
        応答：**5**  # int 型の `5` を返す
        ---
        お客様：6
        応答：**6**  # int 型の `6` を返す
        ---
        お客様：六
        応答：**6**  # int 型の `6` を返す
        ---
        お客様：6人
        応答：**6**  # int 型の `6` を返す
        ---
        お客様：7人
        応答：**7**  # int 型の `7` を返す
        ---
        お客様：7
        応答：**7**  # int 型の `7` を返す
        ---
        お客様：8
        応答：**8**  # int 型の `8` を返す
        ---
        お客様：九
        応答：**9**  # int 型の `9` を返す
        ---
        お客様：9
        応答：**9**  # int 型の `9` を返す
        ---
        お客様が無効な表現（例: 「たくさん」「全員」「大勢」「1人半」など）の場合は、None を返してください。
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


def process_number_of_guests(event):
    session_state = event.get("sessionState", {})
    intent = session_state.get("intent", {})
    intent_name = intent.get("name", "")
    slots = intent.get("slots", {})
    user_input_text = event.get("inputTranscript", "")
    logger.info(f"intent_name: {intent_name}")
    logger.info(f"slots: {slots}")
    logger.info(f"user_input_text: {user_input_text}")
    if event.get("invocationSource") == "DialogCodeHook":
        number_of_guests = None
        if slots:
            logger.info(f"slots: {slots}")
            number_of_guests_slot = slots.get("NumberOfGuests", {})
            if number_of_guests_slot:
                number_of_guests_value = number_of_guests_slot.get("value", {})
                if number_of_guests_value:
                    number_of_guests = number_of_guests_value.get("originalValue", None)
        if number_of_guests is None:
            number_of_guests = user_input_text
        print("number_of_guests_null", number_of_guests)
        print("number_of_guests type", type(number_of_guests))
        if number_of_guests is not None and not isinstance(number_of_guests, int):
            print("number_of_guestsがNoneでもなくint型ではない")
            try:
                number_of_guests = convert_guests_to_number(user_input_text)
                if number_of_guests == "None":
                    number_of_guests = None
                if number_of_guests is None:
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
                            "NumberOfGuests",
                            "無効な入力が続いたため、予約の受付を終了します。",
                            "Fulfilled",
                            "Close",
                            invalid_attempts
                        )
                    else:
                        return response_elicit_session(
                            intent_name,
                            slots,
                            "NumberOfGuests",
                            "入力された値が無効です。正しい利用者人数を入力してください。例: 1,一人,2,二人",
                            "InProgress",
                            "ElicitSlot",
                            invalid_attempts
                        )
            except ValueError:
                return response_elicit_session(
                    intent_name,
                    slots,
                    "NumberOfGuests",
                    "有効な人数を入力してください",
                )
            number_of_guests = int(number_of_guests)
            if number_of_guests and isinstance(number_of_guests, int) and number_of_guests <= 9:
                response = response_elicit_session(
                    intent_name,
                    slots,
                    "RoomType",
                    f" {number_of_guests} 名様の利用者人数を受けたまりました。続きまして部屋タイプを教えてください",
                )
                return response
            else:
                return response_elicit_session(
                    intent_name,
                    slots,
                    "NumberOfGuests",
                    "有効な人数を入力してください",
                )
        else:
            print("number_of_guestsがNoneかint型")
            return response_elicit_session(
                intent_name,
                slots,
                "NumberOfGuests",
                "利用者人数を入力してください",
            )

