"""
Baby Boo SNS管理 Webアプリ
Streamlit製。Streamlit Community Cloudで無料ホスティング。
"""
import os
import sys
import base64
import streamlit as st
from datetime import datetime, timedelta, timezone
from pathlib import Path
from PIL import Image

JST = timezone(timedelta(hours=9))


def _fmt_sched(iso_str: str, fallback: str = "") -> str:
    """Buffer APIのISO時刻文字列を "MM/DD HH:MM" に変換"""
    if not iso_str:
        return fallback
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.astimezone(JST).strftime("%m/%d %H:%M")
    except Exception:
        return iso_str or fallback


# ── Streamlit Cloud の secrets を環境変数に注入
if hasattr(st, "secrets"):
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ.setdefault(_k, _v)

sys.path.insert(0, str(Path(__file__).parent))

# ── アイコン画像をbase64に変換
_icon_path = Path(__file__).parent / "icon.png"
_icon_b64  = ""
_page_icon = "🍼"
if _icon_path.exists():
    with open(_icon_path, "rb") as _f:
        _icon_b64 = base64.b64encode(_f.read()).decode()
    _page_icon = Image.open(_icon_path)

# ── ページ設定
st.set_page_config(
    page_title="Baby Boo SNS管理",
    page_icon=_page_icon,
    layout="wide",
)

# ── カスタムCSS
st.markdown("""
<style>
.main .block-container {
    padding: 1rem 2rem 2rem;
    max-width: 960px;
    margin: 0 auto;
}
.baby-header {
    background: linear-gradient(135deg, #FFB6C1 0%, #FFDDE8 50%, #FFE8B0 100%);
    border-radius: 24px;
    padding: 1.8rem 1.5rem 1.4rem;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 6px 24px rgba(255, 107, 157, 0.25);
}
.baby-header .header-icon {
    width: 90px; height: 90px; border-radius: 50%;
    border: 4px solid white; box-shadow: 0 4px 16px rgba(255,107,157,0.4);
    object-fit: cover; margin-bottom: 0.6rem;
}
.baby-header h1 {
    color: #C2185B !important; font-size: 1.9rem !important;
    margin: 0 0 0.2rem !important; letter-spacing: 0.04em; font-weight: 800 !important;
}
.baby-header .date-text { color: #AD1457; font-size: 0.85rem; margin-bottom: 1rem; }
.baby-header .social-links {
    display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;
}
.baby-header .social-links a {
    display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px;
    border-radius: 20px; text-decoration: none; font-size: 0.85rem; font-weight: 700;
    color: white; transition: transform 0.15s, box-shadow 0.15s;
}
.baby-header .social-links a:hover {
    transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}
.social-ig  { background: linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888); box-shadow: 0 3px 10px rgba(220,39,67,0.35); }
.social-tiktok  { background: linear-gradient(135deg,#010101,#333); box-shadow: 0 3px 10px rgba(0,0,0,0.35); }
.social-rakuten { background: linear-gradient(135deg,#BF0000,#FF0000); box-shadow: 0 3px 10px rgba(191,0,0,0.3); }
.social-yt   { background: linear-gradient(135deg,#FF0000,#CC0000); box-shadow: 0 3px 10px rgba(255,0,0,0.3); }
.social-lit    { background: linear-gradient(135deg,#FF6B6B,#FF8E53); box-shadow: 0 3px 10px rgba(255,107,107,0.3); }
.social-buffer { background: linear-gradient(135deg,#168eea,#0063d1); box-shadow: 0 3px 10px rgba(22,142,234,0.35); }

/* モードカード */
.mode-card {
    border-radius: 18px; padding: 1.4rem 1rem; text-align: center; cursor: pointer;
    transition: transform 0.15s, box-shadow 0.15s;
    border: 3px solid transparent;
}
.mode-card:hover { transform: translateY(-3px); }
.mode-card-buzz   { background: linear-gradient(135deg,#FF6B9D,#FF8FAB); color: white; box-shadow: 0 4px 16px rgba(255,107,157,0.35); }
.mode-card-normal { background: linear-gradient(135deg,#42A5F5,#64B5F6); color: white; box-shadow: 0 4px 16px rgba(66,165,245,0.35); }
.mode-card-active { border: 3px solid white; box-shadow: 0 6px 24px rgba(0,0,0,0.25); transform: translateY(-3px); }
.mode-card-icon { font-size: 2.4rem; margin-bottom: 0.4rem; }
.mode-card-title { font-size: 1.1rem; font-weight: 800; margin-bottom: 0.2rem; }
.mode-card-desc  { font-size: 0.8rem; opacity: 0.9; }

/* ボタン */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF6B9D, #FF8FAB) !important;
    border: none !important; border-radius: 25px !important; color: white !important;
    font-weight: 700 !important; font-size: 1rem !important; padding: 0.6rem 1.2rem !important;
    box-shadow: 0 4px 12px rgba(255, 107, 157, 0.35) !important;
    transition: transform 0.15s, box-shadow 0.15s !important; width: 100% !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important; box-shadow: 0 6px 16px rgba(255, 107, 157, 0.45) !important;
}
.stButton > button[kind="secondary"] {
    border-radius: 20px !important; border: 2px solid #FF6B9D !important;
    color: #FF6B9D !important; font-weight: 600 !important;
}

/* タブ */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px; background: rgba(255,182,193,0.15); border-radius: 14px; padding: 5px; flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important; font-weight: 600 !important; color: #AD1457 !important;
    font-size: 0.9rem !important; padding: 6px 14px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FF6B9D, #FF8FAB) !important; color: white !important;
}

/* コードブロック */
.stCode { border-radius: 12px !important; border: 1px solid #FFB6C1 !important; font-size: 0.85rem !important; }

/* 通常modeカードを含む列のボタンを水色に（stColumn / column 両方対応） */
[data-testid="stColumn"]:has(.mode-card-normal) [data-testid="stBaseButton-primary"],
[data-testid="column"]:has(.mode-card-normal) [data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #42A5F5, #64B5F6) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(66,165,245,0.35) !important;
}
[data-testid="stColumn"]:has(.mode-card-normal) [data-testid="stBaseButton-primary"]:hover,
[data-testid="column"]:has(.mode-card-normal) [data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 6px 16px rgba(66,165,245,0.45) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stColumn"]:has(.mode-card-normal) [data-testid="stBaseButton-secondary"],
[data-testid="column"]:has(.mode-card-normal) [data-testid="stBaseButton-secondary"] {
    background: transparent !important;
    border: 2px solid #42A5F5 !important;
    color: #42A5F5 !important;
    box-shadow: none !important;
}

/* その他 */
.stAlert { border-radius: 12px !important; }
hr { border-color: #FFD6E7 !important; }
.stLinkButton > a { border-radius: 20px !important; font-weight: 600 !important; }
h2, h3, h4 { color: #C2185B !important; }

/* モバイルレスポンシブ */
@media screen and (max-width: 768px) {
    .main .block-container { padding: 0.5rem 0.6rem 1.5rem !important; }
    .baby-header { padding: 1.2rem 1rem 1rem !important; border-radius: 16px !important; }
    .baby-header .header-icon { width: 70px !important; height: 70px !important; }
    .baby-header h1 { font-size: 1.4rem !important; }
    .baby-header .social-links a { padding: 6px 12px !important; font-size: 0.78rem !important; }
    [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; }
    .stButton > button { font-size: 0.9rem !important; padding: 0.5rem 1rem !important; }
    .stTabs [data-baseweb="tab"] { font-size: 0.8rem !important; padding: 5px 8px !important; }
    h2, h3, h4 { font-size: 1rem !important; }
    .stCode { font-size: 0.78rem !important; }
    .mode-card { padding: 1rem 0.6rem !important; }
    .mode-card-icon { font-size: 1.8rem !important; }
    .mode-card-title { font-size: 0.95rem !important; }
}
@media screen and (max-width: 480px) {
    .baby-header h1 { font-size: 1.2rem !important; }
    .baby-header .social-links { gap: 6px !important; }
    .baby-header .social-links a { padding: 5px 10px !important; font-size: 0.75rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ── セッション状態の初期化
_defaults = {
    "generated":            False,
    "posts":                None,
    "scripts":              None,
    "all_products":         None,
    "content_mode":         "normal",
    "video_url":            None,
    "instagram_posted":     False,
    "tiktok_posted":        False,
    "youtube_posted":       False,
    "use_event":            False,
    "active_event":         None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── イベント検出
from utils.seasonal_events import get_upcoming_events as _get_events
from utils.baby_config import calc_month_age
_upcoming_events = _get_events(days_ahead=7)


# ──────────────────────────────────────────────────────
# サイドバー：今月の基準写真管理
# ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📸 今月の基準写真")
    try:
        from agents.image_agent import calc_month_age as _calc_age
        from utils.sheets_helper import get_reference_photo, set_reference_photo
        from utils.cloudinary_helper import upload_bytes as _upload_bytes
        _cur_month = _calc_age()
        _ref = get_reference_photo(_cur_month)

        if _ref:
            st.image(_ref["url"], use_container_width=True)
            st.caption(f"生後{_cur_month}ヶ月 / 登録日: {_ref['registered_at']}")
            st.success("✅ 基準写真登録済み")
        else:
            st.warning(f"⚠️ 生後{_cur_month}ヶ月の基準写真が未登録です")
            st.caption("下から写真を登録してください")

        st.markdown("---")
        _ref_file = st.file_uploader(
            "写真を登録・更新（PNG / JPG）",
            type=["png", "jpg", "jpeg"],
            key="ref_photo_uploader",
        )
        if _ref_file:
            st.image(_ref_file, caption="プレビュー", use_container_width=True)
            if st.button("📸 この写真を基準写真として登録", use_container_width=True, type="primary"):
                with st.spinner("Cloudinaryにアップロード中..."):
                    _ref_url = _upload_bytes(_ref_file.read(), resource_type="image")
                if _ref_url:
                    set_reference_photo(_cur_month, _ref_url)
                    st.success("✅ 登録しました！")
                    st.rerun()
                else:
                    st.error("アップロードに失敗しました")

        st.markdown("---")
        st.caption(
            "💡 月齢が上がったら新しい写真を登録してください。\n"
            "登録した写真を毎回 ChatGPT の参照画像として使うことで、\n"
            "せなっちの顔が一定に保たれます。"
        )
    except Exception as _e:
        st.caption(f"基準写真機能 読み込みエラー: {_e}")

    # ── Cloudinaryクリーンアップ
    st.markdown("---")
    with st.expander("🗑️ Cloudinaryクリーンアップ"):
        st.caption("古い動画・画像ファイルをまとめて削除します")
        _cl_days = st.number_input("削除対象の経過日数", min_value=7, max_value=365, value=30, step=7, key="cl_days")
        if st.button("🔍 古いファイルを確認", use_container_width=True, key="cl_check"):
            with st.spinner("確認中..."):
                try:
                    from utils.cloudinary_helper import list_assets as _list_cl
                    _old_all = (
                        _list_cl(days_old=_cl_days, resource_type="video") +
                        _list_cl(days_old=_cl_days, resource_type="image")
                    )
                    st.session_state["_cl_old"] = _old_all
                except Exception as _ce:
                    st.error(f"取得失敗: {_ce}")
                    st.session_state["_cl_old"] = []

        _old_cl = st.session_state.get("_cl_old")
        if _old_cl is not None:
            if not _old_cl:
                st.success("✅ 削除対象なし")
            else:
                _cl_mb = sum(f.get("bytes", 0) for f in _old_cl) / 1024 / 1024
                st.warning(f"⚠️ {len(_old_cl)}件 / {_cl_mb:.1f}MB が削除対象")
                for _of in _old_cl[:8]:
                    st.caption(f"・{_of['public_id'].split('/')[-1]} ({_of.get('bytes',0)//1024}KB) {_of.get('created_at','')[:10]}")
                if len(_old_cl) > 8:
                    st.caption(f"  他 {len(_old_cl)-8}件")
                if st.button("🗑️ 全て削除する", type="primary", use_container_width=True, key="cl_delete"):
                    _cl_ok = _cl_ng = 0
                    with st.spinner("削除中..."):
                        from utils.cloudinary_helper import delete_asset as _del_cl
                        for _of in _old_cl:
                            if _del_cl(_of["public_id"], _of["resource_type"]):
                                _cl_ok += 1
                            else:
                                _cl_ng += 1
                    st.session_state.pop("_cl_old", None)
                    _ng_msg = f"（{_cl_ng}件失敗）" if _cl_ng else ""
                    st.success(f"✅ {_cl_ok}件削除完了 {_ng_msg}")


def _reset_session():
    """再生成時にセッション状態をリセット"""
    for k, v in _defaults.items():
        st.session_state[k] = v
    # 編集状態もクリア
    for k in list(st.session_state.keys()):
        if k.startswith(("ed_", "ev_", "ebtn_", "dbtn_", "ta_edit_")):
            del st.session_state[k]


def _prompt_block(key: str, content: str, height: int = 160):
    """プロンプトブロック：コピーボタン付き表示（st.code）＋ 編集トグル"""
    display_val = st.session_state.get(f"ev_{key}", content) or ""
    is_editing  = st.session_state.get(f"ed_{key}", False)

    if not is_editing:
        st.code(display_val, language=None)
        if st.button("✏️ 編集する", key=f"ebtn_{key}"):
            st.session_state[f"ed_{key}"] = True
            st.session_state[f"ev_{key}"] = display_val
            st.rerun()
    else:
        new_val = st.text_area(
            "", value=display_val, height=height,
            key=f"ta_edit_{key}", label_visibility="collapsed",
        )
        if st.button("✅ 編集を確定する", key=f"dbtn_{key}"):
            st.session_state[f"ev_{key}"] = new_val
            st.session_state[f"ed_{key}"] = False
            st.rerun()


def _build_post_scripts(scripts: list) -> list:
    """投稿前にプロンプトタブの編集内容を scripts に反映して返す"""
    import copy
    result = copy.deepcopy(scripts)
    edit_map = [
        ("ev_ig_caption", "instagram"),
        ("ev_tt_caption", "tiktok"),
        ("ev_yt_title",   "youtube_title"),
        ("ev_yt_desc",    "youtube"),
        ("ev_yt_pin",     "pin_comment"),
    ]
    for s in result:
        caps = s.setdefault("captions", {})
        for ev_key, cap_key in edit_map:
            edited = st.session_state.get(ev_key)
            if edited is not None:
                caps[cap_key] = edited
    return result


# ── ヘッダー
today_str = datetime.now(tz=JST).strftime("%Y年%m月%d日")
icon_img  = f'<img src="data:image/png;base64,{_icon_b64}" class="header-icon">' if _icon_b64 else '<div style="font-size:4rem;">🍼</div>'

st.markdown(f"""
<div class="baby-header">
    {icon_img}
    <h1>Baby Boo SNS管理</h1>
    <div class="date-text">✨ {today_str} ✨</div>
    <div class="social-links">
        <a href="https://www.instagram.com/aibaby.jp/" target="_blank" class="social-ig">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="white">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
            </svg>
            @aibaby.jp
        </a>
        <a href="https://www.tiktok.com/@toshigo_papa_lab" target="_blank" class="social-tiktok">
            🎵 TikTok
        </a>
        <a href="https://room.rakuten.co.jp/room_3b6e1ab198/items" target="_blank" class="social-rakuten">
            🛍️ 楽天ROOM
        </a>
        <a href="https://www.youtube.com/channel/UCh-tGc4c1irK3IhYGiqOYYA" target="_blank" class="social-yt">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="white">
                <path d="M23.495 6.205a3.007 3.007 0 0 0-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 0 0 .527 6.205a31.247 31.247 0 0 0-.522 5.805 31.247 31.247 0 0 0 .522 5.783 3.007 3.007 0 0 0 2.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 0 0 2.088-2.088 31.247 31.247 0 0 0 .5-5.783 31.247 31.247 0 0 0-.5-5.805zM9.609 15.601V8.408l6.264 3.602z"/>
            </svg>
            YouTube
        </a>
        <a href="https://lit.link/baby_boo" target="_blank" class="social-lit">
            🔗 lit.link
        </a>
        <a href="https://publish.buffer.com/schedule?tab=sent" target="_blank" class="social-buffer">
            📅 Buffer
        </a>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION A: モード選択 ＋ コンテンツ生成（タブの外）
# ══════════════════════════════════════════════════════════════

_mode    = st.session_state.content_mode
_is_buzz = (_mode == "buzz")

if st.session_state.generated and st.session_state.posts:
    # ── 生成済みサマリー（保存・再生成ボタン付き）
    import json as _json_dl
    _p0 = st.session_state.posts[0]
    _col_info, _col_dl, _col_btn = st.columns([4, 1, 1])
    with _col_info:
        if _is_buzz:
            st.success("✅ **バズmode** 生成完了")
        else:
            st.success(f"✅ **通常mode** 生成完了 — {_p0['name'][:35]}　¥{_p0.get('price',0):,}")
    with _col_dl:
        _dl_banner = {
            "generated_at": datetime.now(tz=JST).isoformat(),
            "mode": _mode,
            "posts": st.session_state.posts,
            "scripts": st.session_state.scripts,
        }
        st.download_button(
            "📥 保存",
            data=_json_dl.dumps(_dl_banner, ensure_ascii=False, indent=2),
            file_name=f"babyboo_{datetime.now(tz=JST).strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
            help="リロードで消えます。JSONに保存しておくと安心です。",
        )
    with _col_btn:
        if st.button("🔄 再生成", use_container_width=True):
            _reset_session()
            st.rerun()

else:
    # ── STEP 1: モード選択カード
    st.markdown("""
    <div style="text-align:center; font-size:1.05rem; font-weight:700; color:#C2185B; margin-bottom:0.8rem;">
        🎬 今日はどちらのモードで投稿しますか？
    </div>
    """, unsafe_allow_html=True)

    _c_buzz, _c_normal = st.columns(2)
    with _c_buzz:
        _buzz_active_cls = "mode-card-active" if _is_buzz else ""
        st.markdown(f"""
        <div class="mode-card mode-card-buzz {_buzz_active_cls}">
            <div class="mode-card-icon">🎉</div>
            <div class="mode-card-title">バズmode</div>
            <div class="mode-card-desc">せなっちが踊る・ふざける<br>（商品なし）</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("バズmodeを選ぶ", use_container_width=True,
                     type="primary" if _is_buzz else "secondary", key="sel_buzz"):
            st.session_state.content_mode = "buzz"
            st.rerun()

    with _c_normal:
        _normal_active_cls = "mode-card-active" if not _is_buzz else ""
        st.markdown(f"""
        <div class="mode-card mode-card-normal {_normal_active_cls}">
            <div class="mode-card-icon">📦</div>
            <div class="mode-card-title">通常mode</div>
            <div class="mode-card-desc">楽天商品を紹介する動画<br>（商品あり）</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("通常modeを選ぶ", use_container_width=True,
                     type="primary" if not _is_buzz else "secondary", key="sel_normal"):
            st.session_state.content_mode = "normal"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── STEP 2: 入力フォーム（モードごと）
    with st.form("generation_form", clear_on_submit=False):

        _today_event = ""

        _kling_scene_key = None
        _event_for_gen = None
        _is_milestone = False
        if _is_buzz:
            _is_milestone = st.checkbox(
                "📅 今週の成長記録にする（週1マイルストーム投稿）",
                help="チェックすると「生後○ヶ月○週目」形式の成長記録キャプションが生成されます",
            )

            # ── イベントバナー
            if _upcoming_events:
                for _ev in _upcoming_events:
                    _days = _ev["days_until"]
                    if _days == 0:
                        _timing = "🎉 今日"
                    elif _days > 0:
                        _timing = f"あと{_days}日"
                    else:
                        _timing = f"{abs(_days)}日前"
                    st.markdown(f"""
<div style="background:linear-gradient(135deg,#FFF8E1,#FFF3CD); border-radius:12px;
            padding:0.9rem 1.2rem; margin:0.5rem 0; border:1px solid #FFD54F;">
    <span style="font-size:1.2rem;">{_ev['emoji']}</span>
    <strong style="color:#E65100;"> {_ev['label']}</strong>
    <span style="color:#F57F17; font-size:0.9rem;">（{_timing}）</span>
    <br><span style="font-size:0.82rem; color:#795548;">衣装・背景・キャプションをイベント仕様に自動切替できます</span>
</div>
""", unsafe_allow_html=True)
                    _use_ev = st.checkbox(
                        f"{_ev['emoji']} {_ev['label']}コンテンツとして生成する",
                        key=f"use_event_{_ev['key']}",
                    )
                    if _use_ev:
                        _event_for_gen = _ev
                        break
        else:
            from agents.image_agent import PRODUCT_SCENE_MAP as _psm
            _scene_options = {"🔍 自動検出（推奨）": None}
            _scene_options.update({v["label"]: k for k, v in _psm.items()})
            _scene_label = st.selectbox(
                "🎥 Klingシーン（自動検出 or 手動指定）",
                list(_scene_options.keys()),
                help="商品に合った赤ちゃんの動きを選択。自動検出で外れた場合に変更してください。",
            )
            _kling_scene_key = _scene_options[_scene_label]

        _submitted = st.form_submit_button(
            "🚀 コンテンツを生成する（約30〜60秒）",
            type="primary",
            use_container_width=True,
        )

    if _submitted:

        try:
            from agents import image_agent, instagram_agent, youtube_agent

            if not _is_buzz:
                from agents import rakuten_agent, analyzer_agent, writer_agent, quality_agent
                with st.status("🍼 コンテンツを生成中...", expanded=True) as status:
                    st.write("① 楽天で売れ筋商品を取得中...")
                    from utils.sheets_helper import (
                        get_product_history, get_recent_codes, upsert_product,
                        get_posted_affiliate_urls,
                    )
                    history       = get_product_history()
                    recent_codes  = get_recent_codes(history, days=7)
                    posted_urls   = get_posted_affiliate_urls()
                    products      = rakuten_agent.run()
                    try:
                        from agents import amazon_agent
                        if amazon_agent.is_configured():
                            st.write("   Amazon商品も取得中...")
                            amazon_products = amazon_agent.run(max_per_keyword=2)
                            products = products + amazon_products
                    except Exception:
                        pass
                    top3 = analyzer_agent.run(products, history=history, recent_codes=recent_codes, posted_urls=posted_urls)
                    if top3:
                        _t0 = top3[0]
                        _t0_code = _t0.get("item_code", "")
                        _t0_hist = history.get(_t0_code, {})
                        if _t0_hist.get("楽天ROOM投稿数", 0) > 0:
                            st.warning(f"⚠️ 「{_t0['name'][:25]}」は楽天ROOMに投稿済みです。他に候補がなかったため選ばれました。楽天ROOMへの重複投稿はできません。")
                        elif _t0_code in recent_codes:
                            st.warning(f"⚠️ 「{_t0['name'][:25]}」は直近7日以内に生成済みです。他に候補がなかったため同じ商品が選ばれました。")
                    all_scored = sorted(
                        [p for p in products if "score" in p],
                        key=lambda x: x["score"], reverse=True,
                    )
                    posts = writer_agent.run(top3)
                    st.write(f"   ✅ 商品選出完了：{posts[0]['name'][:30]}")

                    st.write("② 画像・動画プロンプトを生成中...")
                    if _kling_scene_key:
                        for _p in posts:
                            _p["kling_scene_override"] = _kling_scene_key
                    posts = image_agent.run(posts)
                    posts = quality_agent.run(posts)
                    st.write("   ✅ GPT Image 2 / Kling AIプロンプト完了")

                    st.write("③ Instagram・YouTube・TikTok キャプションを生成中...")
                    reel_script = instagram_agent.run(product=posts[0])
                    reel_script = youtube_agent.run(instagram_script=reel_script, product=posts[0])
                    st.write("   ✅ キャプション完了")

                    status.update(label="🎉 全コンテンツ生成完了！", state="complete")

                st.session_state.posts          = posts
                st.session_state.scripts        = [reel_script]
                st.session_state.all_products   = all_scored
                st.session_state.generated      = True
                st.session_state.tiktok_posted  = False
                upsert_product(posts[0])

            else:
                _ev_label = f" {_event_for_gen['emoji']} {_event_for_gen['label']}" if _event_for_gen else ""
                with st.status(f"🎉 バズmodeコンテンツを生成中...{_ev_label}", expanded=True) as status:
                    st.write(f"① バズmode 画像・動画プロンプトを生成中...{_ev_label}")
                    buzz_post = image_agent.run_buzz(event=_event_for_gen)
                    st.write("   ✅ プロンプト完了")

                    st.write("② Instagram・YouTube・TikTok キャプションを生成中...")
                    reel_script = instagram_agent.run_buzz(event=_event_for_gen, is_milestone=_is_milestone, buzz_post=buzz_post)
                    reel_script = youtube_agent.run(instagram_script=reel_script, product=None)
                    st.write("   ✅ キャプション完了")

                    status.update(label=f"🎉 バズmodeコンテンツ生成完了！{_ev_label}", state="complete")

                st.session_state.posts          = [buzz_post]
                st.session_state.scripts        = [reel_script]
                st.session_state.all_products   = []
                st.session_state.generated      = True
                st.session_state.tiktok_posted  = False

            st.balloons()
            st.rerun()

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            raise


# ══════════════════════════════════════════════════════════════
# SECTION B: タブ（生成後のみ表示）
# ══════════════════════════════════════════════════════════════
if not st.session_state.generated:
    st.stop()

st.markdown("<br>", unsafe_allow_html=True)

posts   = st.session_state.posts or []
scripts = st.session_state.scripts or []
today   = datetime.now(tz=JST).strftime("%Y%m%d")

if _is_buzz:
    tab_prompt, tab_post = st.tabs(["📋 プロンプト", "📤 投稿"])
    tab_analysis = tab_history = None
else:
    tab_prompt, tab_post, tab_analysis, tab_history = st.tabs(
        ["📋 プロンプト", "📤 投稿", "🔍 商品分析", "📊 商品履歴"]
    )


# ──────────────────────────────────────────────────────
# TAB: プロンプト
# ──────────────────────────────────────────────────────
with tab_prompt:
    if not posts:
        st.info("データがありません。再生成してください。")
        st.stop()

    p = posts[0]

    st.markdown("""
    <div style="background:#F3E5F5; border-radius:12px; padding:0.6rem 1rem;
                margin-bottom:1rem; border-left:4px solid #9C27B0;">
        <span style="font-weight:800; color:#6A1B9A; font-size:0.95rem;">
            📸 STEP 1 — ChatGPT・Kling AI 用プロンプト
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── 楽天ROOM紹介文（通常modeのみ）
    if not _is_buzz:
        st.markdown("#### 🛍️ 楽天ROOM 紹介文")
        _room_col1, _room_col2 = st.columns([3, 2])
        with _room_col1:
            st.caption("📱 楽天ROOMアプリから手動投稿してください")
            st.link_button("🏠 楽天ROOMを開く", "https://room.rakuten.co.jp/room_3b6e1ab198/items")
        with _room_col2:
            _room_key = f"room_posted_{p.get('item_code','')}"
            if st.session_state.get(_room_key):
                st.success("✅ 楽天ROOM投稿済み")
            else:
                if st.button("✅ 楽天ROOM 投稿済みにする", use_container_width=True):
                    from utils.sheets_helper import increment_count
                    increment_count(p.get("item_code", ""), "楽天ROOM投稿数")
                    st.session_state[_room_key] = True
                    st.rerun()
        _prompt_block("room_desc", p.get("room_description", ""), height=130)
        if p.get("affiliate_url"):
            st.caption(f"アフィリエイトURL: `{p['affiliate_url']}`")
        st.divider()

        # ── GPT Image プロンプト（文字あり・楽天ROOM用）
        st.markdown("#### 🖼️ GPT Image プロンプト（文字あり・楽天ROOM用）")
        st.caption(f"せなっち写真＋商品写真を添付 → `{today}.png` として保存")
        st.link_button("🤖 ChatGPTを開く", "https://chatgpt.com")
        _prompt_block("gpt_img_txt", p.get("gpt_image_prompt", ""), height=220)
        st.divider()

    # ── GPT Image プロンプト（動画用 / バズmode）
    if _is_buzz:
        st.markdown("#### 🎉 GPT Image プロンプト（バズmode・コスチューム）")
        st.markdown("""
        <div style="background:#FFF8E7; border-radius:10px; padding:0.7rem 1rem;
                    border:1px solid #FFCC80; font-size:0.84rem; margin-bottom:0.5rem;">
            📎 <b>ChatGPTへ添付する画像は1枚だけ</b>　— せなっちの写真のみ<br>
            コスチューム・背景はプロンプトが自動生成します。生成のたびにコスチュームが変わります。
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"生成後 `{today}_buzz.png` として保存 → Kling AIで動画化")
    else:
        st.markdown("#### 🎬 GPT Image プロンプト（文字なし・動画用）")
        st.caption(f"せなっち写真＋商品写真を添付 → `{today}_video.png` として保存 → Kling AIで動画化")

    # ── 基準写真リマインダー
    try:
        from utils.sheets_helper import get_reference_photo as _get_ref
        from agents.image_agent import calc_month_age as _ca
        _rm = _get_ref(_ca())
        if _rm:
            _rc1, _rc2 = st.columns([1, 3])
            with _rc1:
                st.image(_rm["url"], use_container_width=True)
            with _rc2:
                st.markdown(
                    f"<div style='background:#E8F5E9; border-radius:10px; padding:0.6rem 0.9rem;"
                    f"border:1px solid #A5D6A7; font-size:0.83rem;'>"
                    f"📎 <b>今月の基準写真（左）をChatGPTに添付してください</b><br>"
                    f"<span style='color:#555;'>毎回この写真を使うことでせなっちの顔が一定に保たれます</span><br>"
                    f"<a href='{_rm['url']}' target='_blank' style='font-size:0.78rem;'>🔗 Cloudinaryで開く</a>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("📸 サイドバーから今月の基準写真を登録すると、ここにリマインダーが表示されます。")
    except Exception:
        pass

    st.link_button("🤖 ChatGPTを開く ", "https://chatgpt.com")
    _prompt_block("gpt_img_notxt", p.get("gpt_image_prompt_notxt", ""), height=220)
    st.divider()

    # ── Kling AI 動画プロンプト
    st.markdown("#### 🎥 Kling AI 動画プロンプト")
    st.caption("上記で生成した画像をKling AIにアップロード → Image to Video で使用")
    st.link_button("🎬 Kling AIを開く", "https://klingai.com")
    _prompt_block("video_prompt", p.get("video_prompt", ""), height=220)

    if scripts:
        for s in scripts:
            if s.get("type") != "reel":
                continue
            captions = s.get("captions", {})

            st.markdown("""
            <div style="background:#E3F2FD; border-radius:12px; padding:0.6rem 1rem;
                        margin: 1.5rem 0 1rem; border-left:4px solid #1976D2;">
                <span style="font-weight:800; color:#0D47A1; font-size:0.95rem;">
                    📝 STEP 2 — SNSキャプション
                </span>
            </div>
            """, unsafe_allow_html=True)

            # ── Hook / BGM情報
            _hook = s.get("hook", "")
            _dm   = s.get("dm_trigger", "")
            _bgm  = s.get("bgm_style", "")
            if _hook or _dm or _bgm:
                with st.expander("🎬 動画設計メモ（Hook / DMシェア / BGM）", expanded=False):
                    if _hook: st.markdown(f"**Hook（冒頭0〜2秒）：** {_hook}")
                    if _dm:   st.markdown(f"**DMシェア設計：** {_dm}")
                    if _bgm:  st.markdown(f"**AI推奨BGM：** {_bgm}")
                    st.markdown("""
                    <div style="background:linear-gradient(135deg,#F3E5F5,#EDE7F6); border-radius:10px;
                                padding:0.8rem 1rem; border:1px solid #CE93D8; font-size:0.82rem;">
                    🥇 <b>LoFi / Nostalgic系</b>（最推奨）— 赤ちゃんスローモーションに最適<br>
                    🥈 <b>Warm Strings / Gentle Piano</b> — 育児日常記録に定番（60〜90 BPM）<br>
                    🥉 <b>K-Pop キャッチー系</b> — ポジティブ・バズ動画向け
                    </div>
                    """, unsafe_allow_html=True)
                    _lc1, _lc2 = st.columns(2)
                    with _lc1: st.link_button("📊 Buffer トレンド音源", "https://buffer.com/resources/trending-audio-instagram/")
                    with _lc2: st.link_button("📊 Later トレンド情報", "https://later.com/blog/instagram-reels-trends/")

            # ── Instagram キャプション
            st.markdown("#### 📱 Instagram Reel キャプション")
            _prompt_block("ig_caption", captions.get("instagram", ""), height=160)
            st.divider()

            # ── TikTok キャプション
            _tt_caption = captions.get("tiktok", "")
            st.markdown("#### 🎵 TikTok キャプション")
            st.caption("冒頭30文字にキーワード集中・ハッシュタグ5個固定")
            if _tt_caption:
                _prompt_block("tt_caption", _tt_caption, height=140)
            else:
                st.warning("TikTokキャプションが生成されませんでした。再生成してください。")
            st.divider()

            # ── YouTube Shorts
            st.markdown("#### ▶️ YouTube Shorts")
            _yt_title    = captions.get("youtube_title", "")
            _yt_desc     = captions.get("youtube", "")
            _pin_comment = captions.get("pin_comment", "")
            if _yt_title:
                st.caption("タイトル")
                _prompt_block("yt_title", _yt_title, height=70)
                st.caption("説明文（#Shorts・ハッシュタグ含む）")
                _prompt_block("yt_desc", _yt_desc, height=160)
                if _pin_comment:
                    st.caption("ピン留めコメント")
                    _prompt_block("yt_pin", _pin_comment, height=80)
            else:
                st.info("再生成するとYouTube Shortsコンテンツが追加されます")


# ──────────────────────────────────────────────────────
# TAB: 投稿
# ──────────────────────────────────────────────────────
with tab_post:
    st.markdown("### 📤 投稿")

    _now = datetime.now(tz=JST)
    _t3  = (_now + timedelta(minutes=3)).strftime("%H:%M")
    _t48 = (_now + timedelta(minutes=48)).strftime("%H:%M")
    # ① 動画アップロード
    st.markdown("""
    <div style="background:linear-gradient(135deg,#F3E5F5,#EDE7F6); border-radius:16px;
                padding:1.2rem 1.4rem; margin-bottom:0.8rem; border:1px solid #CE93D8;">
        <div style="font-size:0.75rem; font-weight:700; color:#AB47BC; letter-spacing:0.08em; margin-bottom:0.2rem;">STEP 1</div>
        <div style="font-size:1.05rem; font-weight:800; color:#6A1B9A; margin-bottom:0.3rem;">☁️ 動画をアップロード</div>
        <div style="font-size:0.85rem; color:#7B1FA2;">Kling AIで生成した動画（MP4）をCloudinaryにアップロードします</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.video_url:
        st.success("✅ 動画アップロード済み")
        st.video(st.session_state.video_url)
        if st.button("🔄 別の動画に差し替える（キャプションは維持）", use_container_width=True):
            st.session_state.video_url = None
            st.session_state.instagram_posted = False
            st.session_state.youtube_posted  = False
            st.session_state.tiktok_posted   = False
            st.rerun()
    else:
        video_file = st.file_uploader("動画ファイルを選択（MP4 / MOV）", type=["mp4", "mov"], key="vid_uploader")
        if video_file:
            st.video(video_file)
            if st.button("☁️ Cloudinaryにアップロード", type="primary", use_container_width=True):
                with st.spinner("アップロード中..."):
                    from utils.cloudinary_helper import upload_bytes
                    url = upload_bytes(video_file.read(), resource_type="video")
                if url:
                    st.session_state.video_url = url
                    st.success("✅ アップロード完了！")
                    st.rerun()
                else:
                    st.error("アップロードに失敗しました。Cloudinaryの設定を確認してください。")

    st.divider()

    # ② Instagram Reel
    st.markdown("""
    <div style="background:linear-gradient(135deg,#FFF0F8,#FFE8EF); border-radius:16px;
                padding:1.2rem 1.4rem; margin-bottom:0.8rem; border:1px solid #FFB6C1;">
        <div style="font-size:0.75rem; font-weight:700; color:#F06292; letter-spacing:0.08em; margin-bottom:0.2rem;">STEP 2</div>
        <div style="font-size:1.05rem; font-weight:800; color:#C2185B; margin-bottom:0.3rem;">📱 Instagram Reel に投稿</div>
        <div style="font-size:0.85rem; color:#AD1457;">STEP 1 完了後に有効になります</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.instagram_posted:
        _ig_disp = _fmt_sched(st.session_state.get("ig_scheduled_at", ""), f"{_t3}頃")
        st.success("✅ Instagram Reel 予約完了")
        _igc1, _igc2 = st.columns(2)
        with _igc1: st.info(f"📅 投稿予定: {_ig_disp}")
        with _igc2: st.link_button("📋 Bufferで確認", "https://buffer.com")
    elif not st.session_state.video_url:
        st.button("📱 Instagram Reel に投稿する", use_container_width=True, disabled=True)
        st.caption("⚠️ 先に動画をアップロードしてください")
    else:
        if st.button("📱 Instagram Reel に投稿する", type="primary", use_container_width=True):
            with st.spinner("Bufferに予約中..."):
                from agents.buffer_agent import run as buf_run
                results = buf_run(_build_post_scripts(scripts), video_url=st.session_state.video_url, platforms=["instagram"])
            ok_ig = any(r.get("buffer_posts", {}).get("instagram", {}).get("success") for r in results)
            if ok_ig:
                st.session_state.instagram_posted = True
                _ic = (posts or [{}])[0].get("item_code", "")
                if _ic:
                    from utils.sheets_helper import increment_count as _inc
                    _inc(_ic, "Instagram投稿数")
                _ig_res = next((r.get("buffer_posts", {}).get("instagram", {}) for r in results if r.get("buffer_posts", {}).get("instagram", {}).get("success")), {})
                st.session_state["ig_scheduled_at"] = _ig_res.get("scheduled_at", "")
                st.rerun()
            else:
                errs = [r.get("buffer_posts", {}).get("instagram", {}).get("error", "") for r in results]
                st.error(f"❌ Instagram 投稿失敗: {' | '.join(e for e in errs if e) or '不明なエラー'}")
                st.link_button("⚙️ Bufferダッシュボードを確認", "https://buffer.com")

    st.divider()

    # ③ YouTube Shorts
    st.markdown("""
    <div style="background:linear-gradient(135deg,#FFF3E0,#FFE0B2); border-radius:16px;
                padding:1.2rem 1.4rem; margin-bottom:0.8rem; border:1px solid #FFB74D;">
        <div style="font-size:0.75rem; font-weight:700; color:#FFA726; letter-spacing:0.08em; margin-bottom:0.2rem;">STEP 3</div>
        <div style="font-size:1.05rem; font-weight:800; color:#E65100; margin-bottom:0.3rem;">▶️ YouTube Shorts に投稿</div>
        <div style="font-size:0.85rem; color:#BF360C;">STEP 1 完了後に有効になります / Bufferにチャンネル連携済みが前提</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.youtube_posted:
        _yt_disp = _fmt_sched(st.session_state.get("yt_scheduled_at", ""), f"{_t3}頃")
        st.success("✅ YouTube Shorts 予約完了")
        _ytc1, _ytc2 = st.columns(2)
        with _ytc1: st.info(f"📅 投稿予定: {_yt_disp}")
        with _ytc2: st.link_button("📋 Bufferで確認", "https://buffer.com")
    elif not st.session_state.video_url:
        st.button("▶️ YouTube Shorts に投稿する", use_container_width=True, disabled=True)
        st.caption("⚠️ 先に動画をアップロードしてください")
    else:
        _yt_reel = next((s for s in scripts if s.get("type") == "reel"), None)
        _yt_title_preview = (_yt_reel or {}).get("captions", {}).get("youtube_title", "（タイトル未生成）")
        st.caption(f"タイトル: {_yt_title_preview}")
        if st.button("▶️ YouTube Shorts に投稿する", type="primary", use_container_width=True):
            with st.spinner("Bufferに予約中..."):
                from agents.buffer_agent import run as buf_run_yt
                results_yt = buf_run_yt(_build_post_scripts(scripts), video_url=st.session_state.video_url, platforms=["youtube"])
            ok_yt = any(r.get("buffer_posts", {}).get("youtube", {}).get("success") for r in results_yt)
            if ok_yt:
                st.session_state.youtube_posted = True
                _yt_ic = (posts or [{}])[0].get("item_code", "")
                if _yt_ic:
                    from utils.sheets_helper import increment_count as _inc_yt
                    _inc_yt(_yt_ic, "YouTube投稿数")
                _yt_res = next((r.get("buffer_posts", {}).get("youtube", {}) for r in results_yt if r.get("buffer_posts", {}).get("youtube", {}).get("success")), {})
                st.session_state["yt_scheduled_at"] = _yt_res.get("scheduled_at", "")
                st.rerun()
            else:
                errs_yt = [r.get("buffer_posts", {}).get("youtube", {}).get("error", "") for r in results_yt]
                st.error(f"❌ YouTube 投稿失敗: {' | '.join(e for e in errs_yt if e) or '不明なエラー'}")
                st.link_button("⚙️ Bufferダッシュボードを確認", "https://buffer.com")

    # ③-b YouTube ピン留めコメント自動投稿
    _pin_comment_text = next(
        (s.get("captions", {}).get("pin_comment", "") for s in scripts if s.get("type") == "reel"), ""
    )
    if _pin_comment_text:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#FFF8E1,#FFF3CD); border-radius:14px;
                    padding:1rem 1.2rem; margin-top:0.6rem; border:1px solid #FFE082;">
            <div style="font-size:0.95rem; font-weight:800; color:#F57F17; margin-bottom:0.2rem;">
                📌 ピン留めコメント自動投稿
            </div>
            <div style="font-size:0.8rem; color:#F9A825;">
                動画公開後にコメント投稿 → YouTube Studioで手動ピン留めしてください
            </div>
        </div>
        """, unsafe_allow_html=True)

        _yt_video_url = st.text_input(
            "YouTube動画URLまたはビデオID",
            placeholder="https://youtube.com/watch?v=XXXXXXXX  または  XXXXXXXX",
            key="yt_comment_video_url"
        )
        st.caption(f"投稿するコメント: {_pin_comment_text[:80]}…" if len(_pin_comment_text) > 80 else f"投稿するコメント: {_pin_comment_text}")

        if st.session_state.get("yt_comment_posted"):
            st.success("✅ コメント投稿済み ─ YouTube Studioでピン留めしてください")
            st.link_button("📌 YouTube Studio を開く", "https://studio.youtube.com")
        else:
            _can_comment = bool(_yt_video_url and _yt_video_url.strip())
            if st.button("💬 コメントを投稿する", type="primary", use_container_width=True, disabled=not _can_comment):
                with st.spinner("YouTube APIにコメント投稿中..."):
                    from agents.youtube_comment_agent import post_comment as _post_yt_comment
                    _comment_result = _post_yt_comment(_yt_video_url.strip(), _pin_comment_text)
                if _comment_result.get("success"):
                    st.session_state["yt_comment_posted"] = True
                    st.success("✅ コメント投稿完了！YouTube Studioでピン留めしてください")
                    st.link_button("📌 YouTube Studio を開く", "https://studio.youtube.com")
                    st.rerun()
                else:
                    st.error(f"失敗: {_comment_result.get('error', '不明なエラー')}")
            if not _can_comment:
                st.caption("⚠️ 動画URLを入力してください")

    st.divider()

    # ④ TikTok
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a1a2e,#2d2d44); border-radius:16px;
                padding:1.2rem 1.4rem; margin-bottom:0.8rem; border:1px solid #444;">
        <div style="font-size:0.75rem; font-weight:700; color:#aaa; letter-spacing:0.08em; margin-bottom:0.2rem;">STEP 4</div>
        <div style="font-size:1.05rem; font-weight:800; color:#fff; margin-bottom:0.3rem;">🎵 TikTok に投稿</div>
        <div style="font-size:0.85rem; color:#aaa;">TikTok Studio から直接投稿してください（AI開示ラベル対応のため）</div>
    </div>
    """, unsafe_allow_html=True)

    _tt_caption_post = st.session_state.get("ev_tt_caption", "")
    if not _tt_caption_post:
        for _s in (scripts or []):
            if _s.get("type") == "reel":
                _tt_caption_post = _s.get("captions", {}).get("tiktok", "")
                break

    st.info(
        "⚠️ Buffer経由のTikTok投稿はAI生成コンテンツの開示ラベルが付かず、削除される場合があります。\n\n"
        "**手順：**\n"
        "1. 下のキャプションをコピー\n"
        "2. Cloudinaryの動画URLを開いてローカルに保存\n"
        "3. TikTok Studio でアップロード → 「AIによって生成または編集されたコンテンツ」をON → スケジュール投稿"
    )
    st.link_button("🎵 TikTok Studio を開く", "https://www.tiktok.com/tiktokstudio")

    if _tt_caption_post:
        st.caption("📋 TikTok キャプション（コピーして使用）")
        st.code(_tt_caption_post, language=None)


# ──────────────────────────────────────────────────────
# TAB: 商品分析（通常modeのみ）
# ──────────────────────────────────────────────────────
if tab_analysis:
    with tab_analysis:
        st.markdown("### 🔍 商品分析レポート")

        all_p = st.session_state.all_products or []
        if not all_p:
            st.info("💡 通常modeで生成すると商品分析が表示されます。")
        else:
            import plotly.express as px
            import plotly.graph_objects as go
            import pandas as pd

            top3_codes = {p.get("item_code", "") for p in posts if p.get("item_code")}
            selected_p = posts[0] if posts else None

            st.markdown("""
            <div style="background:linear-gradient(135deg,#FFF0F8,#FFE8EF); border-radius:14px;
                        padding:1rem 1.2rem; margin-bottom:1rem; border:1px solid #FFB6C1; font-size:0.88rem;">
                📐 <b>スコア計算式</b>：レビュー数 × 0.6 ＋ レビュー評価 × 10 × 0.4
            </div>
            """, unsafe_allow_html=True)

            df = pd.DataFrame(all_p)
            df["選出"] = df["item_code"].apply(lambda c: "🏆 選出" if c in top3_codes else "その他")
            df["商品名（短）"] = df["name"].str[:22] + df["name"].str[22:].apply(lambda x: "…" if x else "")
            df["スコア"] = df["score"].astype(float)
            df["レビュー数"] = df["review_count"].astype(int)
            df["レビュー評価"] = df["review_average"].astype(float)
            df["価格"] = df["price"].astype(int)
            COLOR_MAP = {"🏆 選出": "#FF6B9D", "その他": "#FFAECB"}

            st.markdown("#### 📊 スコアランキング（上位15件）")
            top15 = df.head(15).iloc[::-1].copy()
            fig_bar = px.bar(top15, x="スコア", y="商品名（短）", orientation="h", color="選出",
                             color_discrete_map=COLOR_MAP,
                             hover_data={"レビュー数": True, "レビュー評価": True, "価格": True, "選出": False},
                             height=max(320, len(top15) * 28))
            fig_bar.update_layout(
                plot_bgcolor="rgba(255,245,248,0.6)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="sans-serif", size=12, color="#3D2B3D"), legend_title_text="",
                margin=dict(l=10, r=20, t=10, b=10),
                xaxis=dict(gridcolor="#FFD6E7", title="スコア"), yaxis=dict(title=""),
            )
            fig_bar.update_traces(marker_line_width=0)
            st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("#### 🫧 レビュー数 × レビュー評価")
            fig_scatter = px.scatter(df, x="レビュー数", y="レビュー評価", size="スコア", color="選出",
                                     color_discrete_map=COLOR_MAP, hover_name="商品名（短）",
                                     hover_data={"スコア": ":.1f", "価格": True, "選出": False},
                                     size_max=40, height=380)
            fig_scatter.update_layout(
                plot_bgcolor="rgba(255,245,248,0.6)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="sans-serif", size=12, color="#3D2B3D"), legend_title_text="",
                margin=dict(l=10, r=20, t=10, b=10),
                xaxis=dict(gridcolor="#FFD6E7", title="レビュー数（件）"),
                yaxis=dict(gridcolor="#FFD6E7", title="レビュー評価（5点満点）"),
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

            if selected_p:
                st.markdown("#### 🏆 選出商品のスコア内訳")
                rc = selected_p.get("review_count", 0)
                ra = selected_p.get("review_average", 0.0)
                s_review = round(rc * 0.6, 1)
                s_rating = round(ra * 10 * 0.4, 1)
                total    = round(s_review + s_rating, 1)
                c1, c2, c3 = st.columns(3)
                c1.metric("レビュー数スコア", f"{s_review}", f"({rc:,}件 × 0.6)")
                c2.metric("評価スコア",       f"{s_rating}", f"({ra} × 10 × 0.4)")
                c3.metric("合計スコア",       f"{total}")

            st.divider()
            st.markdown("#### 📋 全商品一覧")
            st.caption(f"楽天APIで取得した {len(all_p)} 件をスコア順に表示")
            for rank, p_item in enumerate(all_p, 1):
                is_selected = p_item.get("item_code", "") in top3_codes and p_item.get("item_code", "")
                badge = "🏆 選出" if is_selected else ""
                score_color = "#FF6B9D" if rank <= 3 else "#888"
                with st.container():
                    col_rank, col_info, col_score = st.columns([1, 6, 2])
                    with col_rank:
                        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
                        st.markdown(f'<div style="font-size:1.4rem; text-align:center; padding-top:0.5rem;">{medal}</div>', unsafe_allow_html=True)
                    with col_info:
                        name_display = p_item["name"][:55] + ("…" if len(p_item["name"]) > 55 else "")
                        st.markdown(f'<div style="font-weight:700; font-size:0.95rem; color:#3D2B3D;">{name_display} {badge}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="font-size:0.82rem; color:#888;">🔑 {p_item.get("keyword","—")} ｜ 🏪 {p_item.get("shop_name","")[:20]}</div>', unsafe_allow_html=True)
                        url = p_item.get("affiliate_url") or p_item.get("url", "")
                        if url:
                            st.markdown(f'<a href="{url}" target="_blank" style="font-size:0.78rem; color:#FF6B9D;">🔗 商品を見る</a>', unsafe_allow_html=True)
                    with col_score:
                        st.markdown(f'<div style="text-align:center;"><div style="font-size:1.3rem; font-weight:800; color:{score_color};">{p_item["score"]:.1f}</div><div style="font-size:0.75rem; color:#888;">スコア</div><div style="font-size:0.85rem; font-weight:700; color:#3D2B3D;">¥{p_item["price"]:,}</div><div style="font-size:0.75rem; color:#888;">⭐ {p_item.get("review_average",0)} ({p_item.get("review_count",0):,}件)</div></div>', unsafe_allow_html=True)
                st.markdown('<hr style="border-color:#FFD6E7; margin:0.4rem 0;">', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
# TAB: 商品履歴（通常modeのみ）
# ──────────────────────────────────────────────────────
if tab_history:
    with tab_history:
        st.markdown("### 📊 商品履歴")
        st.caption("商品ごとの生成回数・各プラットフォーム投稿数を管理します（生成3回でその商品はスキップ）")

        # ── スプレッドシート整理ボタン
        with st.expander("🛠️ スプレッドシートのメンテナンス"):
            st.caption("""
現在の仕様（HEADERS）に合わせてスプレッドシートを整理します。
- 不要な列（Threads投稿数 等）を削除
- 不足している列を追加
- 列の順番を統一
- **既存データは保持されます**
            """)
            if st.button("🧹 スプレッドシートを整理する", type="primary", use_container_width=True):
                with st.spinner("スプレッドシートを整理中..."):
                    from utils.sheets_helper import cleanup_sheet
                    result = cleanup_sheet()
                if "error" in result:
                    st.error(f"❌ エラー: {result['error']}")
                else:
                    st.success(f"✅ 整理完了（{result['migrated_rows']}行を移行）")
                    if result["dropped_columns"]:
                        st.info(f"🗑️ 削除した列: {', '.join(result['dropped_columns'])}")
                    if result["added_columns"]:
                        st.info(f"➕ 追加した列: {', '.join(result['added_columns'])}")
                    if not result["dropped_columns"] and not result["added_columns"]:
                        st.info("すでに最新の仕様になっていました")

        st.divider()

        if st.button("🔍 履歴を読み込む", use_container_width=True):
            with st.spinner("Google Sheetsから取得中..."):
                from utils.sheets_helper import get_history
                _hist_df = get_history()

            if _hist_df is None:
                st.error("Google Sheetsの設定を確認してください（GOOGLE_CREDENTIALS_JSON / GOOGLE_SHEETS_ID）")
            elif _hist_df.empty:
                st.info("📭 まだ投稿履歴がありません。")
            else:
                try:
                    s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)
                    with s_col1: st.metric("商品数", len(_hist_df))
                    with s_col2: st.metric("楽天ROOM投稿", int(_hist_df["楽天ROOM投稿数"].astype(int).sum()) if "楽天ROOM投稿数" in _hist_df.columns else "-")
                    with s_col3: st.metric("Instagram投稿", int(_hist_df["Instagram投稿数"].astype(int).sum()) if "Instagram投稿数" in _hist_df.columns else "-")
                    with s_col4: st.metric("TikTok投稿", int(_hist_df["TikTok投稿数"].astype(int).sum()) if "TikTok投稿数" in _hist_df.columns else "-")
                    with s_col5: st.metric("YouTube投稿", int(_hist_df["YouTube投稿数"].astype(int).sum()) if "YouTube投稿数" in _hist_df.columns else "-")
                except Exception:
                    pass

                st.divider()
                display_cols = [c for c in ["最終生成日", "商品名", "価格", "キーワード", "生成回数", "楽天ROOM投稿数", "Instagram投稿数", "TikTok投稿数", "YouTube投稿数"] if c in _hist_df.columns]
                st.dataframe(_hist_df[display_cols] if display_cols else _hist_df, use_container_width=True, hide_index=True)
                st.caption(f"合計 {len(_hist_df)} 商品")


