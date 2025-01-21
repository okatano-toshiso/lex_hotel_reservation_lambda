import logging
import json
from utils.intent_checkin_date import process_check_in_date
from utils.intent_number_of_guests import process_number_of_nights

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):  # context を追加
    logger.info(f"event: {event}")
    print("*****************  OUTPUT1  ******************")
    next_state = event.get("proposedNextState", {})
    dialog_action = next_state.get("dialogAction", {})
    slot_to_elicit = dialog_action.get("slotToElicit")

    print("slot_to_elicit", slot_to_elicit)

    print("*****************  OUTPUT2  ******************")

    # セッション状態からスロット情報を取得
    session_state = event.get("sessionState", {})
    intent = session_state.get("intent", {})
    slots = intent.get("slots", {})

    # 現在のスロットを動的に取得
    dialog_action = session_state.get("dialogAction", {})
    current_slot = dialog_action.get("slotToElicit", None)

    print("current_slot", current_slot)

    # スロット値を動的に取得
    if current_slot:
        current_slot_value = (
            slots.get(current_slot, {}).get("value", {}).get("interpretedValue", None)
        )
    else:
        current_slot_value = None

    # レスポンスメッセージの構築
    if current_slot_value:
        message = f"現在のスロット '{current_slot}' の値は {current_slot_value} です。"
    else:
        message = f"現在のスロット '{current_slot}' に値が設定されていません。"

    if slot_to_elicit == "CheckInDate":
        check_in_date = process_check_in_date(event)
        return check_in_date
