"""LLM 実行の観測 (Langfuse)。

Langfuse は LLM アプリのトレース基盤。プロンプト・出力・モデル・レイテンシ・コストを
実行ごとに記録し、あとから評価・改善するための土台をつくる。

セルフホスト (docker compose -f docker-compose.langfuse.yml up -d) で
http://localhost:3001 に立てる想定。キーが未設定なら計装は無効化され、
アプリは JSONL のローカルログだけで通常どおり動く（観測基盤の有無に依存しない設計）。
"""

import os
from contextlib import contextmanager
from typing import Any, Iterator

_client: Any = None


@contextmanager
def trace_attributes(**kwargs: Any) -> Iterator[None]:
    """トレースレベルの属性 (tags, metadata 等) をブロック内の観測に伝播させる。

    Langfuse Python SDK は v4 で OpenTelemetry ベースになり、v3 の
    `span.update_trace()` は廃止されて `propagate_attributes()` に置き換わった。
    Langfuse が未設定・未インストールなら何もしない (no-op) ため、
    観測基盤の有無に関係なくアプリは動く。
    """
    if get_langfuse() is None:
        yield
        return

    from langfuse import propagate_attributes

    with propagate_attributes(**kwargs):
        yield


def get_langfuse() -> Any:
    """Langfuse クライアント。未設定・未インストールなら None を返す。"""
    global _client
    if _client is not None:
        return _client

    if not (os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY")):
        return None

    try:
        from langfuse import Langfuse
    except ImportError:
        return None

    _client = Langfuse(
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        host=os.environ.get("LANGFUSE_HOST", "http://localhost:3001"),
    )
    return _client
