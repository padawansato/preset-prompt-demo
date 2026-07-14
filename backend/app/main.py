"""プリセットプロンプト実行 API。

- GET  /api/templates : プリセット一覧
- POST /api/generate  : テンプレート＋変数 → 検証 → プロンプト組み立て → LLM 呼び出し
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from .providers import get_provider
from .schemas import GenerateRequest, GenerateResponse, Template
from .templates_data import TEMPLATE_INDEX, TEMPLATES

# LLM 実行の観測ログ (最小版)。本番なら Langfuse / LangSmith 等のトレース基盤に流す層。
# 評価・改善はログが残っていて初めて可能になるため、デモでも記録だけは落とす。
LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "generations.jsonl"
LOG_PATH.parent.mkdir(exist_ok=True)

app = FastAPI(title="Preset Prompt Demo API")

# フロント (localhost:3000) からのブラウザ越しアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/templates", response_model=list[Template])
def list_templates() -> list[Template]:
    return TEMPLATES


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    template = TEMPLATE_INDEX.get(req.template_id)
    if template is None:
        raise HTTPException(status_code=404, detail=f"テンプレート {req.template_id} は存在しません")

    # 必須変数がすべて埋まっているかの検証（利用者はプロンプトを書かない分、入力の検証はサーバーの責任）
    required = {v.name for v in template.variables}
    missing = required - req.variables.keys()
    if missing:
        raise HTTPException(status_code=400, detail=f"変数が不足しています: {sorted(missing)}")

    filled_prompt = template.prompt_body.format(**{k: req.variables[k] for k in required})

    provider = get_provider()
    started = time.perf_counter()
    output = provider.generate(filled_prompt)
    latency_ms = round((time.perf_counter() - started) * 1000)

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(),
            "template_id": template.id,
            "provider": provider.name,
            "latency_ms": latency_ms,
            "prompt_chars": len(filled_prompt),
            "output_chars": len(output),
        }, ensure_ascii=False) + "\n")

    return GenerateResponse(
        template_id=template.id,
        filled_prompt=filled_prompt,
        output=output,
        provider=provider.name,
    )
