"""API のテスト。FastAPI の TestClient はサーバーを立てずにアプリを直接叩ける。

テストは外部 API（OpenRouter）や観測基盤（Langfuse）に依存させない。
.env に本番設定が入っていてもテストは決定的に動くよう、環境変数を上書きしてから
アプリを import する（main.py の load_dotenv より先に環境変数を確定させる必要がある）。
"""

import os

# load_dotenv は既存の環境変数を上書きしないため、ここで先に空値を入れて .env を無効化する
os.environ["LLM_PROVIDER"] = "mock"
os.environ["LANGFUSE_PUBLIC_KEY"] = ""
os.environ["LANGFUSE_SECRET_KEY"] = ""

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_テンプレート一覧が3件返る():
    res = client.get("/api/templates")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 3
    assert {t["id"] for t in body} == {"reply-email", "minutes-summary", "job-posting"}


def test_変数を埋めて生成できる():
    res = client.post(
        "/api/generate",
        json={
            "template_id": "job-posting",
            "variables": {
                "position": "バックエンドエンジニア",
                "requirements": "Python 3年以上",
                "appeal": "AI開発ツール導入済み",
            },
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert "バックエンドエンジニア" in body["filled_prompt"]
    assert body["provider"] == "mock"


def test_変数不足は400():
    res = client.post(
        "/api/generate",
        json={"template_id": "job-posting", "variables": {"position": "エンジニア"}},
    )
    assert res.status_code == 400
    assert "requirements" in res.json()["detail"]


def test_存在しないテンプレートは404():
    res = client.post("/api/generate", json={"template_id": "no-such", "variables": {}})
    assert res.status_code == 404
