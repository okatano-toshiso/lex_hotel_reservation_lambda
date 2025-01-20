import logging
import json
from utils.intent_checkin_date import process_check_in_date
from utils.intent_checkout_date import process_check_out_date
from utils.intent_number_of_nights import process_number_of_nights

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
        check_in_date = process_check_in_date(event)
        return check_in_date

    if invocation_label == "CheckOutDateSlot":
        check_in_date = process_check_out_date(event)
        return check_in_date
