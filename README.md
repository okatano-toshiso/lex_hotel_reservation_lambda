# lex_hotel_reservation_lambda

AWS ConnectとLexを使用してホテル予約リクエストを検証および処理するためのAWS Lambda関数です。

## 機能
- チェックイン日、チェックアウト日、部屋タイプ、利用者人数のスロットを処理
- OpenAIのGPTモデルを使用して相対日付や特別なイベントの日付を解析
- 無効な入力に対するエラーメッセージの生成

## ファイル構成
- `lambda_function.py`: Lambda関数のエントリーポイント
- `utils/intent_checkin_date.py`: チェックイン日を処理するユーティリティ
- `utils/intent_checkout_date.py`: チェックアウト日を処理するユーティリティ
- `utils/intent_room_type.py`: 部屋タイプを処理するユーティリティ
- `utils/intent_number_of_guests.py`: 利用者人数を処理するユーティリティ

## 環境変数
- `OPENAI_API_KEY`: OpenAI APIキー

## ログレベル
- `INFO`: 一般的な情報ログ
- `ERROR`: エラーログ

## 使用方法
1. AWS Lambdaにデプロイ
2. AWS ConnectとLexを設定してLambda関数を呼び出す
3. ユーザーの入力に基づいて予約情報を処理

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。
