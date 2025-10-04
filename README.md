# 🏨 Lex Hotel Reservation Lambda

AWS ConnectとAmazon Lexを使用して、ホテル予約リクエストを**検証・処理**するためのAWS Lambda関数です。  
音声またはテキスト入力を通じて、宿泊予約の自動化を実現します。

---

## 📚 目次

- [概要](#-概要)
- [特徴](#-特徴)
- [アーキテクチャ構成](#-アーキテクチャ構成)
- [ディレクトリ構成](#-ディレクトリ構成)
- [主要機能](#-主要機能)
- [セットアップ手順](#-セットアップ手順)
- [デプロイ方法](#-デプロイ方法)
- [テスト](#-テスト)
- [ライセンス](#-ライセンス)
- [作者情報](#-作者情報)
- [参考資料](#-参考資料)

---

## 🧠 概要

このLambda関数は、**Amazon Lex**（音声・テキストボット）と**Amazon Connect**（コールセンターサービス）を連携し、  
ホテル予約に関するユーザーのリクエストを受け取り、**検証・確認・登録**を行います。

主な目的は、宿泊予約プロセスを自動化し、オペレーターの負担を軽減することです。

---

## ✨ 特徴

- 🗣️ **音声・テキスト両対応**（Amazon Lex経由）  
- 🧾 **入力検証**（日付・人数・部屋タイプなど）  
- 🔄 **AWS Connect連携** によるリアルタイム応答  
- ☁️ **サーバーレス構成**（AWS Lambda + API Gateway）  
- 🧩 **拡張性の高い設計**（他システムとの統合が容易）

---

## 🏗️ アーキテクチャ構成

```
ユーザー（音声/テキスト）
   ↓
Amazon Connect / Amazon Lex
   ↓
AWS Lambda (lex_hotel_reservation_lambda)
   ↓
DynamoDB / API / 外部予約システム
```

---

## 📁 ディレクトリ構成

```
lex_hotel_reservation_lambda/
├── lambda_function.py        # メインロジック
├── validation.py             # 入力検証（チェックイン日・人数など）
├── response_builder.py       # Lex形式のレスポンス生成
├── utils/                    # 共通ユーティリティ
│   ├── date_utils.py         # 日付処理
│   ├── room_utils.py         # 部屋タイプ判定
│   └── logger.py             # CloudWatchログ出力
├── requirements.txt          # 依存パッケージ
└── README.md                 # 本ドキュメント
```

---

## ⚙️ 主要機能

| 機能 | 説明 |
|------|------|
| **Intent解析** | Lexから送信されたインテントを解析し、予約・キャンセル・確認などを判定 |
| **スロット検証** | チェックイン日、宿泊日数、人数などの入力を検証 |
| **レスポンス生成** | Lex形式のJSONレスポンスを構築し、Connectへ返却 |
| **外部連携** | DynamoDBや外部APIを通じて予約情報を登録・更新 |

---

## 🧰 セットアップ手順

```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

---

## 🚀 デプロイ方法

1. AWSコンソールでLambda関数を作成  
2. `lambda_function.py` をアップロード  
3. Amazon LexのFulfillment設定でこのLambdaを指定  
4. Amazon ConnectフローにLexボットを統合  

---

## 🧪 テスト

ローカルまたはAWSコンソール上でテストイベントを実行できます。

```bash
python lambda_function.py
```

または、Lexのテストコンソールで対話テストを行います。

---

## 📄 ライセンス

このプロジェクトは社内利用を目的としており、外部公開は想定していません。

---

## 👤 作者情報

| 項目 | 内容 |
|------|------|
| **名前** | 岡田 俊宏 (Toshihiro Okada) |
| **GitHub** | [okatano-toshiso](https://github.com/okatano-toshiso) |
| **所属** | SynapseAI |
| **Webサイト** | [https://github.com/okatano-toshiso/synapseai](https://github.com/okatano-toshiso/synapseai) |
| **専門分野** | AIソリューション開発・AWSサーバーレス設計・自然言語処理 |

---

### 🧩 作者メッセージ

> 「AIとクラウドの融合で、業務をよりスマートに。」

このLambdaは、SynapseAIのAIソリューション開発の一環として設計されました。  
AWSのサーバーレス技術を活用し、**音声認識 × 自然言語理解 × 自動応答** による  
次世代のホテル予約体験を実現します。

---

## 🧭 参考資料

> 本READMEは以下の資料を参考に、構造性・可読性・開発者体験を重視して作成されています。

- [GitHub公式: READMEの書き方](https://docs.github.com/ja/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
- [Qiita: READMEの書き方まとめ](https://qiita.com/shun198/items/c983c713452c041ef787)
- [C++ Learning: READMEの基本構成](https://cpp-learning.com/readme/)
- [Reddit: Good README Templates](https://www.reddit.com/r/programming/comments/l0mgcy/github_readme_templates_creating_a_good_readme_is/?tl=ja)

---
