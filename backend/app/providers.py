"""LLM プロバイダの抽象化。

実プロダクトは Azure OpenAI / Gemini を基盤にしている（案件票より）。
プロバイダを差し替え可能なインターフェースとして切り、環境変数で選択する:

    LLM_PROVIDER=mock       (デフォルト。外部接続なし。テストはこれで決定的に動く)
    LLM_PROVIDER=openrouter (OPENROUTER_API_KEY が必要。OPENROUTER_MODEL でモデル指定)

OpenRouter は OpenAI 互換の API で多数のモデル (Gemini / GPT / Claude 等) を
同じインターフェースで呼べるゲートウェイ。「基盤モデルを顧客ごとに差し替える」
という実プロダクトの構造を、1プロバイダで擬似的に体験できる。
"""

import os
from abc import ABC, abstractmethod

import httpx


class LLMProvider(ABC):
    """LLM 呼び出しの差し替え口。「プロンプトを受けてテキストを返す」だけに絞る。"""

    name: str

    @abstractmethod
    def generate(self, prompt: str) -> str: ...


class MockProvider(LLMProvider):
    """外部接続なしのダミー実装。デモ・テスト用。"""

    name = "mock"

    def generate(self, prompt: str) -> str:
        return (
            "（モック応答）以下のプロンプトを受け取りました。実運用では "
            "LLM の応答がここに入ります。\n"
            f"--- 受信プロンプト({len(prompt)}文字) ---\n{prompt[:200]}"
        )


class OpenRouterProvider(LLMProvider):
    """OpenRouter (OpenAI 互換 API) 経由で実モデルを呼ぶ。"""

    name = "openrouter"

    def __init__(self) -> None:
        self.api_key = os.environ["OPENROUTER_API_KEY"]
        self.model = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")

    def generate(self, prompt: str) -> str:
        res = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]


def get_provider() -> LLMProvider:
    """環境変数 LLM_PROVIDER で切り替え。既定は mock（明示オプトインで実接続）。"""
    kind = os.environ.get("LLM_PROVIDER", "mock")
    if kind == "openrouter":
        return OpenRouterProvider()
    return MockProvider()
