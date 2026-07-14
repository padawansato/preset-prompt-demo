// バックエンドの Pydantic スキーマ (schemas.py) と対になる TypeScript 型定義。
// API の入出力の「契約」を両側で型として持つ、という構図。

export type TemplateVariable = {
  name: string;
  label: string;
  example: string;
};

export type Template = {
  id: string;
  title: string;
  description: string;
  prompt_body: string;
  variables: TemplateVariable[];
};

export type GenerateResponse = {
  template_id: string;
  filled_prompt: string;
  output: string;
  provider: string;
};

export const API_BASE = "http://localhost:8000";
