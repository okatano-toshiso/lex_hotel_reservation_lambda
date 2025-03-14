import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def hotel_booking_confirm(event):
    # LEXの設定をそのまま活かすため、イベント内の sessionState をそのまま返す
    return event


