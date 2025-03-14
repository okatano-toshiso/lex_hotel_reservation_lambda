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
assistantは、userが送信したテキストメッセージから日本人名を抽出し、カタカナで回答します。もし名前らしきものがなければ、テキスト全体をカタカナに変換して回答します。なお、**抽出できなかった旨のメッセージは絶対に返さないでください**。

**指示**:
1. **日本人名の抽出**:
   - 日本人名は、姓と名が組み合わさった形式のものを抽出してください。
   - 日本人名の構成（漢字、ひらがななど）に注意して、明らかな日本人名と判断できるものを抽出します。
   - 可能な限り、姓と名を分けずに、姓名全体を1つの名前として扱ってください。

2. **カタカナへの変換**:
   - 抽出した名前を正確にカタカナに変換してください。
   - ひらがな、漢字、アルファベット、句読点、記号など、カタカナ以外の文字は含めないでください。

3. **名前らしきものがない場合**:
   - 名前らしきものが見つからなかった場合は、テキスト全体をカタカナに変換して回答してください。
   - **必ずカタカナで返答し、"抽出できませんでした"などのメッセージは絶対に返さないでください**。

4. **出力形式**:
   - 抽出した名前のみ、またはカタカナに変換したテキスト全体を回答として表示してください。

**出力例**:

user: 私の名前は開発太郎です。
assistant（回答）: カイハツタロウ

user: 開発太郎です。
assistant（回答）: カイハツタロウ

user: 開発太郎と申します。
assistant（回答）: カイハツタロウ

user: はじめまして。
assistant（回答）: ハジメマシテ

user: 名前は高橋健一です。
assistant（回答）: タカハシケンイチ

user: よろしくお願いします。
assistant（回答）: ヨロシクオネガイシマス

user: 山田太郎です。
system（名前抽出）: 山田太郎
system（カタカナ変換）: ヤマダタロウ
assistant（回答）: ヤマダタロウ

user: 私の名前は鈴木一郎です。
system（名前抽出）: 鈴木一郎
system（カタカナ変換）: スズキイチロウ
assistant（回答）: スズキイチロウ

user: こんにちは、田中花子と申します。
system（名前抽出）: 田中花子
system（カタカナ変換）: タナカハナコ
assistant（回答）: タナカハナコ

user: どうも、私は佐々木健です。
system（名前抽出）: 佐々木健
system（カタカナ変換）: ササキケン
assistant（回答）: ササキケン

user: はじめまして、渡辺綾乃です。
system（名前抽出）: 渡辺綾乃
system（カタカナ変換）: ワタナベアヤノ
assistant（回答）: ワタナベアヤノ

user: 僕は小池百合子です。
system（名前抽出）: 小池百合子
system（カタカナ変換）: コイケユリコ
assistant（回答）: コイケユリコ

user: 名前は高橋健一です。
system（名前抽出）: 高橋健一
system（カタカナ変換）: タカハシケンイチ
assistant（回答）: タカハシケンイチ

user: よろしく、私は大野由美です。
system（名前抽出）: 大野由美
system（カタカナ変換）: オオノユミ
assistant（回答）: オオノユミ

user: こんにちは、私は石田光です。
system（名前抽出）: 石田光
system（カタカナ変換）: イシダヒカル
assistant（回答）: イシダヒカル

user: 僕の名前は佐藤次郎です。
system（名前抽出）: 佐藤次郎
system（カタカナ変換）: サトウジロウ
assistant（回答）: サトウジロウ

user: 私は松本理恵です、よろしく。
system（名前抽出）: 松本理恵
system（カタカナ変換）: マツモトリエ
assistant（回答）: マツモトリエ

user: 私は青木圭介です。
system（名前抽出）: 青木圭介
system（カタカナ変換）: アオキケイスケ
assistant（回答）: アオキケイスケ

user: 私の名前は西川健です。
system（名前抽出）: 西川健
system（カタカナ変換）: ニシカワケン
assistant（回答）: ニシカワケン

user: 僕は中村義行です。
system（名前抽出）: 中村義行
system（カタカナ変換）: ナカムラヨシユキ
assistant（回答）: ナカムラヨシユキ

user: 名前は川崎真由美です。
system（名前抽出）: 川崎真由美
system（カタカナ変換）: カワサキマユミ
assistant（回答）: カワサキマユミ

user: お世話になります、私の名前は村上亮太です。
system（名前抽出）: 村上亮太
system（カタカナ変換）: ムラカミリョウタ
assistant（回答）: ムラカミリョウタ

user: どうぞよろしく、私は藤田友美です。
system（名前抽出）: 藤田友美
system（カタカナ変換）: フジタユウミ
assistant（回答）: フジタユウミ

user: 田村幸子です、よろしくお願いします。
system（名前抽出）: 田村幸子
system（カタカナ変換）: タムラサチコ
assistant（回答）: タムラサチコ

user: 山下真奈美です。
system（名前抽出）: 山下真奈美
system（カタカナ変換）: ヤマシタマナミ
assistant（回答）: ヤマシタマナミ

user: どうも、松田幸です。
system（名前抽出）: 松田幸
system（カタカナ変換）: マツダミユキ
assistant（回答）: マツダミユキ

user: 本日はお世話になります。
assistant（回答）: ホンジツハオセワニナリマス

user: ありがとうございます。
assistant（回答）: アリガトウゴザイマス

user: 私の仕事はソフトウェア開発です。
assistant（回答）: ワタシノシゴトハソフトウェアカイハツデス

user: 今日の天気は晴れですね。
assistant（回答）: キョウノテンキハハレデスネ

user: 来週の会議は水曜日です。
assistant（回答）: ライシュウノカイギハスイヨウビデス

user: 私の好きな色は青です。
assistant（回答）: ワタシノスキナイロハアオデス

user: はじめまして、あなたのお名前は何ですか？
assistant（回答）: ハジメマシテ、アナタノオナマエハナンデスカ

user: 私の住所は東京都港区です。
assistant（回答）: ワタシノジュウショハトウキョウトミナトクデス

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
            "Fulfilled",
            "Close",
            invalid_attempts
        )
    return response_elicit_session(
        intent_name,
        slots,
        "UserName",
        "InProgress",
        "ElicitSlot",
        invalid_attempts
    )


def sanitize_name(name):
    """
    Args:name (str): The name to be sanitized.
    Returns:str: The sanitized name.
    """
    sanitized_name = name.strip()
    sanitized_name = re.sub(r'[^\w\s]', '', sanitized_name)
    sanitized_name = re.sub(r'\s+', '', sanitized_name)
    return sanitized_name


def check_name_length(name, max_length=30):
    """
    max_length (int, optional): The maximum allowed length for the name. Defaults to 50.
    """
    return (None, len(name)) if len(name) >= max_length + 1 else (name, len(name))


def check_name_null(name):
    """
    Checks if the given value is None or the string "None".
    """
    return None if name is None or name == "" else name


def response_elicit_session(
        intent_name,
        slots=None,
        slot_to_elicit=None,
        state="InProgress",
        type="Delegate",
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
        }
    }


def process_user_name(event):
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
            gpt_user_name = generate_user_name(user_input_text)
            gpt_user_name = sanitize_name(gpt_user_name)
            gpt_user_name, gpt_name_length = check_name_length(gpt_user_name)
            print("gpt_check_name_length", gpt_name_length)
            gpt_user_name = check_name_null(gpt_user_name)
            print("gpt_check_name_null", gpt_user_name)

            if not gpt_user_name:
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
                lex_user_name = sanitize_name(lex_user_name)
                print("lex_user_name", lex_user_name)
                lex_user_name, lex_name_length = check_name_length(lex_user_name)
                print("lex_user_name_length", lex_name_length)
                print("lex_check_name_length", lex_user_name)
                lex_user_name = check_name_null(lex_user_name)
                print("lex_check_name_null", lex_user_name)
                if not lex_user_name:
                    lex_user_name = None
                if lex_user_name is None:
                    return handle_invalid_attempts(intent_name, slots, event)
                else:

                    return response_elicit_session(
                        intent_name,
                        slots,
                        "UserName"
                    )
        except ValueError:
            return response_elicit_session(
                intent_name,
                slots,
                "UserName"
            )
    else:
        return response_elicit_session(
            intent_name,
            slots,
            "UserName"
        )

