#!/usr/bin/env python3
"""Alfred Script Filter: translates words between Chinese and English via DeepSeek API."""
import json
import os
import re
import sys
import urllib.request
import urllib.error


def _env_int(key, default):
    v = os.environ.get(key, "").strip()
    if not v:
        return default
    try:
        return int(v)
    except ValueError:
        return default


def _env_float(key, default):
    v = os.environ.get(key, "").strip()
    if not v:
        return default
    try:
        return float(v)
    except ValueError:
        return default


def _env_truthy(key, default=False):
    v = os.environ.get(key, "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "on")


def get_config():
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
    api_base = os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com")
    # Optional tuning (Configure Workflow); lower max_tokens = faster / cheaper completions
    max_tokens = _env_int("DEEPSEEK_MAX_TOKENS", 200)
    # Lower temperature improves consistency / “hit rate” on short glosses
    temperature = _env_float("DEEPSEEK_TEMPERATURE", 0.05)
    thinking = _env_truthy("DEEPSEEK_THINKING", False)
    return api_key, model, api_base.rstrip("/"), max_tokens, temperature, thinking


def detect_language(text):
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff":
            return "zh"
    return "en"


def parse_input(query):
    if "//" in query:
        parts = query.split("//", 1)
        return parts[0].strip(), parts[1].strip()
    return "", query.strip()


def build_messages(context, word):
    lang = detect_language(word)
    source = "Chinese" if lang == "zh" else "English"
    target = "English" if lang == "zh" else "Chinese"

    system = (
        "You are an expert bilingual lexicographer for Chinese and English.\n"
        "Hard rules:\n"
        "1) Translate ONLY the exact string on the TARGET line. Treat it as literal surface text; "
        "do not substitute a different English word or concept (e.g. never interpret the greeting "
        "\"hello\" as \"query\").\n"
        "2) If OPTIONAL_CONTEXT is \"(none)\", pick the most common everyday sense (conversation, news, general prose).\n"
        "3) If OPTIONAL_CONTEXT is not none, prefer the sense that fits that domain.\n"
        "4) Output 1\u20133 lines only. Each line MUST be exactly:\n"
        "   translation (part of speech) \u2014 brief gloss\n"
        "   Use an em dash (—) between gloss and explanation; keep the gloss short.\n"
        "5) The text before \"(\" must be a concise dictionary equivalent, not a long paraphrase.\n"
        "6) No numbering, bullets, headings, code fences, or any text before or after the lines.\n"
        "Example pattern (English\u2192Chinese):\n"
        "TARGET: hello\n"
        "你好 (interjection) \u2014 common greeting\n"
        "喂 (interjection) \u2014 answer phone / get attention\n"
        "嗨 (interjection) \u2014 informal hi"
    )

    ctx_line = context if context else "(none)"
    user_msg = (
        f"TARGET: {word}\n"
        f"SOURCE_LANGUAGE: {source}\n"
        f"TARGET_LANGUAGE: {target}\n"
        f"OPTIONAL_CONTEXT: {ctx_line}\n"
        "\n"
        f"Give up to 3 best {target} equivalents for TARGET, ordered by frequency/naturalness in {target}."
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]


def call_api(api_key, model, api_base, messages, max_tokens, temperature, thinking):
    url = f"{api_base}/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    thinking_type = "enabled" if thinking else "disabled"
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "thinking": {"type": thinking_type},
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    msg = result["choices"][0]["message"]
    text = msg.get("content") or ""
    # Thinking mode may put final answer in content; reasoning in reasoning_content
    return text.strip()


def _strip_markdown_fence(text):
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        while lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t


def _gloss_head(line):
    """Part before em/en dash gloss; models sometimes use '-' instead of '—'."""
    for sep in ("\u2014", "\u2013", "—", "–"):
        if sep in line:
            return line.split(sep, 1)[0].strip()
    if " - " in line:
        return line.split(" - ", 1)[0].strip()
    return line.strip()


def alfred_json(items):
    print(json.dumps({"items": items}, ensure_ascii=False))


def make_item(title, subtitle="", arg=None, valid=True):
    obj = {
        "title": title,
        "subtitle": subtitle,
        "valid": valid,
        "icon": {"path": "icon.png"},
    }
    if arg is not None:
        obj["arg"] = arg
        obj["text"] = {"copy": arg, "largetype": title}
    return obj


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""

    if not query.strip():
        alfred_json([make_item(
            "Type a word to translate",
            "Format: word   or   context // word",
            valid=False,
        )])
        return

    api_key, model, api_base, max_tokens, temperature, thinking = get_config()

    if not api_key:
        alfred_json([make_item(
            "\u26a0\ufe0f  API Key not configured",
            "Click 'Configure Workflow...' to set API Key",
            valid=False,
        )])
        return

    context, word = parse_input(query)

    if not word:
        alfred_json([make_item(
            "Type a word after //",
            "Format: context // word",
            valid=False,
        )])
        return

    try:
        messages = build_messages(context, word)
        result = call_api(api_key, model, api_base, messages, max_tokens, temperature, thinking)
        result = _strip_markdown_fence(result)

        lines = [l.strip() for l in result.strip().splitlines() if l.strip()]
        lines = [re.sub(r"^\d+[.)]\s*", "", l) for l in lines]

        ctx_hint = f"  \u00b7  Context: {context}" if context else ""
        items = []
        for line in lines:
            if not line:
                continue
            copy_text = _gloss_head(line).split("(")[0].strip()
            items.append(make_item(
                line,
                f"\u21a9 Copy \"{copy_text}\"{ctx_hint}",
                arg=copy_text,
            ))

        if not items:
            items.append(make_item(result.strip(), "\u21a9 Copy", arg=result.strip()))

        alfred_json(items)

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        alfred_json([make_item("\u274c  API Error", f"{e.code} \u2014 {body[:120]}", valid=False)])
    except urllib.error.URLError as e:
        alfred_json([make_item("\u274c  Network Error", str(e.reason), valid=False)])
    except Exception as e:
        alfred_json([make_item("\u274c  Error", str(e), valid=False)])


if __name__ == "__main__":
    main()
