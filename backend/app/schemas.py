"""API の入出力スキーマ。

FastAPI は Pydantic モデルの型ヒントから、リクエストの検証と
OpenAPI ドキュメント (/docs) を自動生成する。Django の Serializer に相当するが、
「型ヒントがそのまま検証ルールになる」のが FastAPI の特徴。
"""

from pydantic import BaseModel, Field


class TemplateVariable(BaseModel):
    """テンプレート内の変数スロット1個の定義。"""

    name: str = Field(description="プロンプト本文中の {name} に対応")
    label: str = Field(description="画面に表示する日本語ラベル")
    example: str = Field(description="プレースホルダとして見せる入力例")


class Template(BaseModel):
    """プリセットプロンプト1件。"""

    id: str
    title: str
    description: str
    prompt_body: str = Field(description="{変数名} を含むプロンプト本文")
    variables: list[TemplateVariable]


class GenerateRequest(BaseModel):
    template_id: str
    variables: dict[str, str] = Field(description="変数名 → ユーザー入力値")


class GenerateResponse(BaseModel):
    template_id: str
    filled_prompt: str = Field(description="変数を埋めた最終プロンプト")
    output: str = Field(description="LLM の生成結果")
    provider: str = Field(description="使用した LLM プロバイダ名")
