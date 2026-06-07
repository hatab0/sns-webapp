"""
YouTubeエージェント（一体型）
Instagramスクリプトを受け取りYouTube Shorts専用コンテンツを生成。
2026年アルゴリズム対応：視聴完了率・検索SEO・早期エンゲージメントを最大化。
海外（北米）向け英語コンテンツ。
"""
import anthropic
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

from utils.baby_config import BIRTH_DATE, calc_month_age, calc_weeks_alive, calc_week_in_month

MONTH_AGE = calc_month_age()

BABY_MILESTONE_BY_MONTH = {
    0:  "Documenting senacci's very first days — newborn cries and all.",
    1:  "Capturing senacci's first cooing sounds at 1 month old.",
    2:  "Senacci's first smiles are just starting to appear at 2 months.",
    3:  "Neck control growing, smiles blooming — senacci at 3 months.",
    4:  "Full head control, big grins every day — senacci at 4 months.",
    5:  "Babbling begins, learning to scoot — senacci at 5 months.",
    6:  "Starting solids and crawling practice — senacci at 6 months.",
    7:  "Crawling attempts and separation anxiety — senacci at 7 months.",
    8:  "Getting better at crawling every day — senacci at 8 months.",
    9:  "Pulling up to stand — senacci's big milestone at 9 months.",
    10: "First words appearing, cruising along furniture — senacci at 10 months.",
    11: "Almost walking, almost 1 year old — senacci at 11 months.",
    12: "First birthday! First steps! — senacci at 12 months.",
    13: "Wobbly walking getting steadier — senacci at 13 months.",
    14: "Words starting to emerge — senacci at 14 months.",
    15: "Moving toward two-word phrases — senacci at 15 months.",
}


def get_fixed_footer() -> str:
    milestone = BABY_MILESTONE_BY_MONTH.get(
        MONTH_AGE,
        f"Documenting senacci's growth at {MONTH_AGE} months old."
    )
    return (
        "\n━━━━━━━━━━━━━━━\n"
        "📱 Baby Boo SNS\n"
        "⭐️ Instagram → https://www.instagram.com/aibaby.jp/\n"
        "   Search → @aibaby.jp\n"
        "\n〜About Baby Boo〜\n"
        "A Japanese dad sharing his real baby's growth through AI visuals —\n"
        "because he loves her too much to show her face online. 🇯🇵🍼\n"
        f"{milestone}\n"
        "Dad of 2, on parental leave, capturing every tiny milestone.\n"
        "Fellow parents — drop a comment and let's connect! 👇\n"
        "━━━━━━━━━━━━━━━"
    )


def _parse_json(text: str) -> dict:
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except Exception:
        return {}


def _run_normal(instagram_script: dict, product: dict) -> dict:
    """通常mode: English YouTube Shorts caption for product promotion"""
    hook = instagram_script.get("hook", "")
    concept = instagram_script.get("viral_concept", "")

    prompt = f"""
You are a YouTube Shorts creator running a baby content channel.
Generate English content for a product review Short featuring "senacci", a {MONTH_AGE}-month-old baby shown through AI visuals (real baby, privacy protected).
Channel angle: Japanese dad reviewing baby products.

Hook: {hook}
Concept: {concept}
Product: {product["name"]}

TITLE RULES:
- 50-70 characters total (first 40 chars visible in Shorts feed — keyword goes there)
- Lead with the product benefit or baby reaction
- Include baby's age or "Japanese baby dad" for context
- End with " #Shorts"
- Example: "Japanese dad tested this on his {MONTH_AGE}-month-old 🍼 #Shorts"

DESCRIPTION RULES:
- 2-3 sentences, natural English, SEO keyword-rich
- Mention the product name naturally in the first sentence
- CTA: "Save this for your own baby essentials list! 🙌"
- Hashtags on a new line: #Shorts #baby #babyboo #PR #babyproducts
- Max 5 hashtags

PIN COMMENT RULES:
- 1-2 lines English
- "🍼 Real baby, AI visuals — a Japanese dad reviewing baby must-haves."
- Add: "Find the product link in our Rakuten ROOM 👇"

Output JSON only. No preamble.
{{
  "title": "YouTube title (under 100 chars)",
  "description": "description text with hashtags",
  "pin_comment": "pin comment text"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json(message.content[0].text.strip())


def _run_buzz_en(instagram_script: dict) -> dict:
    """バズmode: English YouTube Shorts — kawaii + Japanese dad angle"""
    hook = instagram_script.get("hook", "")
    concept = instagram_script.get("viral_concept", "")

    prompt = f"""
You are a viral YouTube Shorts creator running a baby content channel.
Generate English content for a Short featuring "senacci", a {MONTH_AGE}-month-old baby shown through AI visuals (real baby, privacy protected).
Channel angle: Japanese dad sharing kawaii moments with the world. 🇯🇵

Hook: {hook}
Concept: {concept}

TITLE RULES:
- 50-70 characters total (first 40 chars visible in Shorts feed — keyword goes first)
- Lead with emotion or curiosity. Use one of these angles:
  • "This Japanese baby is too kawaii [emoji] #Shorts"
  • "POV: you just met the cutest Japanese baby 🍼 #Shorts"
  • "Can't stop watching this Japanese baby [emoji] #Shorts"
  • "This baby's face just healed my whole week #Shorts"
  • "Japanese dad's baby [action] and it's the cutest thing #Shorts"
- Include "kawaii" or "Japanese" to differentiate
- End with " #Shorts"

DESCRIPTION RULES:
- 2-3 sentences, natural English, keyword-rich for SEO
- Sentence 1: context ("A Japanese dad sharing his baby's cutest moments through AI visuals. 🇯🇵")
- Sentence 2: emotional CTA hook ("Comment 🥺 if this healed your whole day!")
- Hashtags on a new line: #Shorts #cutebaby #kawaii #baby #babyboo
- Max 5 hashtags

PIN COMMENT RULES:
- 1-2 lines English
- Start with: "🍼 Real baby, AI visuals —"
- Add a warm one-liner about the channel angle
- End with subscribe CTA ("Subscribe to watch her grow 👶")

Output JSON only. No preamble.
{{
  "title": "YouTube title (under 100 chars)",
  "description": "description text with hashtags",
  "pin_comment": "pin comment text"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json(message.content[0].text.strip())


def _run_milestone(instagram_script: dict) -> dict:
    """マイルストーン: English weekly growth record YouTube Shorts"""
    week_in_month = calc_week_in_month()
    weeks_alive   = calc_weeks_alive()

    prompt = f"""
You are a YouTube Shorts creator documenting a baby's weekly growth.
Generate English content for a weekly growth record Short featuring "senacci" at {MONTH_AGE} months old
(week {week_in_month} of this month, week {weeks_alive} of life overall).
Channel angle: Japanese dad capturing every milestone through AI visuals.

TITLE RULES:
- 50-70 characters
- Format around "{MONTH_AGE}-month-old" and growth/change
- Emotional angle: "growing too fast", "changed so much this week", "can't believe it"
- End with " #Shorts"
- Example: "{MONTH_AGE}-month-old baby changed so much this week 😭 #Shorts"

DESCRIPTION RULES:
- 2-3 sentences in natural English
- Mention a realistic milestone for a {MONTH_AGE}-month-old (cooing, smiling, rolling, crawling, etc.)
- End with: "How is your baby growing? Share in the comments! 👇"
- Hashtags on a new line: #Shorts #baby #babyboo #babymonths #babygrowth
- Max 5 hashtags

PIN COMMENT RULES:
- 1-2 lines English
- "🍼 Weekly growth diary — real baby, AI visuals, Japanese dad."
- Subscribe CTA

Output JSON only. No preamble.
{{
  "title": "YouTube title (under 100 chars)",
  "description": "description text with hashtags",
  "pin_comment": "pin comment text"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json(message.content[0].text.strip())


def run(instagram_script: dict, product: dict = None) -> dict:
    """
    Instagramスクリプトを受け取りYouTube Shorts専用コンテンツを生成。
    product=None のときはバズmode（#PRなし・バズ特化キャプション）。
    instagram_script の captions に youtube_title / youtube / pin_comment を追記して返す。
    """
    global MONTH_AGE
    MONTH_AGE = calc_month_age()
    is_buzz = product is None

    if is_buzz and instagram_script.get("is_milestone"):
        result = _run_milestone(instagram_script)
        default_title = f"{MONTH_AGE}-month-old baby growth record 🍼 #Shorts"
    elif is_buzz:
        result = _run_buzz_en(instagram_script)
        default_title = f"This Japanese baby is too kawaii 🥺 #Shorts"
    else:
        result = _run_normal(instagram_script, product)
        default_title = f"Japanese dad tested this on his {MONTH_AGE}-month-old 🍼 #Shorts"

    instagram_script.setdefault("captions", {})
    instagram_script["captions"]["youtube_title"] = result.get("title", default_title)
    description = result.get("description", "")
    instagram_script["captions"]["youtube"] = description + "\n" + get_fixed_footer()
    instagram_script["captions"]["pin_comment"] = result.get("pin_comment", "")

    return instagram_script
