"""
季節・イベントカレンダー
各イベントに衣装・背景・キャプションテーマを定義する。
バズmodeで通常のランダムプールの代わりに使用する。
"""
from datetime import date, timedelta
from typing import Optional

from utils.baby_config import BIRTH_DATE


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """月のn番目のweekday（0=月〜6=日）を返す"""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + (n - 1) * 7)


def _half_birthday(birth: date) -> date:
    """ハーフバースデー（生後6ヶ月の同日）を返す"""
    m = birth.month + 6
    y = birth.year + (m - 1) // 12
    m = (m - 1) % 12 + 1
    try:
        return date(y, m, birth.day)
    except ValueError:
        return date(y, m + 1, 1)  # 月末の場合は翌月1日


SEASONAL_EVENTS = [
    # ──────────────────────────────────────────────
    # お正月
    # ──────────────────────────────────────────────
    {
        "key": "正月",
        "label": "お正月",
        "emoji": "🎍",
        "type": "fixed",
        "month": 1, "day": 1,
        "window_before": 5, "window_after": 5,
        "costumes": [
            "bright red traditional Japanese baby kimono-style onesie with gold obi sash detail and white plum blossom (梅) print, paired with a tiny gold knit pom-pom hat",
            "ivory white haori-style baby romper with deep red and gold shochikubai (松竹梅) embroidery, paired with a small white knit cap",
        ],
        "backgrounds": [
            "soft tatami mat surface with blurred kadomatsu (gate pine decoration) and red and gold New Year shimekkazari, warm Japanese home atmosphere",
            "pale cream washi paper texture with blurred ume blossom branches and golden New Year decorations softly bokeh'd",
        ],
        "accessories": [
            "tiny red and gold traditional Japanese bow accessory (水引飾り)",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "新年・初夢・今年もよろしく・すくすく育ちますように・生後{age}ヶ月での初めてのお正月",
        "caption_keywords": "新年あけましておめでとう・初めてのお正月・今年もせなっちをよろしく・すくすく大きくなあれ",
        "hashtags": "#お正月 #初正月 #babyboo #赤ちゃんのいる生活 #育児",
    },
    # ──────────────────────────────────────────────
    # バレンタイン
    # ──────────────────────────────────────────────
    {
        "key": "バレンタイン",
        "label": "バレンタイン",
        "emoji": "💝",
        "type": "fixed",
        "month": 2, "day": 14,
        "window_before": 7, "window_after": 1,
        "costumes": [
            "deep red heart-print onesie with tiny white hearts scattered all over, paired with a red pom-pom knit beanie",
            "blush pink romper with a large embroidered heart on the chest, paired with a pale pink ribbed knit hat",
        ],
        "backgrounds": [
            "soft pink bokeh background with blurred heart-shaped chocolate boxes, red roses, and pink ribbon bows — sweet Valentine atmosphere",
            "cream background with scattered red and pink heart confetti and chocolate truffles softly blurred behind",
        ],
        "accessories": [
            "heart-shaped strawberry-print bib (red and white)",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "バレンタイン・愛してる・世界一かわいいチョコより甘い・ドキドキ・生後{age}ヶ月のバレンタイン",
        "caption_keywords": "チョコより甘い・ドキドキする・もらってくれる？・バレンタインは世界一かわいいから",
        "hashtags": "#バレンタイン #valentine #babyboo #赤ちゃんのいる生活 #育児",
    },
    # ──────────────────────────────────────────────
    # ひな祭り
    # ──────────────────────────────────────────────
    {
        "key": "ひな祭り",
        "label": "ひな祭り",
        "emoji": "🎎",
        "type": "fixed",
        "month": 3, "day": 3,
        "window_before": 7, "window_after": 1,
        "costumes": [
            "soft peach pink onesie with delicate sakura blossom print and a pink satin sash detail, paired with a pale pink pom-pom beanie",
            "ivory and blush romper with traditional hina doll pattern in soft pink and gold, paired with a cream knit hat",
        ],
        "backgrounds": [
            "soft pink bokeh background with blurred peach blossom (桃の花) branches and delicate hina doll figures in the distance",
            "pale cream surface with scattered pink sakura petals and soft pink fabric, warm spring Hinamatsuri atmosphere",
        ],
        "accessories": [
            "pale pink ruffled cotton bib",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "ひな祭り・桃の節句・春・桜・生後{age}ヶ月で初めてのひな祭り・すくすく育て",
        "caption_keywords": "初めてのひな祭り・桃の節句・春がきたね・すくすく大きくなあれ・可愛すぎて無理",
        "hashtags": "#ひな祭り #桃の節句 #babyboo #赤ちゃんのいる生活 #育児",
    },
    # ──────────────────────────────────────────────
    # こどもの日
    # ──────────────────────────────────────────────
    {
        "key": "こどもの日",
        "label": "こどもの日",
        "emoji": "🎏",
        "type": "fixed",
        "month": 5, "day": 5,
        "window_before": 7, "window_after": 1,
        "costumes": [
            "deep navy koinobori-print onesie with colorful carp streamers pattern, paired with a tiny traditional samurai kabuto (mini helmet) hat in gold and black",
            "grass green romper with bold carp (鯉) and waves print, paired with a green and gold knit beanie",
        ],
        "backgrounds": [
            "bright clear blue sky bokeh with blurred colorful koinobori (carp streamers) flying proudly in the breeze, joyful outdoors atmosphere",
            "soft green background with blurred iris flowers (菖蒲) and traditional children's day decorations in warm spring light",
        ],
        "accessories": [
            "orange carrot-print cotton bib",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "こどもの日・すくすく育て・元気に大きくなあれ・鯉のぼり・生後{age}ヶ月で初めてのこどもの日",
        "caption_keywords": "鯉のぼりより可愛い・元気に大きくなあれ・こどもの日おめでとう・すくすく育ってね",
        "hashtags": "#こどもの日 #子供の日 #babyboo #赤ちゃんのいる生活 #育児",
    },
    # ──────────────────────────────────────────────
    # 母の日（5月第2日曜）
    # ──────────────────────────────────────────────
    {
        "key": "母の日",
        "label": "母の日",
        "emoji": "💐",
        "type": "nth_weekday",
        "month": 5, "weekday": 6, "n": 2,
        "window_before": 5, "window_after": 1,
        "costumes": [
            "soft ivory onesie with delicate pink carnation (カーネーション) flower embroidery scattered all over, paired with a pale pink pom-pom beanie",
            "blush pink romper with a small embroidered 'I love mama' heart, paired with a pink ribbed knit hat",
        ],
        "backgrounds": [
            "soft cream background with blurred pink carnation bouquet and green ribbons, warm loving Mother's Day atmosphere",
            "white linen surface with scattered fresh pink roses and carnation petals softly blurred, warm golden light",
        ],
        "accessories": [
            "pale pink ruffled cotton bib",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "母の日・ママありがとう・世界一のママ・カーネーション・生後{age}ヶ月のせなっちからママへ",
        "caption_keywords": "ママありがとう・世界一のママ大好き・産んでくれてありがとう・いつもありがとう",
        "hashtags": "#母の日 #mothersday #babyboo #赤ちゃんのいる生活 #育児",
    },
    # ──────────────────────────────────────────────
    # 父の日（6月第3日曜）
    # ──────────────────────────────────────────────
    {
        "key": "父の日",
        "label": "父の日",
        "emoji": "👔",
        "type": "nth_weekday",
        "month": 6, "weekday": 6, "n": 3,
        "window_before": 5, "window_after": 1,
        "costumes": [
            "navy blue denim-style onesie with a yellow sunflower (ひまわり) print, paired with a mustard yellow knit pom-pom beanie",
            "forest green onesie with a tiny bear holding a 'I love papa' sign embroidery, paired with a sage green knit hat",
        ],
        "backgrounds": [
            "warm natural wood floor with blurred bright yellow sunflower (ひまわり) bouquet, golden afternoon Father's Day warmth",
            "cream linen surface with blurred sunflower petals and green leaves, warm natural home atmosphere",
        ],
        "accessories": [
            "blue whale-print cotton bib",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "父の日・パパありがとう・育休パパ・ひまわり・生後{age}ヶ月のせなっちからパパへ",
        "caption_keywords": "父の日だけど撮る側・パパも頑張ってます・育休中のパパへ・いつもありがとうパパ",
        "hashtags": "#父の日 #fathersday #babyboo #育休パパ #育児",
    },
    # ──────────────────────────────────────────────
    # 七夕
    # ──────────────────────────────────────────────
    {
        "key": "七夕",
        "label": "七夕",
        "emoji": "🎋",
        "type": "fixed",
        "month": 7, "day": 7,
        "window_before": 7, "window_after": 1,
        "costumes": [
            "deep midnight navy yukata-style baby romper with silver star and bamboo (笹) print, paired with a navy knit headband with tiny star charm",
            "soft powder blue onesie with scattered silver star constellation print, paired with a silver-star pom-pom beanie",
        ],
        "backgrounds": [
            "deep midnight blue background with soft blurred Milky Way (天の川) star bokeh and delicate tanzaku (短冊) paper strips hanging from bamboo, magical tanabata night",
            "soft dark indigo surface with blurred tanabata bamboo and colorful paper wish strips gently swaying, dreamlike evening atmosphere",
        ],
        "accessories": [
            "mint green silicone pacifier with cloud-shaped shield",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "七夕・星に願いを・天の川・すくすく育ちますように・生後{age}ヶ月の七夕の願い事",
        "caption_keywords": "星に願いを・すくすく育ちますように・天の川よりきれい・一番の願い事はこれ",
        "hashtags": "#七夕 #tanabata #babyboo #赤ちゃんのいる生活 #育児",
    },
    # ──────────────────────────────────────────────
    # お盆
    # ──────────────────────────────────────────────
    {
        "key": "お盆",
        "label": "お盆",
        "emoji": "🏮",
        "type": "fixed",
        "month": 8, "day": 15,
        "window_before": 5, "window_after": 2,
        "costumes": [
            "crisp white summer cotton onesie with indigo blue asanoha (麻の葉) traditional Japanese pattern, paired with a white cotton baby cap",
            "soft sky blue yukata-print romper with white morning glory (朝顔) flower print, paired with a light blue knit hat",
        ],
        "backgrounds": [
            "warm amber evening light with blurred paper lanterns (提灯) floating softly, traditional Japanese summer Obon atmosphere",
            "natural wood floor with blurred glowing round chochin lanterns and summer green foliage, peaceful warm evening home",
        ],
        "accessories": [
            "watermelon-print bib (green and red)",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "お盆・夏の思い出・ご先祖様にご報告・生後{age}ヶ月の夏・大きくなったよ",
        "caption_keywords": "ご先祖様に報告です・生後{age}ヶ月になりました・夏も元気です・大きくなったよ",
        "hashtags": "#お盆 #夏 #babyboo #赤ちゃんのいる生活 #育児",
    },
    # ──────────────────────────────────────────────
    # ハロウィン
    # ──────────────────────────────────────────────
    {
        "key": "ハロウィン",
        "label": "ハロウィン",
        "emoji": "🎃",
        "type": "fixed",
        "month": 10, "day": 31,
        "window_before": 7, "window_after": 1,
        "costumes": [
            "bright orange round pumpkin costume with green leaf stem hat — the ultimate jack-o-lantern baby, chubby and perfectly round",
            "black cat onesie with a soft black hood featuring round plush cat ears and tiny white whisker embroidery, mystery mode",
            "fluffy white ghost costume romper with large black oval eyes and little arms, the friendliest ghost ever",
        ],
        "backgrounds": [
            "warm orange-lit background with blurred piles of colorful Halloween candy, mini pumpkins, candy corn, and orange maple leaves — maximum trick or treat energy",
            "deep orange and black bokeh with blurred grinning jack-o-lanterns, glowing ghost decorations, and floating bats, magical Halloween night",
        ],
        "accessories": [
            "orange carrot-print cotton bib",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "ハロウィン・かぼちゃ・仮装・トリックオアトリート・生後{age}ヶ月の初めてのハロウィン・お菓子くれなきゃイタズラするよ",
        "caption_keywords": "トリックオアトリート・かぼちゃより可愛い・お菓子くれなきゃいたずらするよ・初めてのハロウィン",
        "hashtags": "#ハロウィン #halloween #babyboo #赤ちゃんのいる生活 #育児",
    },
    # ──────────────────────────────────────────────
    # 七五三
    # ──────────────────────────────────────────────
    {
        "key": "七五三",
        "label": "七五三",
        "emoji": "⛩️",
        "type": "fixed",
        "month": 11, "day": 15,
        "window_before": 7, "window_after": 2,
        "costumes": [
            "rich deep red traditional Japanese baby kimono onesie with golden crane (鶴) and pine (松) embroidery, paired with a gold pom-pom knit hat",
            "deep navy baby haori-style jacket over a white kimono-print onesie, traditional shichi-go-san ceremonial look",
        ],
        "backgrounds": [
            "warm blurred autumn leaves (紅葉) in red, orange and gold with a soft shrine torii gate silhouette in the distance, sacred Japanese autumn atmosphere",
            "tatami mat surface with blurred chrysanthemum (菊) arrangements and traditional autumn Japanese decorations, ceremonial warmth",
        ],
        "accessories": [
            "bear-face terry cloth bib (brown and cream)",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "七五三・健やかに育ちますように・すくすく大きくなあれ・生後{age}ヶ月の七五三",
        "caption_keywords": "健やかに育ちますように・七五三・すくすく大きくなあれ・神様にご報告",
        "hashtags": "#七五三 #shichigosan #babyboo #赤ちゃんのいる生活 #育児",
    },
    # ──────────────────────────────────────────────
    # クリスマス
    # ──────────────────────────────────────────────
    {
        "key": "クリスマス",
        "label": "クリスマス",
        "emoji": "🎄",
        "type": "fixed",
        "month": 12, "day": 25,
        "window_before": 7, "window_after": 1,
        "costumes": [
            "classic red Santa Claus onesie with white fluffy trim on collar and cuffs, paired with a matching red Santa hat with oversized white pom-pom",
            "forest green elf onesie with red and green striped collar trim and a pointy green and red striped elf hat with a jingle bell",
            "snow-white fluffy reindeer costume with a brown antler hood, soft and round and impossibly cozy",
        ],
        "backgrounds": [
            "warm golden bokeh background with blurred glowing Christmas tree lights, red and gold wrapped presents, and pine garlands — magical cozy Christmas morning",
            "soft white snowy surface with blurred Christmas baubles, twinkling fairy lights, and pine branches with snow, silent magical winter night",
        ],
        "accessories": [
            "strawberry-print bib (red and white)",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "クリスマス・サンタさんきたよ・プレゼント・メリークリスマス・生後{age}ヶ月の初めてのクリスマス・かわいすぎサンタ",
        "caption_keywords": "メリークリスマス・サンタさんきた・世界一かわいいサンタ・プレゼントはせなっちだけで十分",
        "hashtags": "#クリスマス #christmas #babyboo #赤ちゃんのいる生活 #育児",
    },
    # ──────────────────────────────────────────────
    # ハーフバースデー（生後6ヶ月・動的）
    # ──────────────────────────────────────────────
    {
        "key": "ハーフバースデー",
        "label": "ハーフバースデー",
        "emoji": "🎂",
        "type": "half_birthday",
        "window_before": 7, "window_after": 3,
        "costumes": [
            "snow-white onesie with gold '1/2' number embroidery and tiny gold star confetti print all over, paired with a white pom-pom beanie",
            "ivory lace-trim romper with a small embroidered half-birthday cake with one candle, paired with a cream knit hat with gold star",
        ],
        "backgrounds": [
            "cream bokeh background with a blurred half-birthday smash cake with one tall candle, white and gold balloon letters spelling '0.5', and scattered gold confetti",
            "soft white surface with blurred pastel balloons, gold star garland, and a tiny 'happy half birthday' banner, warm celebration glow",
        ],
        "accessories": [
            "rainbow dot print bib (colorful dots on white)",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "ハーフバースデー・生後6ヶ月・生まれてきてくれてありがとう・半年間ありがとう・大きくなったね",
        "caption_keywords": "ハーフバースデー・生後6ヶ月になりました・産んでくれてありがとう・大きくなりすぎて困る",
        "hashtags": "#ハーフバースデー #halfbirthday #babyboo #赤ちゃんのいる生活 #育児",
    },
    # ──────────────────────────────────────────────
    # 誕生日（12/22・動的）
    # ──────────────────────────────────────────────
    {
        "key": "誕生日",
        "label": "誕生日",
        "emoji": "🎉",
        "type": "birthday",
        "window_before": 7, "window_after": 3,
        "costumes": [
            "bright white birthday onesie with colorful confetti and stars print all over, paired with a tiny golden birthday crown hat",
            "festive rainbow stripe romper with matching rainbow chunky knit beanie, ultimate birthday celebration energy",
            "deep royal blue onesie with gold star embroidery and a gold '1' birthday candle detail, paired with a gold crown knit hat",
        ],
        "backgrounds": [
            "colorful birthday party atmosphere with blurred tiered birthday cake with glowing candles, pastel balloons, colorful streamers, and confetti everywhere",
            "soft cream background with blurred pastel birthday balloons in pink, blue, and gold and party confetti bokeh, warm celebration warmth",
        ],
        "accessories": [
            "rainbow dot print bib (colorful dots on white)",
            "no accessory — just the costume and natural expression",
        ],
        "caption_theme": "誕生日おめでとう・1歳・生まれてきてくれてありがとう・ハッピーバースデー・せなっち1歳おめでとう",
        "caption_keywords": "ハッピーバースデー・1歳おめでとう・産まれてきてくれてありがとう・あっという間の1年・大きくなりすぎ",
        "hashtags": "#誕生日 #birthday #babyboo #赤ちゃんのいる生活 #育児",
    },
]


def _get_event_date(event: dict, year: int) -> Optional[date]:
    """イベントの今年の日付を返す"""
    t = event["type"]
    if t == "fixed":
        return date(year, event["month"], event["day"])
    elif t == "nth_weekday":
        return _nth_weekday(year, event["month"], event["weekday"], event["n"])
    elif t == "half_birthday":
        hb = _half_birthday(BIRTH_DATE)
        return hb if hb.year == year else None
    elif t == "birthday":
        return date(year, BIRTH_DATE.month, BIRTH_DATE.day)
    return None


def get_upcoming_events(days_ahead: int = 7, today: date = None) -> list:
    """今日から days_ahead 日以内に始まるイベントを返す（重複なし・近い順）"""
    today = today or date.today()
    result = []
    seen = set()
    for year in [today.year, today.year + 1]:
        for ev in SEASONAL_EVENTS:
            if ev["key"] in seen:
                continue
            ev_date = _get_event_date(ev, year)
            if ev_date is None:
                continue
            start = ev_date - timedelta(days=ev.get("window_before", 7))
            end   = ev_date + timedelta(days=ev.get("window_after", 1))
            if start <= today <= end:
                ev_copy = dict(ev)
                ev_copy["event_date"] = ev_date
                ev_copy["days_until"] = (ev_date - today).days
                result.append(ev_copy)
                seen.add(ev["key"])
    result.sort(key=lambda x: abs(x["days_until"]))
    return result


def get_active_event(today: date = None) -> Optional[dict]:
    """最も優先度の高い現在進行中のイベントを1つ返す（なければNone）"""
    events = get_upcoming_events(days_ahead=7, today=today)
    return events[0] if events else None
