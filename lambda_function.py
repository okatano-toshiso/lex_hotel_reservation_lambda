import logging
import json
from utils.intent_checkin_date import process_check_in_date
from utils.intent_checkout_date import process_check_out_date
from utils.intent_number_of_guests import process_number_of_guests
from utils.intent_room_type import process_room_type

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"event: {event}")
    print("*****************  OUTPUT1  ******************")

    invocation_label = event.get("invocationLabel", None)

    if invocation_label:
        print(f"現在のinvocationLabelは: {invocation_label}")
    else:
        print("invocationLabelが設定されていません。")

    if invocation_label == "CheckInDateSlot":
        result = process_check_in_date(event)
        return result

    if invocation_label == "CheckOutDateSlot":
        result = process_check_out_date(event)
        return result

    if invocation_label == "NumberOfGuestsSlot":
        result = process_number_of_guests(event)
        return result

    if invocation_label == "RoomTypeSlot":
        result = process_room_type(event)
        return result

