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


def generate_user_name(user_input_text):
    system_content = """

**目的**:
systemは、userが送信したテキストメッセージから日本人名（フルネーム）を抽出してください。もし名前らしきものがなければ、テキスト全体をカタカナに変換して回答します。
なお、**抽出できなかった旨のメッセージは絶対に返さないでください**。

**指示**:
1. **日本人名の抽出**:
   - 日本人名は、姓と名が組み合わさった形式のものを抽出してください。
   - 日本人名の構成（漢字、ひらがななど）に注意し、明らかに日本人名と判断できるものを抽出します。
   - 可能な限り、姓と名を分けずに、姓名全体を1つの名前として扱ってください。

2. **名前らしきものがない場合**:
   - 名前らしきものが見つからなかった場合は、テキスト全体をカタカナに変換して回答してください。

3. **出力形式**:
   - 抽出した名前のみを回答してください。

**出力例**:

user: 私の名前は開発太郎です。
system（回答）: 開発太郎

user: 名前は高橋健一です。
system（回答）: 高橋健一

user: 山田花子と申します。
system（回答）: 山田花子

user: はじめまして。
system（回答）: ハジメマシテ

user: よろしくお願いします。
system（回答）: ヨロシクオネガイシマス

user: 田中太郎と加藤花子が参加します。
system（回答）: 田中太郎

user: 伊藤純一です。
system（回答）: 伊藤純一

user: 出席者は佐藤一郎と鈴木さちこです。
system（回答）: 佐藤一郎

user: 名前は松本英二郎です。
system（回答）: 松本英二郎

user: どうぞよろしく。
system（回答）: ドウゾヨロシク

user: 私は堀江正人です。
system（回答）: 堀江正人

user: 昨日の参加者は大久保敏郎でした。
system（回答）: 大久保敏郎

user: こんにちは。
system（回答）: コンニチハ

user: 名前は吉田雄也です。
system（回答）: 吉田雄也

**出力例**:

user: こんにちは、私は山本花子です。
system（回答）: 山本花子

user: おはようございます、鈴木健一と申します。
system（回答）: 鈴木健一

user: こんばんは、田中真一郎です。
system（回答）: 田中真一郎

user: はじめまして、渡辺太郎といいます。
system（回答）: 渡辺太郎

user: 私の名前は佐藤ひろしです。
system（回答）: 佐藤ひろし

user: 山田由美といいます、よろしくお願いします。
system（回答）: 山田由美

user: こんにちは、三木あきらです。どうぞよろしく。
system（回答）: 三木あきら

user: 名前は小林優子です。
system（回答）: 小林優子

user: 高橋と申します、どうぞよろしく。
system（回答）: 高橋

user: はじめまして、森田浩二です。
system（回答）: 森田浩二

user: 今日の参加者は松本義之と申します。
system（回答）: 松本義之

user: こんにちは。名前は井上信二です。
system（回答）: 井上信二

user: 名前は杉山真理子と申します。
system（回答）: 杉山真理子

user: 山下太郎と申します、こんにちは。
system（回答）: 山下太郎

user: 出席者は吉川孝子です。
system（回答）: 吉川孝子

user: どうも、石田正人です。
system（回答）: 石田正人

user: こんにちは、上田敏彦です。
system（回答）: 上田敏彦

user: 名前は工藤美咲です。
system（回答）: 工藤美咲

user: おはようございます、伊藤博之と申します。
system（回答）: 伊藤博之

user: はじめまして、椎名亮一です。
system（回答）: 椎名亮一

user: こんにちは、私の名前は中村沙織です。
system（回答）: 中村沙織

user: 初めまして。名前は山本俊です。
system（回答）: 山本俊

user: こんにちは。名前は斉藤花です。
system（回答）: 斉藤花

user: どうぞよろしく、安藤正と申します。
system（回答）: 安藤正

user: 私の名前は藤本由紀子です。
system（回答）: 藤本由紀子

user: あなたの名前は？私は田口剛です。
system（回答）: 田口剛

user: こんばんは、私は秋山浩一です。
system（回答）: 秋山浩一

user: ご紹介します。こちらは森山奈緒子さんです。
system（回答）: 森山奈緒子

user: 今日の担当は木村誠一です。
system（回答）: 木村誠一

user: 名前は伊沢未来です。
system（回答）: 伊沢未来

user: こんにちは、佐野圭一です。
system（回答）: 佐野圭一

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
            "UserName",
            "無効な入力が続いたため、予約の受付を終了します。",
            "Fulfilled",
            "Close",
            invalid_attempts
        )
    return response_elicit_session(
        intent_name,
        slots,
        "UserName",
        "入力された値が無効です。代表のお名前をフルネームで入力してください。",
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


def process_user_name(event):
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
            gpt_user_name = generate_user_name(user_input_text)
            print("gpt_user_name", gpt_user_name)
            if gpt_user_name == "None":
                gpt_user_name = None
            if gpt_user_name is None:
                return handle_invalid_attempts(intent_name, slots, event)
            else:
                lex_user_name = None
                if slots:
                    user_name_slot = slots.get("UserName", {})
                    if user_name_slot:
                        user_name_value = user_name_slot.get("value", {})
                        if user_name_value:
                            lex_user_name = user_name_value.get("interpretedValue", None)
                if lex_user_name == "None":
                    lex_user_name = None
                if lex_user_name is None:
                    return handle_invalid_attempts(intent_name, slots, event)
                else:
                    return response_elicit_session(
                        intent_name,
                        slots,
                        "UserName",
                        f" {gpt_user_name} 代表者様のお名前を受けたまりました。続きまして、当日に連絡可能な電話番号を教えてくてください。",
                    )
        except ValueError:
            return response_elicit_session(
                intent_name,
                slots,
                "UserName",
                "代表者のお名前をフルネームで入力してください。",
            )
    else:
        return response_elicit_session(
            intent_name,
            slots,
            "UserName",
            "代表者のお名前をフルネームで入力してください。",
        )

