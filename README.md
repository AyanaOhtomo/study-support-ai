# Study Support AI

学習記録 × 可視化 × AIコーチングで学習を継続させるアプリ

プログラミング学習者向けの学習支援アプリです。
学習記録の保存・可視化・AIコーチングを通じて、継続的な学習をサポートします。

---

## アプリ画面

### AIコーチング機能
![AIコーチング](images/ai_coaching.png)


## アプリ概要

* 学習内容を記録（日時・テーマ・理解度など）
* 学習データをダッシュボードで可視化
* AIが週間フィードバックを生成
* AIコーチとチャットで相談できる

**学習記録 × 可視化 × AIコーチング** を組み合わせたアプリです

---

## 主な機能

### 学習記録

* 学習日・テーマ・学習時間を入力
* 理解度・つまずいたポイント・次回やることを記録

---

### ダッシュボード

* 合計学習時間
* 学習回数
* 平均理解度
* 学習テーマ別の学習時間（グラフ）

---

### 学習履歴

* 過去の学習記録を一覧表示
* 日本語ラベルで見やすく整理

---

### AIコーチング

* 今週の学習データをもとにAIがフィードバックを生成
* チャット形式でAIコーチに質問可能

例：

* 「今週は何を優先して復習すべき？」
* 「理解度を上げるにはどうしたらいい？」

---

## 技術スタック

* Python
* Streamlit
* SQLite
* pandas
* Plotly
* OpenAI API
* LangChain
* python-dotenv

---

## アーキテクチャ

```
main.py        ：アプリのエントリーポイント
components.py  ：UI表示ロジック
database.py    ：DB操作
constants.py   ：定数管理
utils.py       ：AI処理（LangChain）
```

 UI / DB / AI を分離した構成にしています

---

## AI機能について

### 使用技術

* OpenAI API
* LangChain（PromptTemplate + ChatOpenAI）

### 工夫した点

* 学習記録データをプロンプトに組み込み
* 個別の学習状況に応じたフィードバックを生成
* AIコーチとして自然な対話体験を実現

---

## セットアップ方法

### 1. リポジトリをクローン

```bash
git clone <リポジトリURL>
cd study-support-ai
```

---

### 2. 仮想環境を作成・有効化

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. 必要パッケージをインストール

```bash
pip install -r requirements.txt
```

---

### 4. `.env` ファイルを作成

```env
OPENAI_API_KEY=your_api_key
```

---

### 5. アプリ起動

```bash
streamlit run main.py
```

---

## 必要パッケージ

```
streamlit
pandas
plotly
openai
langchain
langchain-openai
python-dotenv
```

---

## 今後の改善案

* 学習履歴のフィルタ機能（日付・テーマ）
* 週間レポートのグラフ化
* 学習目標の設定機能
* ユーザー認証

---

## 制作意図

学習を「記録するだけ」で終わらせず、
**振り返り → 改善 → 次の行動** までサポートすることを目的に開発しました。

特にAIコーチング機能では、
単なる要約ではなく「次にどう行動するか」にフォーカスしています。

---

## ポイント

* データの蓄積（SQLite）
* 可視化（Plotly）
* AI活用（LangChain + OpenAI）
* UI / ロジック分離設計

実務を意識した構成（UI / DB / AI分離）で開発しています

