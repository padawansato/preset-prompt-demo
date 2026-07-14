"""プリセットプロンプトの定義。

実プロダクトなら DB や管理画面で顧客ごとにカスタマイズする部分。
デモでは静的定義とし、「テンプレートをサーバー側で管理し、
利用者はプロンプトを書かない」という構造だけを示す。
"""

from .schemas import Template, TemplateVariable

TEMPLATES: list[Template] = [
    Template(
        id="reply-email",
        title="ビジネスメール返信",
        description="受信メールの要点を踏まえた返信文を作成する",
        prompt_body=(
            "あなたは{industry}業界の営業担当です。以下の受信メールに対する返信を、"
            "{tone}のトーンで、300字以内の日本語で作成してください。\n\n"
            "# 受信メール\n{received_email}"
        ),
        variables=[
            TemplateVariable(name="industry", label="業界", example="IT"),
            TemplateVariable(name="tone", label="トーン", example="丁寧だが簡潔"),
            TemplateVariable(name="received_email", label="受信メール本文", example="お見積りの件、いかがでしょうか…"),
        ],
    ),
    Template(
        id="minutes-summary",
        title="議事録の要約",
        description="会議メモから決定事項とアクションアイテムを抽出する",
        prompt_body=(
            "以下の会議メモを読み、(1)決定事項 (2)アクションアイテム(担当者付き) "
            "(3)持ち越し課題 の3項目で要約してください。対象読者は{audience}です。\n\n"
            "# 会議メモ\n{meeting_notes}"
        ),
        variables=[
            TemplateVariable(name="audience", label="対象読者", example="経営層"),
            TemplateVariable(name="meeting_notes", label="会議メモ", example="7/15 定例。リリースは8月に延期…"),
        ],
    ),
    Template(
        id="job-posting",
        title="求人票ドラフト",
        description="職種と必須条件から求人票の下書きを作成する",
        prompt_body=(
            "{position}の求人票ドラフトを作成してください。必須条件: {requirements}。"
            "会社の魅力: {appeal}。応募したくなる具体的な文面にしてください。"
        ),
        variables=[
            TemplateVariable(name="position", label="職種", example="バックエンドエンジニア"),
            TemplateVariable(name="requirements", label="必須条件", example="Python 3年以上"),
            TemplateVariable(name="appeal", label="会社の魅力", example="フルリモート・AI開発ツール導入済み"),
        ],
    ),
]

TEMPLATE_INDEX: dict[str, Template] = {t.id: t for t in TEMPLATES}
