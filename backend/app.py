import json
import os
import tempfile

from flask import Flask, jsonify, request
import fitz  # PyMuPDF
import requests

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def extract_text(pdf_path: str):
    """Extract all text from a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    texts = [page.get_text("text") for page in doc]
    return "\n\n".join(texts), len(doc)


def summarize_with_llm(text: str):
    """Summarize the extracted PDF text using an OpenAI chat completion."""
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY が設定されていません")

    max_chars = 15000
    if len(text) > max_chars:
        text = text[:max_chars]

    system_prompt = (
        "あなたはPDF文書を要約する日本語アシスタントです。"
        "ユーザーに代わって文書全体像を掴みやすく整理してください。"
    )

    user_prompt = (
        "以下はPDFから抽出したテキストです。\n"
        "次の形式のJSONだけを返してください。\n"
        '{\n'
        '  "summary": "文書全体の要約",\n'
        '  "sections": [\n'
        '    { "heading": "セクション名", "summary": "その要約" }\n'
        '  ]\n'
        '}\n'
        "余計な説明文は書かず、必ず有効なJSONのみを返してください。\n\n"
        "=== テキスト開始 ===\n"
        f"{text}\n"
        "=== テキスト終了 ==="
    )

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json={
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"LLM API error: {response.text}")

    content = response.json()["choices"][0]["message"]["content"]

    try:
        data = json.loads(content)
        summary = data.get("summary", "").strip()
        sections = data.get("sections", [])
    except Exception:
        summary = content.strip()
        sections = []

    return summary, sections


@app.route("/api/mvp/analyze", methods=["POST"])
def analyze_pdf_mvp():
    """Accept a PDF upload, extract text, and summarize it using the MVP flow."""
    if "file" not in request.files:
        return jsonify({"error": "PDFファイルが指定されていません"}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "PDFファイルのみアップロード可能です"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        file.save(tmp.name)
        pdf_path = tmp.name

    try:
        text, pages = extract_text(pdf_path)
        summary, sections = summarize_with_llm(text)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    finally:
        try:
            os.remove(pdf_path)
        except OSError:
            pass

    return jsonify(
        {
            "title": file.filename,
            "pages": pages,
            "summary": summary,
            "sections": sections,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
