import logging
import json
from utils.intent_checkin_date import process_check_in_date
# from utils.intent_number_of_nights import process_number_of_nights

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):  # context を追加
    logger.info(f"{event}")
    print("*****************  OUTPUT  ******************")
    slot_to_elicit = event["proposedNextState"]["dialogAction"]["slotToElicit"]
    logger.info(f"slot_to_elicit: {slot_to_elicit}")
    logger.info(f"dialogAction: {event['proposedNextState']['dialogAction']}")
    if slot_to_elicit == "CheckInDate":
        check_in_date = process_check_in_date(event)
        return check_in_date
    # elif slot_to_elicit == "NumberOfNights":
    #     number_of_nights = process_number_of_nights(event)
    #     return number_of_nights
