from __future__ import annotations

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "auth.invalid_credentials": "Invalid username or password.",
        "auth.user_exists": "Username is already taken.",
        "auth.user_not_found": "User not found.",
        "auth.user_not_ready": "RBAC bootstrap is incomplete. Please contact administrator.",
        "auth.unauthorized": "Authentication required.",
        "auth.forbidden": "You do not have enough permissions to perform this action.",
        "graph.unavailable": "Graph service is currently unavailable.",
        "graph.interrupt_confirmation": (
            "The assistant is ready to execute a sensitive action. "
            "Reply with 'y' to continue, or provide your requested change."
        ),
        "health.ok": "ok",
    },
    "zh": {
        "auth.invalid_credentials": "用户名或密码错误。",
        "auth.user_exists": "用户名已存在。",
        "auth.user_not_found": "用户不存在。",
        "auth.user_not_ready": "RBAC 初始化未完成，请联系管理员。",
        "auth.unauthorized": "需要登录认证。",
        "auth.forbidden": "你没有执行该操作的权限。",
        "graph.unavailable": "工作流服务当前不可用。",
        "graph.interrupt_confirmation": (
            "AI助手准备执行敏感操作。输入'y'继续，或说明你希望修改的内容。"
        ),
        "health.ok": "正常",
    },
}


def detect_locale(accept_language: str | None) -> str:
    if not accept_language:
        return "en"
    lowered = accept_language.lower()
    if lowered.startswith("zh"):
        return "zh"
    return "en"


def t(key: str, locale: str = "en", **kwargs: object) -> str:
    template = TRANSLATIONS.get(locale, TRANSLATIONS["en"]).get(
        key, TRANSLATIONS["en"].get(key, key)
    )
    return template.format(**kwargs)
