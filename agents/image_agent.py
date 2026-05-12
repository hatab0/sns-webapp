"""
画像プロンプト生成エージェント
ChatGPT GPT Image 2用の画像プロンプトと Kling AI動画プロンプトをClaude APIで生成する
"""
import anthropic
import os
import random
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

BIRTH_DATE = date(2025, 12, 22)

# 毎回ランダムで変わるかわいいアクセサリープール
CUTE_ACCESSORIES = [
    "白いリボンカチューシャ（細いサテンリボン）",
    "ピンクのフリルカチューシャ",
    "くまの耳カチューシャ（ベージュ・もこもこ素材）",
    "うさぎの耳カチューシャ（白・ふわふわ素材）",
    "白いポンポン付きニット帽（ベビーサイズ）",
    "淡いピンクのベレー帽",
    "白いフリル付きスタイ（前掛け）",
    "イチゴ柄のかわいいスタイ",
    "小花のヘアクリップ（白・ピンク）",
    "水色のドット柄スタイとお揃いカチューシャセット",
    "黄色のひよこコスチューム帽子",
    "クリームいろのアニマルニット帽（耳付き）",
]


def calc_month_age() -> int:
    today = date.today()
    months = (today.year - BIRTH_DATE.year) * 12 + (today.month - BIRTH_DATE.month)
    if today.day < BIRTH_DATE.day:
        months -= 1
    return max(0, months)


MONTH_AGE = calc_month_age()

# 月齢グループ別Kling AI動画プロンプト設計
MOTION_BY_AGE_GROUP = {
    "0-2": {
        "sounds": ["おぎゃー", "あー", "うー"],
        "motion_en": (
            "stares gently at camera with wide innocent eyes, tiny fingers occasionally twitch, "
            "peaceful newborn breathing rhythm, slow subtle head tilt, serene newborn moment"
        ),
        "mood_en": "serene, calm, precious newborn",
    },
    "3": {
        "sounds": ["あははっ", "きゃっ", "うふー"],
        "motion_en": (
            "suddenly breaks into a big gummy smile directly at camera, arms flap excitedly, "
            "legs kick with joy, whole body expresses happiness"
        ),
        "mood_en": "joyful, heartwarming, first real laughs",
    },
    "4-5": {
        "sounds": ["あーっ！", "えへへ", "きゃっ"],
        "motion_en": (
            "looks directly at camera then suddenly flashes a huge delighted smile, "
            "slow gentle zoom in, natural seamless loop"
        ),
        "mood_en": "warm, natural, irresistibly cute",
    },
    "6-7": {
        "sounds": ["まーまー", "ぱーぱー", "んまー"],
        "motion_en": (
            "babbles 'mama' or 'papa' sounds with mouth movements, hands open and close "
            "in grabbing motion, leans forward curiously toward camera"
        ),
        "mood_en": "curious, developing personality, engaging babbling",
    },
    "8-9": {
        "sounds": ["まんまー！", "ぱっぱー", "やー！"],
        "motion_en": (
            "points finger at camera with big expressive eyes, leans forward excitedly, "
            "waves hands enthusiastically, clear intentional gestures"
        ),
        "mood_en": "expressive, interactive, dynamic personality",
    },
    "10-12": {
        "sounds": ["ママ！", "パパ！", "まんま！"],
        "motion_en": (
            "clearly mouths 'mama' or 'papa', reaches both arms toward camera with a big smile, "
            "milestone moment of first real words"
        ),
        "mood_en": "milestone, emotional, first words moment",
    },
    "13+": {
        "sounds": ["だっこ！", "もっと！", "いやいや！"],
        "motion_en": (
            "shakes head 'no' expressively or reaches out with demanding gesture, "
            "strong emerging personality, deliberate funny toddler movements"
        ),
        "mood_en": "opinionated, funny, relatable toddler",
    },
}

# バズmode：月齢別ダンス動作（Kling AI用）
BUZZ_MOTION_BY_AGE_GROUP = {
    "0-6": (
        "body sways gently from side to side, head bobs adorably, "
        "tiny arms wave in rhythm, pure joy and movement"
    ),
    "7-12": (
        "whole body bounces up and down to the beat, claps hands together, "
        "big excited smile, full body rhythm"
    ),
    "13+": (
        "spins in place laughing, wiggles hips to the music, "
        "falls down and pops back up still dancing, irresistibly funny"
    ),
}

# バズmode：月齢別シーン設定（baby_cubo_official スタイル）
# 各月齢グループ5種類 → random.choice() でランダム選択
BUZZ_SCENE_BY_AGE = {
    "0-2": [
        {
            "pose": "peacefully sleeping, swaddled snugly in soft muslin cloth, arms tucked in, tiny lips parted",
            "expression": "serene angelic sleeping face, completely relaxed, impossibly tiny and precious",
            "camera": "extreme close-up, face fills 85% of frame, slight overhead angle, very shallow DOF",
            "lighting": "ultra-soft diffused window light, gentle warm glow, no shadows, skin luminous",
            "background": "blurred soft white or cream muslin fabric, completely clean and minimal",
        },
        {
            "pose": "lying on back mid full-body stretch, both tiny arms raised, back gently arched, legs extended",
            "expression": "wide perfect yawn — mouth forms a tiny O, eyes squeezed shut, entire face adorably scrunched",
            "camera": "overhead angle directly above, baby centered, capturing full stretch head to toe",
            "lighting": "bright soft morning window light, clean and airy, warm tones",
            "background": "clean white fleece blanket surface, smooth and seamless",
        },
        {
            "pose": "lying on back, both tiny fists raised near cheeks, head tilted slightly to one side",
            "expression": "classic newborn old-man frown — furrowed wrinkled brow, pursed lips, deep serious concentration",
            "camera": "tight close-up on face and fists, straight-on, face fills 80% of frame",
            "lighting": "soft diffused studio light, even and clean, gentle skin luminosity",
            "background": "soft pale pink bokeh background, completely clean",
        },
        {
            "pose": "lying on side in gentle fetal curl, cheek squished softly upward against fluffy surface, one fist near chin",
            "expression": "peacefully sleeping, cheek pushed up into adorable squishy fold, lips slightly parted",
            "camera": "eye-level side angle to capture the squished cheek perfectly, very shallow DOF",
            "lighting": "warm soft rim lighting from behind, gentle glow on hair and cheek edge",
            "background": "ultra-soft blurred white sherpa texture, cozy and warm",
        },
        {
            "pose": "lying on back, completely still, staring directly and intensely at the camera with wide open eyes",
            "expression": "maximum alert newborn stare — huge dark eyes wide open, utterly focused, ancient soul expression",
            "camera": "extreme tight close-up, eyes as absolute focal point, fills 90% of frame",
            "lighting": "soft dramatic single window light catching bright catchlights in wide dark eyes",
            "background": "blurred deep navy or charcoal background for dramatic contrast",
        },
    ],
    "3": [
        {
            "pose": "lying on back, legs kicking high in the air, arms reaching up, caught at peak of first big laugh",
            "expression": "very first social smile blooming — round chubby cheeks, eyes crinkled to slits, pure joy",
            "camera": "close-up face and chest, slight low angle looking up at baby, 85mm portrait style",
            "lighting": "soft warm studio light, bright catchlights making eyes sparkle",
            "background": "soft pastel mint green bokeh, clean and fresh",
        },
        {
            "pose": "tummy time, barely managing to lift head, chin quivering with effort, arms tucked underneath",
            "expression": "intense tiny determination face — brow furrowed, eyes wide, trying with all available willpower",
            "camera": "very low angle, exactly eye level on tummy, face fills majority of frame",
            "lighting": "warm soft side window light, showing effort in face and texture",
            "background": "soft textured play mat, warm muted colors blurred",
        },
        {
            "pose": "lying on back, mid-movement frozen completely still, staring at camera in total shock",
            "expression": "maximum surprise face — mouth wide open O-shape, eyebrows raised to hairline, eyes enormous",
            "camera": "overhead angle straight down, face fills center of frame completely",
            "lighting": "bright even overhead light, clean white and airy",
            "background": "clean pastel yellow blanket, warm and cheerful",
        },
        {
            "pose": "sitting in tiny baby bathtub, water droplets on chubby arms, one hand caught mid-splash",
            "expression": "water shock delight — eyes wide, mouth in surprised O, water droplets sparkling on chubby cheeks",
            "camera": "medium close-up, slight overhead angle, water surface catching light",
            "lighting": "bright bathroom window light, water droplets sparkling",
            "background": "soft white bath towel edge visible, tiles softly blurred behind",
        },
        {
            "pose": "held upright facing camera at chest height, tiny feet dangling, both fists clenched at sides",
            "expression": "supremely serious judgement face — staring directly into camera with ancient wisdom eyes, unimpressed",
            "camera": "medium shot from slightly below, baby gazing down at camera with gravity",
            "lighting": "soft diffused studio light, clean and professional",
            "background": "blurred soft gray or white background, minimal and elegant",
        },
    ],
    "4-5": [
        {
            "pose": "tummy time, head lifted high and proud, chest fully off mat, arms extended, showing off neck strength",
            "expression": "enormous open-mouth laugh, chubby cheeks puffed, eyes wide with joy — genuinely candid moment",
            "camera": "low angle front-on, eye level with baby's face, face as sharp focal point",
            "lighting": "soft warm studio light, prominent catchlights in laughing eyes",
            "background": "creamy white bokeh, clean and simple",
        },
        {
            "pose": "lying on back with both arms raised triumphantly, legs kicking simultaneously in pure excitement",
            "expression": "absolute peak excitement — eyes crinkled shut in huge grin, cheeks at maximum chubbiness",
            "camera": "overhead angle, baby fills 85% of frame, looking up at camera",
            "lighting": "bright soft overhead studio light, clean white fill, celebratory",
            "background": "bright white background, clean and crisp",
        },
        {
            "pose": "caught perfectly mid-roll from back to tummy — body halfway tilted, one arm trapped underneath",
            "expression": "completely confused where-am-I face — one eye visible, mouth open O, pure adorable bewilderment",
            "camera": "straight-on medium close-up capturing the mid-roll suspended moment",
            "lighting": "bright clean studio light",
            "background": "colorful play mat, primary colors softly blurred",
        },
        {
            "pose": "lying on back, both hands successfully grabbing both feet simultaneously, legs lifted high, very proud",
            "expression": "enormously self-satisfied giggling face — eyes squeezed shut laughing, incredibly proud of foot discovery",
            "camera": "slight overhead angle to see both hands gripping feet together",
            "lighting": "warm soft window light, natural feel",
            "background": "soft pastel blue or lavender blanket, dreamy and clean",
        },
        {
            "pose": "lying on side, cheek pressed flat against soft surface creating maximum squish, eyes looking up at camera",
            "expression": "helpless squished-cheek cuteness — one eye bigger from squish, small surprised mouth, maximum chub",
            "camera": "extreme tight close-up filling entire frame, squished cheek as main focus",
            "lighting": "ultra-soft window light, flattering on squishy cheek",
            "background": "blurred pink or peach soft fabric, warm and cozy",
        },
    ],
    "6-7": [
        {
            "pose": "sitting with slight support, leaning noticeably forward, one hand fully extended reaching toward camera",
            "expression": "wide-eyed wonder and curiosity — eyebrows raised high, mouth slightly open in pure amazement",
            "camera": "medium shot head to waist, slight low angle to make baby look grand",
            "lighting": "bright soft light, warm tones, clear sparkling catchlights",
            "background": "soft sofa corner or textured knit blanket lifestyle setting, warm blurred",
        },
        {
            "pose": "sitting in high chair, first food just tasted, spoon pulled away, face covered in orange puree",
            "expression": "impossible-to-read first food verdict — one eye squinted, brow twisted, mouth puckered, jury still out",
            "camera": "close-up on food-covered face, straight level angle capturing full reaction",
            "lighting": "bright natural kitchen window light, warm and lively",
            "background": "high chair tray edge visible, blurred warm kitchen behind",
        },
        {
            "pose": "being held standing on adult lap, both knees bending deep and bouncing with unstoppable joy and rhythm",
            "expression": "unstoppable bouncing delight — mouth wide open mid-laugh, eyes crinkled, whole body involved",
            "camera": "medium front shot, slight motion blur on bouncing legs showing energy",
            "lighting": "warm cozy living room light, golden afternoon feel",
            "background": "blurred soft living room setting, warm and homey",
        },
        {
            "pose": "hands just pulled away from face in peekaboo reveal, eyes huge, whole body leaning forward in shock",
            "expression": "peekaboo explosion of laughter — mouth open in full guffaw, eyes crinkled, delighted total shock",
            "camera": "close-up capturing the revealed expression, hands visible at frame edges",
            "lighting": "bright warm studio light, sparkling catchlights in surprised eyes",
            "background": "clean soft pink or lavender bokeh background",
        },
        {
            "pose": "sitting propped, facing mostly forward but eyes cutting sharply sideways — full baby side-eye",
            "expression": "legendary baby side-eye — one eyebrow marginally higher, mouth neutral, pure unbothered judgment",
            "camera": "straight-on medium close-up, capturing the sideways eye direction perfectly",
            "lighting": "slightly dramatic single side lighting emphasizing the expression",
            "background": "clean deep blue or gray backdrop for comedic contrast",
        },
    ],
    "8-9": [
        {
            "pose": "sitting very independently, one finger pointing directly and authoritatively at camera",
            "expression": "animated personality fully present — intense eye contact, slight smirk, owner of the room energy",
            "camera": "medium close-up, very slight dynamic angle, face as undeniable main subject",
            "lighting": "vibrant warm light, sharp bright catchlights in eyes",
            "background": "bold solid color backdrop, deep red or royal blue for personality",
        },
        {
            "pose": "mid-crawl with one hand raised off the ground, looking up at camera like a tiny conqueror",
            "expression": "pure crawling triumph — enormous open grin, eyes bright and proud, total conquest expression",
            "camera": "very low angle, slightly in front of baby, capturing crawl and face simultaneously",
            "lighting": "bright natural floor-level light, warm tones",
            "background": "soft play mat colors blurred, clean room behind",
        },
        {
            "pose": "sitting, holding a small colorful object in both hands, bringing it extremely close to face to study",
            "expression": "full scientist investigation mode — brow furrowed intensely, eyes crossing slightly at close object",
            "camera": "medium close-up from front, baby's face and the object both in frame",
            "lighting": "bright window light, natural and clear",
            "background": "warm blurred home interior, cozy feeling",
        },
        {
            "pose": "sitting upright, both hands coming together in a big enthusiastic clap, arms spread wide",
            "expression": "self-congratulatory clapping joy — huge beam, eyes dancing, so proud of own clapping ability",
            "camera": "medium shot slightly wide to capture the hand-clap motion, slight hand blur",
            "lighting": "bright warm studio light, clean celebration feel",
            "background": "bright pastel yellow or orange single-color, cheerful",
        },
        {
            "pose": "sitting perfectly still, looking straight at camera, eyes cutting hard to one side — supreme side-eye",
            "expression": "ultimate skeptical side-eye — one brow raised, lips pressed together, deep unimpressed judgment",
            "camera": "extreme tight close-up filling 90% of frame, totally straight-on",
            "lighting": "slightly moody single side light to emphasize the iconic skeptical expression",
            "background": "dark moody charcoal or black bokeh for maximum comedic contrast",
        },
    ],
    "10-12": [
        {
            "pose": "pulling to stand holding furniture edge, legs straight, chest puffed with enormous first-time pride",
            "expression": "milestone achievement beam — huge open smile, bright eyes, pride radiating from entire face",
            "camera": "full body shot to show the standing achievement, slight low angle to celebrate it",
            "lighting": "bright celebratory studio light, clean and crisp",
            "background": "clean minimal light backdrop, all focus on achievement",
        },
        {
            "pose": "sitting and clapping both hands high overhead enthusiastically, whole body bouncing with the rhythm",
            "expression": "maximum celebration energy — eyes squeezed shut laughing, mouth fully open, pure joy abandon",
            "camera": "medium shot to capture the overhead clap and full-body bounce together",
            "lighting": "bright cheerful studio light, high energy feeling",
            "background": "bright pastel single-color, festive pink or sky blue",
        },
        {
            "pose": "standing completely free with nothing to hold, arms spread wide for balance, frozen mid-wobble",
            "expression": "terror-joy hybrid face — eyes enormous, mouth open, somewhere between falling and flying",
            "camera": "full body shot, slight low angle to emphasize the gravity-defying moment",
            "lighting": "clean bright light, every detail sharp",
            "background": "clean minimal home interior or white backdrop",
        },
        {
            "pose": "sitting or pulling to stand, waving one arm in full enthusiastic arc — big exaggerated bye-bye",
            "expression": "social milestone pride — giant grin while waving, so proud of knowing bye-bye skill",
            "camera": "medium shot capturing face and enthusiastic waving arm together",
            "lighting": "warm bright natural light, homey feeling",
            "background": "warm lifestyle home setting, blurred interior",
        },
        {
            "pose": "both hands covering face in peekaboo, but one eye peeking through gap in fingers, building anticipation",
            "expression": "barely-contained excitement — one eye wide peeking through fingers, huge suppressed grin visible",
            "camera": "close-up, eye peeking through finger gap as absolute focal point, very shallow DOF",
            "lighting": "warm playful light, bright catchlight in the single peeking eye",
            "background": "soft blurred pastel colors, warm and playful",
        },
    ],
    "13+": [
        {
            "pose": "toddling with both arms stretched fully out wide for balance, one foot mid-step, utterly determined",
            "expression": "intense walking concentration face — tongue slightly out, eyes focused forward, absolute determination",
            "camera": "full body shot, slight low angle, capturing the whole toddling journey",
            "lighting": "bright energetic room light, lively and warm",
            "background": "colorful indoor play setting, toys visible and blurred",
        },
        {
            "pose": "caught doing something forbidden — hand outstretched toward off-limits thing, freeze-frame guilty moment",
            "expression": "maximum caught-in-the-act face — eyes wide, mouth O-shaped, complete freeze-frame guilt and shock",
            "camera": "medium shot showing both the forbidden reach and the guilty expression simultaneously",
            "lighting": "bright natural home light, nothing hidden, fully exposed",
            "background": "home setting, recognizable domestic environment, warm tones",
        },
        {
            "pose": "mid-spin, just beginning to lose balance and topple sideways, one arm flailing for balance",
            "expression": "spinning delirium laughter — mouth fully open, eyes unfocused and dizzy, about to magnificently fall",
            "camera": "medium full-body shot capturing the spin and the impending joyful fall",
            "lighting": "bright energetic light, sense of movement and chaos",
            "background": "blurred colorful living room, motion and life blurred behind",
        },
        {
            "pose": "seen from behind and slight side, chubby legs running at full toddler sprint, head turned looking back grinning",
            "expression": "gleeful escape look over shoulder — huge grin, complete joy at being chased, wind-in-hair energy",
            "camera": "medium shot from behind-side angle, face visible in the turned-back look",
            "lighting": "bright indoor or soft outdoor light, energetic and lively",
            "background": "hallway or garden path, motion blur on pumping legs",
        },
        {
            "pose": "perfect full toddler squat on chubby legs, face inches from the floor examining something tiny on the ground",
            "expression": "total scientific absorption — face extremely close to ground, eyebrows furrowed, world completely forgotten",
            "camera": "side-on angle showing the full adorable toddler squat, camera at floor level",
            "lighting": "natural floor-level warm light, soft and intimate",
            "background": "blurred floor surface and room behind, minimal and quiet",
        },
    ],
}

# バズmode：コスチュームプール（baby_cubo_official スタイル）
BUZZ_COSTUME_POOL = [
    # ━━ baby_cubo_official シグネチャー：シンプルオールインワン＋ニットビーニー ━━
    # (最もバズる組み合わせ - 毎投稿に近い頻度で使用)
    "solid soft pink onesie with a tiny white chunky-knit beanie hat",
    "solid lavender purple onesie with a colorful multicolor striped knit beanie",
    "bright white onesie with a mint green cable-knit pom-pom hat",
    "pale lemon yellow onesie with an orange knit pom-pom beanie",
    "coral orange snap-button romper with a cream white knit beanie",
    "soft sage green onesie with a blush pink ribbed knit hat",
    "sky blue onesie with a navy and white striped knit beanie",
    "clean white onesie with a rainbow striped chunky knit hat",
    "dusty rose onesie with a matching rose-pink oversized pom-pom hat",
    "tomato red onesie with a white ribbed knit hat",
    "solid mint green onesie with a mustard yellow knit beanie",
    "heather gray onesie with a multicolor pompom chunky knit beanie",
    # ━━ ニットセーター・カーディガン style ━━
    "soft pastel striped knit sweater (pink-yellow-white horizontal stripes) over white onesie underneath",
    "tiny cream cable-knit cardigan over a pastel blue onesie, open front",
    "oversized cozy sage green knit pullover sweater, chunky texture",
    "bold red and white fair-isle patterned knit sweater",
    "soft lilac ribbed knit long-sleeve onesie with a matching ribbed beanie",
    # ━━ つば広ハット・バケットハット style ━━
    "wide-brim soft pink cotton bucket hat with a plain white short-sleeve onesie",
    "natural straw sun hat with a simple floral print cotton romper",
    "floppy oversized cream bucket hat with a sage green onesie",
    # ━━ アニマルフーディー・テーマ衣装 ━━
    "bright green dinosaur hoodie onesie with tiny spikes along the hood",
    "brown teddy bear hoodie onesie with round plush ears",
    "black and white panda hoodie onesie with panda ear hood",
    "soft yellow duckling costume with orange beak hood",
    "white fluffy bunny onesie with long floppy ear hood",
    "mint green frog costume with round bug-eye hood",
    # ━━ 果物・季節・カジュアル ━━
    "bright red strawberry costume with green leaf hat",
    "orange pumpkin round costume with green stem hat",
    "tiny navy blue denim jacket over a white onesie (mini casual style)",
    "cream sherpa bear-ear hooded zip-up suit",
    "red and white horizontal striped long-sleeve with tiny denim shorts",
    "rainbow striped chunky knit sweater with matching booties",
]


def _get_age_group(month_age: int) -> str:
    if month_age <= 2:
        return "0-2"
    elif month_age == 3:
        return "3"
    elif month_age <= 5:
        return "4-5"
    elif month_age <= 7:
        return "6-7"
    elif month_age <= 9:
        return "8-9"
    elif month_age <= 12:
        return "10-12"
    else:
        return "13+"


def _get_buzz_age_group(month_age: int) -> str:
    if month_age <= 6:
        return "0-6"
    elif month_age <= 12:
        return "7-12"
    else:
        return "13+"


def _base_image_prompt_text(product: dict, accessory: str = "") -> str:
    """商品あり：画像プロンプトの共通部分（2枚参照画像前提）"""
    acc = accessory or random.choice(CUTE_ACCESSORIES)
    return f"""
ChatGPT GPT Image 2で使用する、高品質な画像生成プロンプトを英語で作成してください。

【前提：ユーザーから2枚の参照画像が送信されます】
  参照画像1: 赤ちゃん「せなっち」の写真 → 外見の完全一致に使用
  参照画像2: 商品「{product['name'][:50]}」の商品写真 → 商品外観の完全一致に使用

【タスク】
参照画像1のせなっちが、参照画像2の商品を実際に着用・使用しているリアルな写真を生成する。
赤ちゃんの顔・髪・体つきは参照画像1と完全一致させること。
商品のデザイン・色・形は参照画像2と完全一致させること。

【GPT Image 2向け：撮影スタイル】
・スタイル：Photorealistic studio photography, professional baby product lifestyle photo
・カメラ：Shot with 85mm portrait lens, shallow depth of field, soft bokeh background
・照明：Soft diffused studio lighting, warm 3200K color temperature, gentle fill light from left
・構図：Close-up to medium shot, subject centered, 1:1 square format

【せなっちのキャラクター補足（参照画像1に加えて守る）】
・生後{MONTH_AGE}ヶ月の日本人男の子
・アクセサリー：{acc}
・表情：穏やかな笑顔 or 商品に興味を示している顔

【背景・雰囲気】
・背景：クリーム色・アイボリー・ベージュのナチュラルスタジオ
・小物：白いふわふわのブランケット・薄いモスリンガーゼ
・全体的にナチュラル・オーガニック・清潔感のある世界観
"""


def _base_scene_text_buzz() -> str:
    """バズmode：baby_cubo_officialスタイルの月齢特化シーン（参照画像1枚のみ）"""
    age_group = _get_age_group(MONTH_AGE)
    scenes = BUZZ_SCENE_BY_AGE.get(age_group, BUZZ_SCENE_BY_AGE["4-5"])
    scene = random.choice(scenes)
    costume = random.choice(BUZZ_COSTUME_POOL)

    return f"""
Create a high-quality image generation prompt for ChatGPT GPT Image 2.

TARGET STYLE: Replicate the exact aesthetic of the viral Instagram account "baby_cubo_official" —
hyper-realistic, professional infant photography that goes instantly viral because it is
irresistibly cute, emotionally engaging, and technically flawless.

━━ REFERENCE IMAGE (1 photo provided by user) ━━
One reference photo of baby "Senacchi" will be provided.
→ Reproduce face, eyes, nose, facial contours, skin tone, and hair EXACTLY from reference.
→ Costume and background are 100% generated from text instructions below (no second image needed).

━━ BABY CHARACTER (strictly follow) ━━
• Japanese baby boy, {MONTH_AGE} months old
• Chubby rounded cheeks, jet-black hair, large round dark brown eyes
• Male baby boy only — must not look feminine

━━ baby_cubo_official SIGNATURE VISUAL RULES (critical) ━━
① EYES ARE EVERYTHING: Massive, round, dark brown eyes must be razor-sharp and glistening.
   Bright white catchlights (specular highlights) MUST be visible in both eyes — this is non-negotiable.
② FACE FILLS THE FRAME: Baby's face occupies 70–90% of the frame. This is the signature crop.
③ CHUBBY CHEEKS: Emphasize the softness and roundness of chubby baby cheeks — they are a key feature.
④ SKIN PERFECTION: Smooth, luminous, soft baby skin. Never plastic, never waxy, never AI-looking.
⑤ CLEAN SIMPLE BACKGROUND: Solid single-color bokeh only. No busy patterns, no cluttered scenes.
⑥ EXPRESSION IS VIRAL: The expression must trigger an emotional reaction — adorable, funny, shocking, or heartwarming.

━━ COSTUME (fully generate from text) ━━
{costume}
→ Reproduce this costume accurately. Scale appropriately for a {MONTH_AGE}-month-old baby size.

━━ POSE & EXPRESSION for {MONTH_AGE}-month-old ━━
Pose: {scene['pose']}
Expression: {scene['expression']}
→ Capture a genuine candid split-second moment — not posed, not stiff. Real and alive.

━━ CAMERA & FRAMING ━━
{scene['camera']}
Format: 1:1 square / 85mm portrait lens equivalent / f/1.8 very shallow depth of field

━━ LIGHTING ━━
{scene['lighting']}
MANDATORY: Clear bright catchlights (white sparkle points) in both eyes.

━━ BACKGROUND ━━
{scene['background']}
Background fully blurred into clean simple bokeh — baby is the only subject that matters.

━━ TECHNICAL QUALITY (non-negotiable) ━━
• Style: Hyper-realistic professional infant photography, editorial/magazine quality
• Skin: Smooth, soft, naturally glowing — not plastic, not AI-generated looking
• Eyes: Tack-sharp, large, alive, wet-looking with bright catchlights
• Color grade: Warm, soft, slightly golden — like natural window light
• No text, no watermarks, no logos, no overlays, no feminine hair accessories
• Final result should look like a photo that would get 100K+ likes on Instagram
"""


def generate_image_prompt(product: dict, accessory: str = "") -> str:
    """
    【楽天ROOM用】文字あり画像プロンプト（英語）
    手書き風テキスト3フレーズを画面に追加。
    保存ファイル名: YYYYMMDD.png
    """
    product_short = product['name'][:20]
    prompt = _base_image_prompt_text(product, accessory) + f"""
【手書き風テキスト 3フレーズ（必須）】
商品「{product_short}」に合わせて、白い細い手書き風ペンで以下の3つを画面の端・隅に配置する：
  1. 商品への感動コメント（「{product_short}最高すぎた！」のようなスタイル / 8〜12文字の日本語）
  2. ブランド名または商品の種類名（4〜8文字 / やや小さめのサイズ）
  3. 必要性を訴えるフレーズ（「これないと困る」「神育児グッズ」「買って大正解」など / 7〜10文字）

各テキストは角度・サイズを少しずつ変えてナチュラルな手書き感を出す。
No watermarks, no logos, no brand logos.

【出力仕様（プロンプト末尾に必ず明記）】
Output format: PNG / Size: 1024×1024 (square, 1:1) / File size: under 2097152 bytes (2MB)

英語のプロンプトのみ出力してください。前置き不要。
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def generate_image_prompt_notxt(product: dict, accessory: str = "") -> str:
    """
    【動画用・通常mode】文字なし画像プロンプト（英語）
    Kling AIに読み込む素材画像として使用。
    保存ファイル名: YYYYMMDD_video.png
    """
    prompt = _base_image_prompt_text(product, accessory) + """
【テキスト（Kling AI動画用・文字なし版）】
・テキスト・文字・手書き文字は一切入れない
・No text, no handwriting, no captions, no watermarks, no logos, no overlays of any kind
・純粋な写真のみ

【出力仕様（プロンプト末尾に必ず明記）】
Output format: PNG / Size: 1024×1024 (square, 1:1) / File size: under 2097152 bytes (2MB)

英語のプロンプトのみ出力してください。前置き不要。
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def generate_image_prompt_notxt_buzz() -> str:
    """
    【動画用・バズmode】文字なし画像プロンプト（英語）
    せなっちが踊っている・ふざけているシーン。
    保存ファイル名: YYYYMMDD_buzz.png
    """
    prompt = _base_scene_text_buzz() + """
【テキスト（Kling AI動画用・文字なし版）】
・テキスト・文字・手書き文字は一切入れない
・No text, no handwriting, no captions, no watermarks, no logos, no overlays of any kind
・純粋な写真のみ

【出力仕様（プロンプト末尾に必ず明記）】
Output format: PNG / Size: 1024×1024 (square, 1:1) / File size: under 2097152 bytes (2MB)

英語のプロンプトのみ出力してください。前置き不要。
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def generate_kling_prompt(product: dict) -> str:
    """
    【通常mode】Kling AI（Image to Video）用動画プロンプト（英語）
    月齢に合った動きで10秒バイラル動画を生成。Positive / Negative Prompt形式で出力。
    """
    age_group = _get_age_group(MONTH_AGE)
    age_info = MOTION_BY_AGE_GROUP.get(age_group, MOTION_BY_AGE_GROUP["4-5"])
    primary_sound = age_info["sounds"][0]
    motion_en = age_info["motion_en"]
    mood_en = age_info["mood_en"]

    prompt = f"""
せなっち（生後{MONTH_AGE}ヶ月）が商品「{product['name'][:40]}」を着ている・使っている静止画を
Kling AI（Image to Video）でInstagramリール バイラル動画にするプロンプトを英語で作成してください。

【バイラルコンセプト】
・せなっちが商品を着ている・使っている状態で月齢に合った自然な動きをする
・主な動き：{motion_en}
・月齢({MONTH_AGE}ヶ月)の声のイメージ："{primary_sound}"
・「かわいすぎ」「これ何使ってるの？」と思わずコメントしたくなる構成
・動画が自然にループする構成（最後のフレームが最初につながる）
・動画尺：10秒（Kling AIの設定で10sを選択）

【Kling AIプロンプトのルール】
・外見の詳細描写は不要（入力画像から取得するため）
・Positive Promptは動き・カメラ・雰囲気を中心に60〜100語で記述
・Negative Promptは「NG要素」を15〜25語で列挙
・箇条書き不要・それぞれ1段落で出力

【カメラワーク・雰囲気】
・カメラ：slow gentle zoom in, then slowly pull back（10秒自然ループ用）
・全体的な雰囲気：{mood_en}, warm, cozy, natural, cinematic

【出力形式】以下の形式のみ。前置き不要。
Positive Prompt:
（英語プロンプト）

Negative Prompt:
（英語NG要素）
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    result = message.content[0].text.strip()
    if result.startswith("```"):
        result = "\n".join(result.split("\n")[1:])
    if result.endswith("```"):
        result = "\n".join(result.split("\n")[:-1])
    return result.strip()


def generate_kling_prompt_buzz() -> str:
    """
    【バズmode】Kling AI（Image to Video）用ダンス動画プロンプト（英語）
    せなっちが踊っている・ふざけているコミカルな動画。Positive / Negative Prompt形式。
    """
    buzz_age_group = _get_buzz_age_group(MONTH_AGE)
    motion_en = BUZZ_MOTION_BY_AGE_GROUP.get(buzz_age_group, BUZZ_MOTION_BY_AGE_GROUP["0-6"])
    age_group = _get_age_group(MONTH_AGE)
    age_info = MOTION_BY_AGE_GROUP.get(age_group, MOTION_BY_AGE_GROUP["4-5"])
    primary_sound = age_info["sounds"][0]

    prompt = f"""
せなっち（生後{MONTH_AGE}ヶ月）のコスチューム姿の静止画を
Kling AI（Image to Video）でバイラル ダンス動画にするプロンプトを英語で作成してください。

【バズコンセプト：思わずシェアしたくなるコミカルな動き】
・主な動き：{motion_en}
・月齢({MONTH_AGE}ヶ月)の声のイメージ："{primary_sound}"
・「かわいすぎて笑える」「友達に送りたい」という感情を引き出す
・リズミカルで楽しい動き・明るいテンポ
・動画尺：10秒（Kling AIの設定で10sを選択）

【Kling AIプロンプトのルール】
・外見の詳細描写は不要（入力画像から取得するため）
・Positive Promptは動き・カメラ・雰囲気を中心に60〜100語で記述
・Negative Promptは「NG要素」を15〜25語で列挙
・箇条書き不要・それぞれ1段落で出力

【カメラワーク・雰囲気】
・カメラ：dynamic, slightly bouncy camera movement synced to the rhythm
・全体的な雰囲気：fun, playful, comedic, bright, energetic, viral

【出力形式】以下の形式のみ。前置き不要。
Positive Prompt:
（英語プロンプト）

Negative Prompt:
（英語NG要素）
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    result = message.content[0].text.strip()
    if result.startswith("```"):
        result = "\n".join(result.split("\n")[1:])
    if result.endswith("```"):
        result = "\n".join(result.split("\n")[:-1])
    return result.strip()


def run(products: list) -> list:
    """通常mode：商品ありの画像・動画プロンプトを生成して返す"""
    print("画像・動画プロンプト生成エージェント 起動")
    results = []
    for i, product in enumerate(products):
        print(f"  [{i+1}/{len(products)}] {product['name'][:40]}")
        acc = random.choice(CUTE_ACCESSORIES)
        print(f"    アクセサリー: {acc}")
        product["gpt_image_prompt"]       = generate_image_prompt(product, accessory=acc)
        product["gpt_image_prompt_notxt"] = generate_image_prompt_notxt(product, accessory=acc)
        product["video_prompt"]           = generate_kling_prompt(product)
        results.append(product)
        print("    ✅ プロンプト生成完了")
    print(f"\n✅ {len(results)} 件のプロンプトを生成しました")
    return results


def run_buzz() -> dict:
    """バズmode：商品なしのダンス画像・動画プロンプトを生成して返す"""
    print("画像・動画プロンプト生成エージェント 起動（バズmode）")
    result = {
        "name": f"バズmode - せなっち生後{MONTH_AGE}ヶ月",
        "price": 0,
        "url": "",
        "affiliate_url": "",
        "item_code": "",
        "gpt_image_prompt": "",
        "gpt_image_prompt_notxt": generate_image_prompt_notxt_buzz(),
        "video_prompt": generate_kling_prompt_buzz(),
        "room_description": "",
        "score": 0,
        "is_buzz_mode": True,
    }
    print("  ✅ バズmodeプロンプト生成完了")
    return result
