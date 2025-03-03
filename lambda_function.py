import logging
import json
from utils.intent_checkin_date import process_check_in_date
from utils.intent_checkout_date import process_check_out_date
from utils.intent_number_of_guests import process_number_of_guests
from utils.intent_room_type import process_room_type
from utils.intent_smoking_preference import process_smoking_preference
from utils.intent_user_name import process_user_name
from utils.intent_phone_number import process_phone_number

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"event: {json.dumps(event, indent=2, ensure_ascii=False)}")  # 入力ログの出力
    print("*****************  OUTPUT1  ******************")

    invocation_label = event.get("invocationLabel", None)

    if invocation_label:
        print(f"現在の invocationLabel は: {invocation_label}")
    else:
        print("invocationLabel が設定されていません。")

    result = None

    if invocation_label == "CheckInDateSlot":
        result = process_check_in_date(event)

    elif invocation_label == "CheckOutDateSlot":
        result = process_check_out_date(event)

    elif invocation_label == "NumberOfGuestsSlot":
        result = process_number_of_guests(event)

    elif invocation_label == "RoomTypeSlot":
        result = process_room_type(event)

    elif invocation_label == "SmokingPreferenceSlot":
        result = process_smoking_preference(event)

    elif invocation_label == "UserNameSlot":
        result = process_user_name(event)

    elif invocation_label == "PhoneNumberSlot":
        result = process_phone_number(event)

        # 🔥 Lex の intent 情報を正しく取得してスロット情報をログに出力
        intent = event.get("sessionState", {}).get("intent", {})
        slots = intent.get("slots", {})

        logger.info(f"修正後の slots: {json.dumps(slots, indent=2, ensure_ascii=False)}")

    if result:
        logger.info(f"Lambda の戻り値: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return result

    # invocationLabel が一致しない場合のエラーハンドリング
    error_response = {
        "sessionState": {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Failed",
                "message": {
                    "contentType": "PlainText",
                    "content": "エラーが発生しました。処理を完了できませんでした。"
                }
            }
        }
    }
    logger.error("エラー: 適切な invocationLabel が見つかりませんでした。")
    return error_response
