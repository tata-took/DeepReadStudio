# DeepRead Studio (MVP)

DeepRead Studioは、PDFファイルをアップロードするだけでAIによる要約を生成する最小限のバックエンドAPIです。本リポジトリはMVPに必要な機能のみに絞り込み、余計な認証や外部連携、非同期処理などはすべて削除しています。

## 提供機能

- `POST /api/mvp/analyze`
  - PDFファイルを受け取り、PyMuPDFでテキスト抽出
  - OpenAI API (Chat Completions) を呼び出してJSON形式の要約を作成
  - 文書タイトル（アップロード時のファイル名）、ページ数、全体要約、セクション要約を返却

## アーキテクチャ

```
Flask (APIサーバー)
└── PyMuPDF: PDFテキスト抽出
└── OpenAI API: 要約生成
```

## 必要要件

- Python 3.10+
- OpenAI APIキー (`OPENAI_API_KEY`)

## セットアップ

1. 依存ライブラリをインストール

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. 環境変数を設定

   ```bash
   export OPENAI_API_KEY="sk-..."
   # 任意: 使用するモデルを変更する場合は以下を設定
   export OPENAI_MODEL="gpt-4.1-mini"
   ```

3. サーバーを起動

   ```bash
   python app.py
   ```

   デフォルトで `http://127.0.0.1:5000` が開きます。

## 使い方

`curl` を使ってPDFを送信する例:

```bash
curl -X POST \
  -F "file=@/path/to/document.pdf" \
  http://127.0.0.1:5000/api/mvp/analyze
```

成功すると以下のようなJSONレスポンスが返ります。

```json
{
  "title": "document.pdf",
  "pages": 12,
  "summary": "文書全体の要約テキスト...",
  "sections": [
    { "heading": "セクション1", "summary": "要約..." },
    { "heading": "セクション2", "summary": "要約..." }
  ]
}
```

## エラーハンドリング

- `400 Bad Request`: ファイル未指定、またはPDF以外のファイルを送信した場合
- `500 Internal Server Error`: PDF解析やLLM呼び出しで失敗した場合（エラーメッセージは `error` フィールドに含まれます）

## ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。
