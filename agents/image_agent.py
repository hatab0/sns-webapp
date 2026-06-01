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

# 通常mode（PR）：ポーズプール（15種）
PR_POSE_POOL = [
    "sitting upright, holding the product with both chubby hands raised, showing it off to the camera",
    "lying on back with product resting on chest, tiny hands touching it curiously",
    "sitting in a bouncy chair with product in lap, leaning forward with bright interest",
    "held in a gentle seated position, product visible at chest level, arms loosely hugging it",
    "tummy time, product placed just in front, lifting head proudly to look at it",
    "sitting propped against a soft cushion, holding product up toward camera like showing a treasure",
    "lying on side with product snuggled beside, one chubby hand resting on it contentedly",
    "sitting in a high chair, product on the tray, both hands eagerly reaching toward it",
    "held upright under arms by unseen hands, product visible at chest level, legs dangling adorably",
    "sitting cross-legged on a soft blanket, product balanced on knees, gazing down at it with wonder",
    "lying on back, product held directly above face with both hands, studying it with intense focus",
    "sitting and stretching one arm out toward camera with product in hand, offering it to the viewer",
    "reclined at 45 degrees in a baby lounger, product resting on chest, completely relaxed and content",
    "sitting upright beside the product, one hand on it, looking directly at camera with a proud grin",
    "peeking over a soft rolled blanket with the product resting on top, eyes wide and curious",
]

# 通常mode（PR）：表情プール（12種）
PR_EXPRESSION_POOL = [
    "soft content smile, warm happy eyes, peacefully satisfied with the product",
    "wide curious eyes gazing at the product, mouth slightly open in genuine wonder",
    "big bright gummy smile beaming at the camera, chubby cheeks pushed up with pure joy",
    "calm serene expression, completely at ease and natural, peaceful and comfortable",
    "delighted surprise — eyebrows slightly raised, eyes sparkling, genuinely pleased and amazed",
    "gentle proud smile looking directly at camera, confident and warm, showing off the product",
    "focused concentration face, studying the product intently with a little furrowed brow",
    "sleepy-happy expression, heavy-lidded drowsy eyes, soft droopy smile of pure comfort",
    "excited anticipation — mouth slightly open, eyes bright and eager, whole face leaning forward",
    "pure joy laugh — eyes crinkled shut, mouth wide open in silent giggle, shoulders bouncing",
    "innocent wonder — mouth in a perfect small O, eyebrows raised, completely enchanted",
    "shy little smile — head tilted slightly down, eyes looking up at camera through lashes, endearingly bashful",
]

# 直近使用履歴（重複防止）
_pr_used_recent: dict = {"pose": [], "accessory": [], "expression": []}


def _pick_no_repeat(pool: list, used: list, window: int) -> str:
    """直近window件を除外してランダム選択。全て除外される場合はプール全体から選ぶ。"""
    available = [x for x in pool if x not in used[-window:]]
    if not available:
        available = pool
    choice = random.choice(available)
    used.append(choice)
    return choice


# 毎回ランダムで変わるかわいいアクセサリープール（35種）
CUTE_ACCESSORIES = [
    # ━━ おしゃぶり ━━
    "白い丸型シリコーンおしゃぶり（淡いピンクのシールド）",
    "ミントグリーンのおしゃぶり（クマ型シールド付き）",
    "クリーム色のシリコーンおしゃぶり（小花型シールド）",
    "パステルイエローのおしゃぶり（星型シールド付き）",
    # ━━ 帽子・ニット帽 ━━
    "白いポンポン付きニット帽（ベビーサイズ）",
    "淡いピンクのベレー帽",
    "黄色のひよこコスチューム帽子",
    "クリームいろのアニマルニット帽（耳付き）",
    "水色×白のストライプキャップ（つば付き）",
    "ベージュのつば広サンハット（綿素材）",
    "レインボー縞のニット帽（ふわふわポンポン付き）",
    "ライトブルーのベビー野球帽（小さなロゴなし）",
    "オレンジ色のかぼちゃ型ハット",
    # ━━ カチューシャ・ヘアアクセ ━━
    "白いリボンカチューシャ（細いサテンリボン）",
    "ピンクのフリルカチューシャ",
    "くまの耳カチューシャ（ベージュ・もこもこ素材）",
    "うさぎの耳カチューシャ（白・ふわふわ素材）",
    "小花のヘアクリップ（白・ピンク）",
    "いちご柄のヘアバンド（赤×白）",
    "レモン柄のカチューシャ（イエロー×ホワイト）",
    # ━━ スタイ（よだれかけ）━━
    "白いフリル付きスタイ（前掛け）",
    "水色のドット柄スタイとお揃いカチューシャセット",
    "スイカ柄のスタイ（緑×赤・白いフリル付き）",
    "にんじん柄のスタイ（オレンジ×白）",
    "いちご柄のスタイ（赤×白・フリル縁取り）",
    "バナナ柄のスタイ（イエロー×白）",
    "りんご柄のよだれかけ（赤×緑の葉っぱ）",
    "ブロッコリー柄のスタイ（グリーン×白）",
    "チェリー柄のスタイ（赤×白）",
    "パイナップル柄のスタイ（イエロー×グリーン）",
    # ━━ その他アクセサリー ━━
    "もこもこ耳付きフードスタイ（ベージュ・クマ耳）",
    "花柄のヘアバンド（白地にピンクの小花）",
    "チェック柄のよだれかけ（水色×白ギンガムチェック）",
    "虹色のレインボースタイ（グラデーション）",
    "クラウン型ヘアバンド（ゴールド・ベビーサイズ）",
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

# バズmode：月齢別シーン設定（baby_cubo_official スタイル）
# 各月齢グループ 9〜11種類 → _pick_buzz_scene() でランダム選択
# kling_motion: Kling AI Image-to-Video 用の動きの説明（画像シーンと必ず一致）
BUZZ_SCENE_BY_AGE = {
    "0-2": [
        # ── 寝ている（おくるみ）
        {
            "pose": "peacefully sleeping, swaddled snugly in soft muslin cloth, arms tucked in, tiny lips parted",
            "expression": "serene angelic sleeping face, completely relaxed, impossibly tiny and precious",
            "camera": "extreme close-up, face fills 85% of frame, slight overhead angle, very shallow DOF",
            "lighting": "ultra-soft diffused window light, gentle warm glow, no shadows, skin luminous",
            "background": "blurred soft white or cream muslin fabric, completely clean and minimal",
            "kling_motion": "tiny chest rises and falls with slow peaceful breathing, lips twitch slightly in sleep, fingers curl and uncurl gently, serene 8-second seamless loop",
        },
        # ── あくび（大きく体を伸ばす）
        {
            "pose": "lying on back mid full-body stretch, both tiny arms raised, back gently arched, legs extended",
            "expression": "wide perfect yawn — mouth forms a tiny O, eyes squeezed shut, entire face adorably scrunched",
            "camera": "overhead angle directly above, baby centered, capturing full stretch head to toe",
            "lighting": "bright soft morning window light, clean and airy, warm tones",
            "background": "clean white fleece blanket surface, smooth and seamless",
            "kling_motion": "mouth opens wide in a huge adorable yawn, tiny body stretches to its full length, arms reach up, then whole body settles back with a sleepy sigh, 8-second loop",
        },
        # ── むずかる顔（新生児のしかめっ面）
        {
            "pose": "lying on back, both tiny fists raised near cheeks, head tilted slightly to one side",
            "expression": "classic newborn old-man frown — furrowed wrinkled brow, pursed lips, deep serious concentration",
            "camera": "tight close-up on face and fists, straight-on, face fills 80% of frame",
            "lighting": "soft diffused studio light, even and clean, gentle skin luminosity",
            "background": "soft pale pink bokeh background, completely clean",
            "kling_motion": "brow furrows and relaxes in expressive sequence, tiny fists clench and unclench near cheeks, head tilts slowly side to side with ancient wisdom expression",
        },
        # ── 横向き寝（ほっぺたつぶれ）
        {
            "pose": "lying on side in gentle fetal curl, cheek squished softly upward against fluffy surface, one fist near chin",
            "expression": "peacefully sleeping, cheek pushed up into adorable squishy fold, lips slightly parted",
            "camera": "eye-level side angle to capture the squished cheek perfectly, very shallow DOF",
            "lighting": "warm soft rim lighting from behind, gentle glow on hair and cheek edge",
            "background": "ultra-soft blurred white sherpa texture, cozy and warm",
            "kling_motion": "slow peaceful breathing makes squished cheek rise and fall, tiny fingers flutter near chin, eyelids flutter briefly then settle, impossibly cozy 8-second loop",
        },
        # ── じっとカメラを見つめる（古代の目）
        {
            "pose": "lying on back, completely still, staring directly and intensely at the camera with wide open eyes",
            "expression": "maximum alert newborn stare — huge dark eyes wide open, utterly focused, ancient soul expression",
            "camera": "extreme tight close-up, eyes as absolute focal point, fills 90% of frame",
            "lighting": "soft dramatic single window light catching bright catchlights in wide dark eyes",
            "background": "blurred deep navy or charcoal background for dramatic contrast",
            "kling_motion": "enormous dark eyes blink slowly and deliberately, tiny head shifts a fraction, eyes re-lock onto camera with unnerving ancient wisdom, 8-second hypnotic loop",
        },
        # ── O字口（ぽかーん）
        {
            "pose": "lying on back, arms relaxed at sides, face centered and fully visible, completely still",
            "expression": "perfect O-mouth — lips form a flawless small round circle, eyes wide and unblinking, genuinely surprised by existence",
            "camera": "extreme close-up, mouth and eyes filling 85% of frame, razor sharp focus on the O-shape",
            "lighting": "bright even soft light, every detail of the tiny O-mouth crystal clear",
            "background": "clean cream or soft white bokeh, no distractions",
            "kling_motion": "lips hold the perfect O shape then slowly relax and reform it, tiny eyebrows rise and fall, occasional slow blink, mesmerizing adorable loop",
        },
        # ── ミルクを飲む
        {
            "pose": "cradled in arms at feeding angle, head supported, bottle or nursing in progress, tiny hands resting on chest",
            "expression": "blissful milk-drunk contentment — eyes heavy and slowly closing, pure satisfaction spreading across face",
            "camera": "close-up on face at 45-degree angle, capturing the feeding moment and expression simultaneously",
            "lighting": "warm golden soft light, intimate and cozy, like a quiet evening",
            "background": "blurred warm blanket and arm, soft home setting",
            "kling_motion": "mouth makes gentle rhythmic sucking motions, tiny hands open and close slowly, eyelids grow heavier and heavier, head relaxes further into milk-drunk bliss",
        },
        # ── しゃっくり
        {
            "pose": "lying on back, arms slightly raised, eyes wide, caught in the middle of a hiccup",
            "expression": "hiccup surprise — eyes go wide with each tiny jolt, eyebrows shoot up, expression resets and repeats",
            "camera": "tight close-up on face, capturing the repeated micro-expression of each hiccup",
            "lighting": "bright soft window light, warm and clear",
            "background": "clean cream or white bokeh",
            "kling_motion": "tiny body jolts adorably with each hiccup, eyes go wide and hands flail slightly, expression resets, jolts again rhythmically, irresistibly funny 8-second loop",
        },
        # ── 眠そうに目をこする
        {
            "pose": "lying on back, one tiny fist raised to eye level, just beginning to rub eye with knuckle",
            "expression": "ultimate drowsy face — eyelids at half-mast, one eye being rubbed, soft unfocused gaze, melting with sleepiness",
            "camera": "close-up on face and rubbing fist, warm intimate framing",
            "lighting": "soft warm dim light, like late afternoon or bedtime glow",
            "background": "blurred cozy bedding, warm cream tones",
            "kling_motion": "tiny fist rubs eye in slow circles, head droops forward then bobs back up, eyelids flutter heavy and slow, fighting sleep with every ounce of newborn will",
        },
    ],
    "3": [
        # ── はじめての笑顔
        {
            "pose": "lying on back, legs kicking high in the air, arms reaching up, caught at peak of first big laugh",
            "expression": "very first social smile blooming — round chubby cheeks, eyes crinkled to slits, pure joy",
            "camera": "close-up face and chest, slight low angle looking up at baby, 85mm portrait style",
            "lighting": "soft warm studio light, bright catchlights making eyes sparkle",
            "background": "soft pastel mint green bokeh, clean and fresh",
            "kling_motion": "face slowly breaks into a massive gummy smile, arms flap with joy, legs kick excitedly in the air, whole tiny body expresses pure happiness",
        },
        # ── うつぶせ（首を上げようと必死）
        {
            "pose": "tummy time, barely managing to lift head, chin quivering with effort, arms tucked underneath",
            "expression": "intense tiny determination face — brow furrowed, eyes wide, trying with all available willpower",
            "camera": "very low angle, exactly eye level on tummy, face fills majority of frame",
            "lighting": "warm soft side window light, showing effort in face and texture",
            "background": "soft textured play mat, warm muted colors blurred",
            "kling_motion": "head strains upward with maximum effort, chin quivers, head lifts for a triumphant moment then slowly lowers, brow furrowed with heroic determination throughout",
        },
        # ── 驚きのO口（びっくり顔）
        {
            "pose": "lying on back, mid-movement frozen completely still, staring at camera in total shock",
            "expression": "maximum surprise face — mouth wide open O-shape, eyebrows raised to hairline, eyes enormous",
            "camera": "overhead angle straight down, face fills center of frame completely",
            "lighting": "bright even overhead light, clean white and airy",
            "background": "clean pastel yellow blanket, warm and cheerful",
            "kling_motion": "eyes go wide and mouth drops open in a perfect O, frozen in shock for a beat, then slowly recovers and resets, only to repeat the surprise — endlessly viral loop",
        },
        # ── お風呂でびっくり
        {
            "pose": "sitting in tiny baby bathtub, water droplets on chubby arms, one hand caught mid-splash",
            "expression": "water shock delight — eyes wide, mouth in surprised O, water droplets sparkling on chubby cheeks",
            "camera": "medium close-up, slight overhead angle, water surface catching light",
            "lighting": "bright bathroom window light, water droplets sparkling",
            "background": "soft white bath towel edge visible, tiles softly blurred behind",
            "kling_motion": "hand splashes water sending droplets flying, baby flinches with wide-eyed delight, then reaches to splash again, water droplets catching light beautifully",
        },
        # ── 冷静な判定顔
        {
            "pose": "held upright facing camera at chest height, tiny feet dangling, both fists clenched at sides",
            "expression": "supremely serious judgement face — staring directly into camera with ancient wisdom eyes, unimpressed",
            "camera": "medium shot from slightly below, baby gazing down at camera with gravity",
            "lighting": "soft diffused studio light, clean and professional",
            "background": "blurred soft gray or white background, minimal and elegant",
            "kling_motion": "eyes scan slowly across the frame with judicial authority, tiny fists clench and unclench, head tilts a fraction in assessment, utterly unimpressed expression holds perfectly",
        },
        # ── プーメリーを見つめる
        {
            "pose": "lying on back directly beneath a colorful mobile toy, eyes locked upward in total fascination",
            "expression": "absolute lock-on focus — huge dark eyes tracking moving shapes above, mouth slightly open in pure wonder",
            "camera": "low angle looking up toward baby's face with mobile toy shapes blurred in background above",
            "lighting": "soft bright room light, clean and fresh",
            "background": "blurred colorful mobile toy shapes above, clean ceiling light behind",
            "kling_motion": "eyes track mobile shapes moving overhead with laser-locked precision, arms slowly reach upward toward the toy, legs kick with growing excitement, tiny fingers grasp at air",
        },
        # ── あくび（小さい体で大きなあくび）
        {
            "pose": "lying on back, mouth wide open in a giant yawn, both arms raising slightly",
            "expression": "enormous yawn overwhelming tiny face — mouth opens impossibly wide, eyes squeeze shut, face crinkles adorably",
            "camera": "tight close-up on face, the yawn as absolute focal point",
            "lighting": "soft warm light, cozy and intimate",
            "background": "blurred soft bedding or blanket, warm cream tones",
            "kling_motion": "mouth opens progressively wider in a massive yawn, eyes squeeze shut, whole face crinkles, tiny arms float upward, then everything settles back with a sleepy satisfied expression",
        },
        # ── 泣きそう（うるうる）
        {
            "pose": "lying on back, face beginning to crumple, bottom lip jutting out dramatically",
            "expression": "maximum pre-cry drama — bottom lip trembling and protruding, eyes beginning to gloss over, brow furrowing in tragedy",
            "camera": "extreme close-up on face, the trembling lip as dramatic focal point",
            "lighting": "soft warm light with gentle catchlights making welling eyes glisten",
            "background": "blurred soft background, warm tones",
            "kling_motion": "bottom lip begins to quiver and jut out dramatically, eyes well up slowly, brow furrows in escalating tragedy, face crumples in the most heartbreaking adorable slow-motion pre-cry",
        },
        # ── 眠そうに目をこする
        {
            "pose": "lying on back, tiny fist raised, rubbing one eye slowly with knuckle",
            "expression": "deeply drowsy — one eye half-closed being rubbed, other eye drooping, completely surrendering to sleep",
            "camera": "warm close-up on sleepy face and rubbing fist",
            "lighting": "soft dim warm light, bedtime atmosphere",
            "background": "blurred cozy blanket, warm cream tones",
            "kling_motion": "tiny fist rubs eye in slow deliberate circles, head lolls to one side, eyelids fight gravity and lose, the most relatable sleepy struggle in 8 seconds",
        },
    ],
    "4-5": [
        # ── うつぶせ大笑い
        {
            "pose": "tummy time, head lifted high and proud, chest fully off mat, arms extended, showing off neck strength",
            "expression": "enormous open-mouth laugh, chubby cheeks puffed, eyes wide with joy — genuinely candid moment",
            "camera": "low angle front-on, eye level with baby's face, face as sharp focal point",
            "lighting": "soft warm studio light, prominent catchlights in laughing eyes",
            "background": "creamy white bokeh, clean and simple",
            "kling_motion": "head lifts proudly and holds, then face breaks into a huge open-mouth laugh, chubby cheeks bounce with the laughter, pure joy radiating from every feature",
        },
        # ── 両手万歳で大興奮
        {
            "pose": "lying on back with both arms raised triumphantly, legs kicking simultaneously in pure excitement",
            "expression": "absolute peak excitement — eyes crinkled shut in huge grin, cheeks at maximum chubbiness",
            "camera": "overhead angle, baby fills 85% of frame, looking up at camera",
            "lighting": "bright soft overhead studio light, clean white fill, celebratory",
            "background": "bright white background, clean and crisp",
            "kling_motion": "arms pump up and down triumphantly, legs kick in simultaneous joy, whole body radiates excitement, the grin never fades — pure celebratory energy for 8 seconds",
        },
        # ── 寝返りの途中でびっくり顔
        {
            "pose": "caught perfectly mid-roll from back to tummy — body halfway tilted, one arm trapped underneath",
            "expression": "completely confused where-am-I face — one eye visible, mouth open O, pure adorable bewilderment",
            "camera": "straight-on medium close-up capturing the mid-roll suspended moment",
            "lighting": "bright clean studio light",
            "background": "colorful play mat, primary colors softly blurred",
            "kling_motion": "body slowly completes the roll from back to tummy, one arm gets trapped, baby freezes with a totally bewildered expression, tries to figure out what just happened",
        },
        # ── 足をつかんで自慢顔
        {
            "pose": "lying on back, both hands successfully grabbing both feet simultaneously, legs lifted high, very proud",
            "expression": "enormously self-satisfied giggling face — eyes squeezed shut laughing, incredibly proud of foot discovery",
            "camera": "slight overhead angle to see both hands gripping feet together",
            "lighting": "warm soft window light, natural feel",
            "background": "soft pastel blue or lavender blanket, dreamy and clean",
            "kling_motion": "both hands grip feet triumphantly, body rocks side to side with self-satisfaction, giggles with the pure joy of having discovered feet — a genius achievement",
        },
        # ── ほっぺたぺたんこ（横向き）
        {
            "pose": "lying on side, cheek pressed flat against soft surface creating maximum squish, eyes looking up at camera",
            "expression": "helpless squished-cheek cuteness — one eye bigger from squish, small surprised mouth, maximum chub",
            "camera": "extreme tight close-up filling entire frame, squished cheek as main focus",
            "lighting": "ultra-soft window light, flattering on squishy cheek",
            "background": "blurred pink or peach soft fabric, warm and cozy",
            "kling_motion": "squished cheek pulses gently with breathing, single visible eye blinks slowly and looks directly at camera, tiny mouth forms expressions, impossibly squishy and cozy",
        },
        # ── プーメリーで大興奮
        {
            "pose": "lying on back beneath a colorful mobile toy, both arms reaching upward, legs kicking with excitement",
            "expression": "electric excitement — eyes tracking moving toy above, mouth open mid-excited-squeal, pure sensory delight",
            "camera": "45-degree angle showing baby reaching up toward the mobile, toy shapes visible above",
            "lighting": "bright cheerful room light",
            "background": "blurred colorful mobile shapes above, bright clean room",
            "kling_motion": "arms reach and grasp toward mobile shapes, legs kick rhythmically with excitement, eyes track moving pieces with total focus, occasional excited squeal ripples through tiny body",
        },
        # ── ミルクでうとうと
        {
            "pose": "cradled at feeding angle, bottle nearby, completely milk-drunk and heavy-lidded",
            "expression": "full milk-drunk bliss — eyes rolling slowly, cheeks flushed pink, the most satisfied tiny human alive",
            "camera": "warm close-up on milk-drunk face, intimate and cozy",
            "lighting": "golden warm soft light, evening feeding atmosphere",
            "background": "blurred cozy arms and blanket",
            "kling_motion": "eyelids droop and flutter, head lolls with milk-drunk satisfaction, lips make tiny sucking motions even when not feeding, the definition of contentment in 8 seconds",
        },
        # ── あくびで体がくにゃっ
        {
            "pose": "lying on back, mid-enormous-yawn, mouth open wide, tiny body arching slightly with the effort",
            "expression": "whole-body yawn — mouth at maximum aperture, eyes squeezed shut, face gloriously scrunched",
            "camera": "close-up capturing the full theatrical yawn expression",
            "lighting": "soft warm natural light",
            "background": "blurred soft bedding, cozy warm tones",
            "kling_motion": "yawn builds progressively, mouth opens wider and wider, tiny body arches with the effort, face crinkles magnificently, then the whole body relaxes with a satisfied exhale",
        },
        # ── O字口でぽかーん
        {
            "pose": "lying on back, arms at sides, face in perfect repose with lips in a tiny round O",
            "expression": "signature O-mouth wonder — lips in a perfect small circle, eyes wide and unblinking, completely absorbed in existence",
            "camera": "extreme close-up, the perfect O-mouth and wide eyes as focal point, 80% of frame",
            "lighting": "bright clean soft light, every detail sharp",
            "background": "clean simple bokeh, no distractions",
            "kling_motion": "lips hold the perfect O shape then slowly widen as eyes go rounder, tiny brow raises, the O-mouth cycles through variations of wonder — the most viral expression possible",
        },
        # ── 泣きそう（下唇ぷるぷる）
        {
            "pose": "sitting with slight support, face beginning to crumple, bottom lip protruding dramatically",
            "expression": "award-winning pre-cry performance — bottom lip trembling at maximum drama, eyes welling, brow furrowing deeply",
            "camera": "tight close-up, the quivering lip as cinematic focal point",
            "lighting": "soft light making welling eyes glisten perfectly",
            "background": "blurred warm background",
            "kling_motion": "bottom lip begins its dramatic quiver, eyes fill with glossy tears, face crumples in exquisite slow-motion tragedy, then resets and begins again — 8 seconds of pure drama",
        },
    ],
    "6-7": [
        # ── 手を伸ばして好奇心爆発
        {
            "pose": "sitting with slight support, leaning noticeably forward, one hand fully extended reaching toward camera",
            "expression": "wide-eyed wonder and curiosity — eyebrows raised high, mouth slightly open in pure amazement",
            "camera": "medium shot head to waist, slight low angle to make baby look grand",
            "lighting": "bright soft light, warm tones, clear sparkling catchlights",
            "background": "soft sofa corner or textured knit blanket lifestyle setting, warm blurred",
            "kling_motion": "body leans forward with growing curiosity, reaching hand extends further toward camera, eyes go wider and wider, mouth opens slightly more — magnetic pull toward the world",
        },
        # ── 離乳食で絶句
        {
            "pose": "sitting in high chair, first food just tasted, spoon pulled away, face covered in orange puree",
            "expression": "impossible-to-read first food verdict — one eye squinted, brow twisted, mouth puckered, jury still out",
            "camera": "close-up on food-covered face, straight level angle capturing full reaction",
            "lighting": "bright natural kitchen window light, warm and lively",
            "background": "high chair tray edge visible, blurred warm kitchen behind",
            "kling_motion": "face processes the flavor in real time — expressions cycle through confusion, disgust consideration, and grudging interest, head tilts side to side deliberating the verdict",
        },
        # ── バウンシングで大笑い
        {
            "pose": "being held standing on adult lap, both knees bending deep and bouncing with unstoppable joy and rhythm",
            "expression": "unstoppable bouncing delight — mouth wide open mid-laugh, eyes crinkled, whole body involved",
            "camera": "medium front shot, slight motion blur on bouncing legs showing energy",
            "lighting": "warm cozy living room light, golden afternoon feel",
            "background": "blurred soft living room setting, warm and homey",
            "kling_motion": "knees bend deep and spring back rhythmically, whole body bounces with joyful momentum, head bobs, mouth stays open in continuous laughter, arms wave with the beat",
        },
        # ── いないいないばあ（爆笑）
        {
            "pose": "hands just pulled away from face in peekaboo reveal, eyes huge, whole body leaning forward in shock",
            "expression": "peekaboo explosion of laughter — mouth open in full guffaw, eyes crinkled, delighted total shock",
            "camera": "close-up capturing the revealed expression, hands visible at frame edges",
            "lighting": "bright warm studio light, sparkling catchlights in surprised eyes",
            "background": "clean soft pink or lavender bokeh background",
            "kling_motion": "hands lower slowly from face, eyes go enormous, then full-body laughter explosion — mouth wide open, shoulders shaking, arms waving — then hands raise back up for another round",
        },
        # ── 完璧なサイドアイ
        {
            "pose": "sitting propped, facing mostly forward but eyes cutting sharply sideways — full baby side-eye",
            "expression": "legendary baby side-eye — one eyebrow marginally higher, mouth neutral, pure unbothered judgment",
            "camera": "straight-on medium close-up, capturing the sideways eye direction perfectly",
            "lighting": "slightly dramatic single side lighting emphasizing the expression",
            "background": "clean deep blue or gray backdrop for comedic contrast",
            "kling_motion": "eyes slide slowly to the extreme side while head stays perfectly still, expression remains stonily neutral, holds the iconic side-eye for maximum comedic effect, occasionally blinks without breaking gaze",
        },
        # ── プーメリーに手が届きそう
        {
            "pose": "sitting with support, both arms stretched high overhead toward a colorful mobile toy, straining to reach",
            "expression": "determined reaching face — tongue tip visible with effort, eyes fixed upward on the prize, so close yet so far",
            "camera": "slight low angle showing baby reaching up, toy shapes visible above",
            "lighting": "bright cheerful room light",
            "background": "blurred mobile toy above, bright clean room",
            "kling_motion": "arms stretch higher and higher toward mobile, whole body strains upward, fingers grasp at air just below the toy, triumphant squeal when fingertips finally brush it",
        },
        # ── しゃっくりで体がぴくっ
        {
            "pose": "sitting with support, eyes wide, caught mid-hiccup with a tiny body jolt",
            "expression": "hiccup surprise — eyes go wide with each jolt, expression resets between each one, completely at mercy of hiccups",
            "camera": "medium close-up capturing the repeating surprise expression",
            "lighting": "bright natural light, warm and clear",
            "background": "clean bokeh background",
            "kling_motion": "body jolts with each hiccup, eyes fly wide open, expression resets, jolts again — rhythmic adorable helplessness that is 100% relatable and shareable",
        },
        # ── ミルク後の満足顔
        {
            "pose": "cradled after feeding, completely satisfied, head lolling to one side, milk residue at corner of mouth",
            "expression": "ultimate milk-drunk satisfaction — eyes glazed with contentment, tiny smile, the face of someone who has everything",
            "camera": "close-up on the blissful satisfied face",
            "lighting": "warm golden evening light, intimate",
            "background": "blurred soft blanket and arm",
            "kling_motion": "face radiates pure satisfaction, eyes slowly drift closed then half-open again, tiny bubble forms at corner of milk-satisfied mouth, body completely boneless with contentment",
        },
        # ── あくびで全力でとろける
        {
            "pose": "sitting with support, massive yawn overtaking entire face, arms drooping",
            "expression": "massive sit-up yawn — mouth open to maximum, eyes squeezed tight, arms going slack with tiredness",
            "camera": "close-up front-on capturing the theatrical full-face yawn",
            "lighting": "soft warm light",
            "background": "blurred cozy setting",
            "kling_motion": "yawn builds slowly and magnificently, mouth opens wider and wider, arms droop helplessly, whole body melts downward, then snaps back slightly more awake — only to start yawning again",
        },
        # ── 目をこすりながらとろける
        {
            "pose": "sitting, one fist rubbing eye vigorously, head starting to droop",
            "expression": "maximum sleepy struggle — one eye being rubbed, other half-closed, losing the battle against sleep in real time",
            "camera": "warm medium close-up on droopy sleepy face",
            "lighting": "soft dim warm light",
            "background": "blurred cozy home setting",
            "kling_motion": "fist rubs eye in slow circles while head droops forward, almost touches chin to chest, then bobs back up surprised, rubs eye again — the cutest losing battle with sleep",
        },
    ],
    "8-9": [
        # ── 指差しカメラ目線
        {
            "pose": "sitting very independently, one finger pointing directly and authoritatively at camera",
            "expression": "animated personality fully present — intense eye contact, slight smirk, owner of the room energy",
            "camera": "medium close-up, very slight dynamic angle, face as undeniable main subject",
            "lighting": "vibrant warm light, sharp bright catchlights in eyes",
            "background": "bold solid color backdrop, deep red or royal blue for personality",
            "kling_motion": "finger extends with authority and points directly at camera, head tilts knowingly, eyes maintain intense contact, the smirk deepens — this baby runs things",
        },
        # ── ハイハイで突進
        {
            "pose": "mid-crawl with one hand raised off the ground, looking up at camera like a tiny conqueror",
            "expression": "pure crawling triumph — enormous open grin, eyes bright and proud, total conquest expression",
            "camera": "very low angle, slightly in front of baby, capturing crawl and face simultaneously",
            "lighting": "bright natural floor-level light, warm tones",
            "background": "soft play mat colors blurred, clean room behind",
            "kling_motion": "body propels forward with crawling determination, head lifts to check the camera, huge grin never fades, arms alternate with purposeful conquest energy — coming straight for you",
        },
        # ── 何かを激しく研究する
        {
            "pose": "sitting, holding a small colorful object in both hands, bringing it extremely close to face to study",
            "expression": "full scientist investigation mode — brow furrowed intensely, eyes crossing slightly at close object",
            "camera": "medium close-up from front, baby's face and the object both in frame",
            "lighting": "bright window light, natural and clear",
            "background": "warm blurred home interior, cozy feeling",
            "kling_motion": "object gets brought closer and closer to face for maximum examination, eyes cross slightly with focus, turns it over carefully, holds it up to light — tiny serious scientist",
        },
        # ── 拍手して自画自賛
        {
            "pose": "sitting upright, both hands coming together in a big enthusiastic clap, arms spread wide",
            "expression": "self-congratulatory clapping joy — huge beam, eyes dancing, so proud of own clapping ability",
            "camera": "medium shot slightly wide to capture the hand-clap motion, slight hand blur",
            "lighting": "bright warm studio light, clean celebration feel",
            "background": "bright pastel yellow or orange single-color, cheerful",
            "kling_motion": "hands clap together enthusiastically then spread wide for the next clap, body bounces with each clap, expression radiates self-congratulation — I did clapping and it was perfect",
        },
        # ── 究極のサイドアイ
        {
            "pose": "sitting perfectly still, looking straight at camera, eyes cutting hard to one side — supreme side-eye",
            "expression": "ultimate skeptical side-eye — one brow raised, lips pressed together, deep unimpressed judgment",
            "camera": "extreme tight close-up filling 90% of frame, totally straight-on",
            "lighting": "slightly moody single side light to emphasize the iconic skeptical expression",
            "background": "dark moody charcoal or black bokeh for maximum comedic contrast",
            "kling_motion": "eyes slide to extreme side position with devastating slowness, one brow raises with perfect comic timing, holds the side-eye for maximum impact, then snaps back to center — unbothered",
        },
        # ── プーメリーで大発見
        {
            "pose": "sitting, both arms raised toward a toy above, one hand has just grabbed it with triumph",
            "expression": "I CAUGHT IT triumph — eyes wide with disbelief at own achievement, mouth open in silent victory scream",
            "camera": "slight low angle celebrating the achievement, toy visible above",
            "lighting": "bright triumphant light",
            "background": "blurred colorful room",
            "kling_motion": "hand finally grabs the toy after straining, face explodes with triumph, whole body shakes with the victory, shows the caught toy to camera proudly",
        },
        # ── しゃっくりで固まる
        {
            "pose": "sitting independently, caught mid-hiccup, entire body stiffened with the jolt",
            "expression": "hiccup freeze — body jolted stiff, eyes wide, expression reboots between each one",
            "camera": "medium shot to capture the full-body hiccup jolt",
            "lighting": "bright clear light",
            "background": "clean cheerful bokeh",
            "kling_motion": "sitting peacefully then JOLT — whole body stiffens with the hiccup, eyes fly open, resets to normal, then JOLT again — rhythmic adorable helplessness on repeat",
        },
        # ── あくびで眠そうにかわいい
        {
            "pose": "sitting, enormous yawn taking over, arms going slack, head beginning to droop",
            "expression": "seated yawn collapse — mouth open huge, eyes squeezed shut, whole body slowly melting downward",
            "camera": "medium close-up capturing the theatrical yawn",
            "lighting": "soft warm light",
            "background": "cozy home setting blurred",
            "kling_motion": "massive yawn builds while sitting, mouth opens to full extent, body slowly melts sideways with tiredness, catches self, sits back up — immediately begins the next yawn",
        },
        # ── 眠そうに目をごしごし
        {
            "pose": "sitting, both fists rubbing both eyes simultaneously, head drooping",
            "expression": "maximum sleep resistance — both eyes being rubbed vigorously, head drooping, losing consciousness by degrees",
            "camera": "close-up on the adorable two-fisted eye-rubbing",
            "lighting": "soft warm dim light",
            "background": "blurred cozy setting",
            "kling_motion": "both fists rub both eyes vigorously, head droops further with each rub, fighting sleep with everything available, a battle already lost — the most relatable 8 seconds ever",
        },
    ],
    "10-12": [
        # ── つかまり立ちで達成感
        {
            "pose": "pulling to stand holding furniture edge, legs straight, chest puffed with enormous first-time pride",
            "expression": "milestone achievement beam — huge open smile, bright eyes, pride radiating from entire face",
            "camera": "full body shot to show the standing achievement, slight low angle to celebrate it",
            "lighting": "bright celebratory studio light, clean and crisp",
            "background": "clean minimal light backdrop, all focus on achievement",
            "kling_motion": "pulls up to standing with determination, straightens to full height, beams with enormous pride at the camera, bounces slightly on wobbly legs — I AM STANDING",
        },
        # ── 頭上拍手で全身バウンス
        {
            "pose": "sitting and clapping both hands high overhead enthusiastically, whole body bouncing with the rhythm",
            "expression": "maximum celebration energy — eyes squeezed shut laughing, mouth fully open, pure joy abandon",
            "camera": "medium shot to capture the overhead clap and full-body bounce together",
            "lighting": "bright cheerful studio light, high energy feeling",
            "background": "bright pastel single-color, festive pink or sky blue",
            "kling_motion": "hands clap high overhead rhythmically, whole body bounces with each clap, laughter overflows, can't contain the celebration energy — pure unstoppable joy in motion",
        },
        # ── 一人立ちでぐらぐら
        {
            "pose": "standing completely free with nothing to hold, arms spread wide for balance, frozen mid-wobble",
            "expression": "terror-joy hybrid face — eyes enormous, mouth open, somewhere between falling and flying",
            "camera": "full body shot, slight low angle to emphasize the gravity-defying moment",
            "lighting": "clean bright light, every detail sharp",
            "background": "clean minimal home interior or white backdrop",
            "kling_motion": "stands free and wobbles dramatically, arms pinwheel for balance, face cycles through terror and triumph, manages to hold it for a glorious moment before sitting down purposefully",
        },
        # ── バイバイで全力の手降り
        {
            "pose": "sitting or pulling to stand, waving one arm in full enthusiastic arc — big exaggerated bye-bye",
            "expression": "social milestone pride — giant grin while waving, so proud of knowing bye-bye skill",
            "camera": "medium shot capturing face and enthusiastic waving arm together",
            "lighting": "warm bright natural light, homey feeling",
            "background": "warm lifestyle home setting, blurred interior",
            "kling_motion": "arm waves in big enthusiastic arcs, face beams with pride at mastering this skill, occasionally uses both arms for extra emphasis — bye-bye is serious important business",
        },
        # ── いないいないばあで目が覗く
        {
            "pose": "both hands covering face in peekaboo, but one eye peeking through gap in fingers, building anticipation",
            "expression": "barely-contained excitement — one eye wide peeking through fingers, huge suppressed grin visible",
            "camera": "close-up, eye peeking through finger gap as absolute focal point, very shallow DOF",
            "lighting": "warm playful light, bright catchlight in the single peeking eye",
            "background": "soft blurred pastel colors, warm and playful",
            "kling_motion": "single eye peeks through fingers with mischievous anticipation, suppressed grin grows unstoppably, then hands drop for the big reveal — BOO — full explosion of laughter",
        },
        # ── しゃっくりでびっくり
        {
            "pose": "sitting, caught mid-hiccup with whole body stiffening in surprise",
            "expression": "hiccup interruption — in the middle of something important when the hiccup hits, maximum indignant surprise",
            "camera": "medium close-up capturing the full hiccup expression",
            "lighting": "bright clear light",
            "background": "clean colorful setting",
            "kling_motion": "sitting doing important baby business when a hiccup interrupts — body jolts, expression goes outraged, attempts to recover dignity, immediately hiccups again — the cycle of life",
        },
        # ── ミルクでにこにこ
        {
            "pose": "sitting after feeding, slightly pink-cheeked, small content smile, occasionally patting own tummy",
            "expression": "post-milk satisfaction — warm rosy cheeks, slow contented blinks, the expression of someone who has achieved everything",
            "camera": "warm close-up on contented face",
            "lighting": "golden warm light, after-meal glow",
            "background": "blurred cozy setting",
            "kling_motion": "pats own full tummy contentedly, blinks slow and satisfied, breaks into a warm smile then looks at camera as if to say 'yes, this is the life'",
        },
        # ── あくびで崩れ落ちる
        {
            "pose": "sitting, overtaken by a giant yawn, whole body beginning to melt sideways",
            "expression": "total yawn surrender — mouth at maximum, eyes completely shut, body tilting sideways helplessly",
            "camera": "medium shot capturing both the yawn and the body melt",
            "lighting": "soft warm light",
            "background": "cozy setting blurred",
            "kling_motion": "yawn builds to maximum, body tilts further and further sideways, catches self at last moment, shakes head to wake up, immediately starts the next yawn — can't be stopped",
        },
        # ── 目をごしごし→ぱっと明るく
        {
            "pose": "sitting, vigorously rubbing eyes, then peeking one eye open to check if anyone noticed",
            "expression": "strategic eye-rubbing — rubbing with exaggerated effort, then sneaking one eye open to see the reaction",
            "camera": "close-up on the rubbing and the strategic peek",
            "lighting": "warm gentle light",
            "background": "cozy home setting",
            "kling_motion": "rubs eyes with theatrical effort, sneaks one eye open to check the audience reaction, sees they're watching, immediately rubs harder for maximum sympathy effect — a performer",
        },
    ],
    "13+": [
        # ── よちよち歩きで突進
        {
            "pose": "toddling with both arms stretched fully out wide for balance, one foot mid-step, utterly determined",
            "expression": "intense walking concentration face — tongue slightly out, eyes focused forward, absolute determination",
            "camera": "full body shot, slight low angle, capturing the whole toddling journey",
            "lighting": "bright energetic room light, lively and warm",
            "background": "colorful indoor play setting, toys visible and blurred",
            "kling_motion": "toddling forward with full commitment, arms spread wide for balance, pauses to correct course, then surges forward again — the most determined tiny person on earth",
        },
        # ── 禁断の何かに手を伸ばす
        {
            "pose": "caught doing something forbidden — hand outstretched toward off-limits thing, freeze-frame guilty moment",
            "expression": "maximum caught-in-the-act face — eyes wide, mouth O-shaped, complete freeze-frame guilt and shock",
            "camera": "medium shot showing both the forbidden reach and the guilty expression simultaneously",
            "lighting": "bright natural home light, nothing hidden, fully exposed",
            "background": "home setting, recognizable domestic environment, warm tones",
            "kling_motion": "hand slowly inches toward forbidden object, gets closer and closer, then catches you watching — freezes completely, eyes wide with guilt, tries to look innocent",
        },
        # ── くるくる回って転ぶ
        {
            "pose": "mid-spin, just beginning to lose balance and topple sideways, one arm flailing for balance",
            "expression": "spinning delirium laughter — mouth fully open, eyes unfocused and dizzy, about to magnificently fall",
            "camera": "medium full-body shot capturing the spin and the impending joyful fall",
            "lighting": "bright energetic light, sense of movement and chaos",
            "background": "blurred colorful living room, motion and life blurred behind",
            "kling_motion": "spins with increasing speed and decreasing control, dizziness sets in, loses balance magnificently, falls softly and laughs from the floor, immediately tries to stand and spin again",
        },
        # ── 逃げながら振り返りにっこり
        {
            "pose": "seen from behind and slight side, chubby legs running at full toddler sprint, head turned looking back grinning",
            "expression": "gleeful escape look over shoulder — huge grin, complete joy at being chased, wind-in-hair energy",
            "camera": "medium shot from behind-side angle, face visible in the turned-back look",
            "lighting": "bright indoor or soft outdoor light, energetic and lively",
            "background": "hallway or garden path, motion blur on pumping legs",
            "kling_motion": "chubby legs pump at full sprint, turns to grin at camera over shoulder, almost trips but doesn't, laughs and runs faster — the pure joy of being chased",
        },
        # ── しゃがんで何かを激しく調査
        {
            "pose": "perfect full toddler squat on chubby legs, face inches from the floor examining something tiny on the ground",
            "expression": "total scientific absorption — face extremely close to ground, eyebrows furrowed, world completely forgotten",
            "camera": "side-on angle showing the full adorable toddler squat, camera at floor level",
            "lighting": "natural floor-level warm light, soft and intimate",
            "background": "blurred floor surface and room behind, minimal and quiet",
            "kling_motion": "squats with perfect toddler form to examine something fascinating, gets face closer and closer to the ground, pokes it carefully, looks up to report findings with great seriousness",
        },
        # ── しゃっくりに激しく動揺する
        {
            "pose": "standing or sitting, arms out, clearly outraged by the audacity of hiccups interrupting daily business",
            "expression": "toddler hiccup indignation — each hiccup jolts the whole body, expression oscillates between surprise and deep offense",
            "camera": "medium shot capturing the full dramatic hiccup performance",
            "lighting": "bright clear light",
            "background": "colorful toddler setting",
            "kling_motion": "conducting important toddler business when hiccups strike — full-body jolts, looks around accusingly, attempts to stop hiccups by sheer force of will, fails dramatically, jolt again",
        },
        # ── あくびして床でとろける
        {
            "pose": "sitting on floor mid-enormous-yawn, body slowly tipping sideways toward the ground",
            "expression": "epic yawn collapse — mouth at absolute maximum, eyes squeezed shut, body slowly going horizontal",
            "camera": "medium wide shot capturing both the yawn and the slow floor descent",
            "lighting": "warm soft light",
            "background": "colorful play area blurred",
            "kling_motion": "yawn hits like a truck, body slowly tips sideways against gravity, lands gently on side, eyes still closed, rolls onto back and continues sleeping — fully committed",
        },
        # ── 目をこすって悲劇顔
        {
            "pose": "standing or sitting, both fists rubbing both eyes, face scrunched in maximum tired drama",
            "expression": "theatrical tired protest — eyes being rubbed with Oscar-worthy commitment, face scrunched in tragedy",
            "camera": "close-up on the dramatic eye-rubbing performance",
            "lighting": "warm soft light",
            "background": "cozy home setting",
            "kling_motion": "rubs eyes with maximum dramatic commitment, occasionally stops to make a tragic face at the camera seeking sympathy, then rubs harder — pure toddler performance art",
        },
        # ── O字口で完璧なポカーン
        {
            "pose": "standing or sitting, caught in a perfect O-mouth moment of total surprise or wonder",
            "expression": "legendary toddler O-mouth — lips in a perfect circle of absolute astonishment, eyes enormous, frozen in wonder",
            "camera": "tight close-up, the magnificent O-mouth as centerpiece",
            "lighting": "bright clear light, O-mouth perfectly illuminated",
            "background": "clean simple bokeh",
            "kling_motion": "O-mouth opens in stages of growing astonishment, eyes widen in sync, stays frozen in perfect wonder for comedic duration, then snaps back to normal as if nothing happened",
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


def _base_image_prompt_text(product: dict, accessory: str = "", pose: str = "", expression: str = "") -> str:
    """商品あり：画像プロンプトの共通部分（2枚参照画像前提）"""
    acc = accessory or random.choice(CUTE_ACCESSORIES)
    selected_pose = pose or random.choice(PR_POSE_POOL)
    selected_expression = expression or random.choice(PR_EXPRESSION_POOL)
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
・ポーズ：{selected_pose}
・表情：{selected_expression}

【背景・雰囲気】
・背景：クリーム色・アイボリー・ベージュのナチュラルスタジオ
・小物：白いふわふわのブランケット・薄いモスリンガーゼ
・全体的にナチュラル・オーガニック・清潔感のある世界観
"""


_last_buzz_scene_pose: str = ""


def _pick_buzz_scene() -> dict:
    """バズmode：月齢に合ったシーンを1つ選ぶ。直前と同じシーンは除外して連続を防ぐ。"""
    global _last_buzz_scene_pose
    age_group = _get_age_group(MONTH_AGE)
    scenes = BUZZ_SCENE_BY_AGE.get(age_group, BUZZ_SCENE_BY_AGE["4-5"])
    available = [s for s in scenes if s.get("pose") != _last_buzz_scene_pose]
    if not available:
        available = scenes
    scene = random.choice(available)
    _last_buzz_scene_pose = scene.get("pose", "")
    return scene


def _base_scene_text_buzz(scene: dict) -> str:
    """バズmode：baby_cubo_officialスタイルの月齢特化シーン（参照画像1枚のみ）"""
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


def generate_image_prompt(product: dict, accessory: str = "", pose: str = "", expression: str = "") -> str:
    """
    【楽天ROOM用】文字あり画像プロンプト（英語）
    手書き風テキスト3フレーズを画面に追加。
    保存ファイル名: YYYYMMDD.png
    """
    product_short = product['name'][:20]
    prompt = _base_image_prompt_text(product, accessory, pose, expression) + f"""
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
    generated = message.content[0].text.strip()
    acc_label = accessory or ""
    header = (
        f"━━ 選択パラメータ ━━\n"
        f"衣装/アクセサリー：{acc_label}\n"
        f"ポーズ：{pose}\n"
        f"表情：{expression}\n"
        f"━━━━━━━━━━━━━━━\n\n"
    )
    return header + generated


def generate_image_prompt_notxt(product: dict, accessory: str = "", pose: str = "", expression: str = "") -> str:
    """
    【動画用・通常mode】文字なし画像プロンプト（英語）
    Kling AIに読み込む素材画像として使用。
    保存ファイル名: YYYYMMDD_video.png
    """
    prompt = _base_image_prompt_text(product, accessory, pose, expression) + """
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
    generated = message.content[0].text.strip()
    acc_label = accessory or ""
    header = (
        f"━━ 選択パラメータ ━━\n"
        f"衣装/アクセサリー：{acc_label}\n"
        f"ポーズ：{pose}\n"
        f"表情：{expression}\n"
        f"━━━━━━━━━━━━━━━\n\n"
    )
    return header + generated


def generate_image_prompt_notxt_buzz(scene: dict) -> str:
    """
    【動画用・バズmode】文字なし画像プロンプト（英語）
    scene は _pick_buzz_scene() で取得したものを渡す。
    保存ファイル名: YYYYMMDD_buzz.png
    """
    prompt = _base_scene_text_buzz(scene) + """
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


# ── 商品カテゴリー別 Kling モーション定義（11カテゴリー）
PRODUCT_SCENE_MAP = {
    "sleep": {
        "label": "😴 寝姿（寝具・おくるみ）",
        "keywords": ["布団", "ベビー布団", "寝具", "マットレス", "おくるみ", "スリーパー", "まくら", "枕", "かけ布団", "ねんね", "寝袋", "ベビー寝具"],
        "motion_en": "tiny chest rises and falls with slow peaceful breathing, lips twitch with small sleepy murmurs 'nnn...nnn...', fingers curl and uncurl gently, eyelids flutter briefly then settle into deep blissful sleep, slow gentle zoom in on the serene sleeping face then softly pull back to reveal the full cozy bedding, seamless 8-second loop",
        "mood_en": "peaceful, serene, cozy, dreamy",
    },
    "feeding": {
        "label": "🍼 ミルク・食事（哺乳瓶・スタイ）",
        "keywords": ["哺乳瓶", "ミルク", "授乳", "離乳食", "スプーン", "食器", "ビブ", "スタイ", "エプロン", "マグ", "ストロー", "ベビーフード", "母乳"],
        "motion_en": "mouth makes gentle rhythmic sucking or tasting motions with pure contentment, tiny hands reach and grasp the item, eyelids grow heavier with milk-drunk satisfaction, small happy 'mnh...' sounds, head lolls blissfully into complete contentment",
        "mood_en": "content, milk-drunk, cozy, satisfied",
    },
    "clothing": {
        "label": "👕 服・ファッション（ロンパース・肌着）",
        "keywords": ["ロンパース", "肌着", "ベビー服", "カバーオール", "レッグウォーマー", "帽子", "ベビーキャップ", "ソックス", "靴下", "ベビーシューズ", "ツーウェイ", "パジャマ"],
        "motion_en": "lying on back showing off the adorable outfit, tiny legs kicking enthusiastically in pure happiness, arms waving with delight, full body wiggle showcasing every cute detail of the clothing, irresistible fashion moment",
        "mood_en": "playful, cheerful, fashion-forward, lively",
    },
    "toy": {
        "label": "🧸 おもちゃ（メリー・ガラガラ）",
        "keywords": ["おもちゃ", "プーメリー", "メリー", "ガラガラ", "知育", "積み木", "ベビージム", "ラトル", "ぬいぐるみ", "絵本", "テザー", "アクティビティ"],
        "motion_en": "eyes track the toy with laser-focused curiosity, arms reach and grasp with growing excitement, legs kick rhythmically with delight, tiny fingers explore and grip, building to an irresistible excited squeal of discovery",
        "mood_en": "curious, excited, playful, wonder-filled",
    },
    "bath": {
        "label": "🛁 お風呂（沐浴・バスグッズ）",
        "keywords": ["バス", "お風呂", "沐浴", "バスタブ", "バスタオル", "ベビーソープ", "シャンプー", "ガーゼ", "バスチェア", "ベビーバス"],
        "motion_en": "tiny hands splash gently in warm water, eyes wide with pure sensory delight, water droplets catching the light beautifully, whole body relaxing into the warmth with a content sigh, playful splashing loops perfectly",
        "mood_en": "delighted, refreshed, squeaky-clean, playful",
    },
    "carrier": {
        "label": "🤗 抱っこ紐・スリング",
        "keywords": ["抱っこ紐", "スリング", "ベビーキャリア", "ヒップシート", "おんぶ紐", "抱っこひも"],
        "motion_en": "snuggled safely and warmly against chest, tiny head nuzzling deeper into the cozy embrace, small fists curled near cheeks, breathing slowly and deeply with pure security, eyelids heavy with complete contentment",
        "mood_en": "secure, snuggly, peaceful, deeply loved",
    },
    "bouncer": {
        "label": "🪑 バウンサー・ハイローチェア",
        "keywords": ["バウンサー", "ハイローチェア", "ベビーチェア", "ロッキング", "スウィング", "電動ゆりかご", "バウンシング"],
        "motion_en": "tiny body gently rocks with the rhythmic motion, arms floating up and down with each sway, eyes going wide with delight then drooping with bliss, legs kicking lightly in rhythm, completely surrendering to the gentle bounce",
        "mood_en": "blissful, gently rocking, dreamy, content",
    },
    "teether": {
        "label": "🦷 歯固め・おしゃぶり",
        "keywords": ["歯固め", "おしゃぶり", "がらがら", "歯ぐずり", "ティーザー"],
        "motion_en": "tiny hands bring the teether to mouth with determined focus, vigorous happy chewing with wide satisfied eyes, drool glistens adorably in the soft light, triumphant expression of someone who has solved life's greatest challenge",
        "mood_en": "determined, satisfied, proudly drooly, victorious",
    },
    "stroller": {
        "label": "🚗 ベビーカー・チャイルドシート",
        "keywords": ["ベビーカー", "バギー", "チャイルドシート", "カーシート", "抱っこ布団", "ベビーシート"],
        "motion_en": "seated comfortably and safely, tiny head swiveling with bright curious eyes drinking in the world, arms reaching toward fascinating passing sights, expression cycling through pure wonder at everything in view",
        "mood_en": "curious, adventurous, wide-eyed, exploratory",
    },
    "skincare": {
        "label": "✨ スキンケア・ローション",
        "keywords": ["ベビークリーム", "ローション", "ベビーオイル", "保湿", "ベビーパウダー", "日焼け止め", "スキンケア", "ベビーローション"],
        "motion_en": "lying peacefully after gentle skincare routine, skin visibly glowing with softness, tiny arms stretched wide in total relaxation, small satisfied smile playing on lips, radiating freshness and utter contentment",
        "mood_en": "fresh, soft, glowing, utterly content",
    },
    "blanket": {
        "label": "🌸 ブランケット・ガーゼケット",
        "keywords": ["ブランケット", "毛布", "ガーゼケット", "タオルケット", "ガーゼ生地", "おひな巻き", "ひざかけ"],
        "motion_en": "wrapped snugly in the impossibly soft fabric, tiny face peeking out with huge wondering eyes, small fingers clutching the blanket edge, cheek nuzzling deeper into the softness, the ultimate expression of cozy baby bliss",
        "mood_en": "cozy, snuggly, soft, wrapped-in-warmth",
    },
}


def _detect_product_scene(product: dict) -> dict | None:
    """
    商品カテゴリーを検出してKlingシーン定義を返す。
    product["kling_scene_override"] が設定されている場合はそれを優先。
    """
    override = product.get("kling_scene_override")
    if override and override in PRODUCT_SCENE_MAP:
        return PRODUCT_SCENE_MAP[override]
    text = " ".join([
        product.get("name", ""),
        product.get("keyword", ""),
        product.get("catch_copy", ""),
    ])
    for data in PRODUCT_SCENE_MAP.values():
        if any(kw in text for kw in data["keywords"]):
            return data
    return None


def generate_kling_prompt(product: dict) -> str:
    """
    【通常mode】Kling AI（Image to Video）用動画プロンプト（英語）
    商品カテゴリーを検出して最適なシーン・動きに自動切り替え。
    """
    age_group = _get_age_group(MONTH_AGE)
    age_info = MOTION_BY_AGE_GROUP.get(age_group, MOTION_BY_AGE_GROUP["4-5"])

    product_scene = _detect_product_scene(product)
    if product_scene:
        motion_en    = product_scene["motion_en"]
        mood_en      = product_scene["mood_en"]
        primary_sound = product_scene["sound"]
    else:
        motion_en    = age_info["motion_en"]
        mood_en      = age_info["mood_en"]
        primary_sound = age_info["sounds"][0]

    prompt = f"""
せなっち（生後{MONTH_AGE}ヶ月）が商品「{product['name'][:40]}」を着ている・使っている静止画を
Kling AI（Image to Video）でInstagramリール バイラル動画にするプロンプトを英語で作成してください。

【バイラルコンセプト】
・せなっちが商品を着ている・使っている状態で、以下の動きを忠実に再現する
・主な動き：{motion_en}
・月齢({MONTH_AGE}ヶ月)の声のイメージ："{primary_sound}"
・「かわいすぎ」「これ何使ってるの？」と思わずコメントしたくなる構成
・動画が自然にループする構成（最後のフレームが最初につながる）
・動画尺：8秒（Kling AIの設定で8sを選択）

【Kling AIプロンプトのルール】
・外見の詳細描写は不要（入力画像から取得するため）
・Positive Promptは動き・カメラ・雰囲気を中心に60〜100語で記述
・Negative Promptは「NG要素」を15〜25語で列挙
・箇条書き不要・それぞれ1段落で出力

【カメラワーク・雰囲気】
・カメラ：slow gentle zoom in, then slowly pull back（8秒自然ループ用）
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


def generate_kling_prompt_buzz(scene: dict) -> str:
    """
    【バズmode】Kling AI（Image to Video）用動画プロンプト（英語）
    scene は _pick_buzz_scene() で取得したものを渡す（画像プロンプトと同じシーン）。
    Positive / Negative Prompt形式。
    """
    age_group = _get_age_group(MONTH_AGE)
    age_info = MOTION_BY_AGE_GROUP.get(age_group, MOTION_BY_AGE_GROUP["4-5"])
    primary_sound = age_info["sounds"][0]
    motion_en = scene.get("kling_motion", age_info["motion_en"])

    prompt = f"""
せなっち（生後{MONTH_AGE}ヶ月）の静止画を
Kling AI（Image to Video）でバイラル動画にするプロンプトを英語で作成してください。

【シーンの動き（画像と必ず一致させること）】
・主な動き：{motion_en}
・月齢({MONTH_AGE}ヶ月)の声のイメージ："{primary_sound}"
・「かわいすぎ」「友達に送りたい」という感情を引き出す
・動画尺：8秒（Kling AIの設定で8sを選択）
・8秒で笑いとかわいさを凝縮、自然にループしたくなる余韻を残す

【Kling AIプロンプトのルール】
・外見の詳細描写は不要（入力画像から取得するため）
・Positive Promptは動き・カメラ・雰囲気を中心に60〜100語で記述
・Negative Promptは「NG要素」を15〜25語で列挙
・箇条書き不要・それぞれ1段落で出力

【カメラワーク・雰囲気】
・カメラ：gentle slow zoom in, warm and intimate feel
・全体的な雰囲気：warm, cute, emotionally engaging, naturally viral

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
        acc = _pick_no_repeat(CUTE_ACCESSORIES, _pr_used_recent["accessory"], window=5)
        pose = _pick_no_repeat(PR_POSE_POOL, _pr_used_recent["pose"], window=5)
        expression = _pick_no_repeat(PR_EXPRESSION_POOL, _pr_used_recent["expression"], window=4)
        print(f"    アクセサリー: {acc}")
        print(f"    ポーズ: {pose[:50]}...")
        print(f"    表情: {expression[:50]}...")
        product["selected_costume"] = acc
        product["selected_pose"] = pose
        product["selected_expression"] = expression
        product["gpt_image_prompt"]       = generate_image_prompt(product, accessory=acc, pose=pose, expression=expression)
        product["gpt_image_prompt_notxt"] = generate_image_prompt_notxt(product, accessory=acc, pose=pose, expression=expression)
        product["video_prompt"]           = generate_kling_prompt(product)
        results.append(product)
        print("    ✅ プロンプト生成完了")
    print(f"\n✅ {len(results)} 件のプロンプトを生成しました")
    return results


def run_buzz() -> dict:
    """バズmode：商品なしの画像・動画プロンプトを生成して返す"""
    global MONTH_AGE
    MONTH_AGE = calc_month_age()
    print("画像・動画プロンプト生成エージェント 起動（バズmode）")
    scene = _pick_buzz_scene()
    print(f"  シーン: {scene['pose'][:50]}...")
    result = {
        "name": f"バズmode - せなっち生後{MONTH_AGE}ヶ月",
        "price": 0,
        "url": "",
        "affiliate_url": "",
        "item_code": "",
        "gpt_image_prompt": "",
        "gpt_image_prompt_notxt": generate_image_prompt_notxt_buzz(scene),
        "video_prompt": generate_kling_prompt_buzz(scene),
        "room_description": "",
        "score": 0,
        "is_buzz_mode": True,
    }
    print("  ✅ バズmodeプロンプト生成完了")
    return result
