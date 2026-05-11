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

# ── Streamlit Cloud の secrets を環境変数に注入
if hasattr(st, "secrets"):
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ.setdefault(_k, _v)

sys.path.insert(0, str(Path(__file__).parent))

# ── アイコン画像をbase64に変換（ヘッダー埋め込み用）
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

# ── カスタムCSS（ベビーテーマ + レスポンシブ）
st.markdown("""
<style>
/* ── 全体 ── */
.main .block-container {
    padding: 1rem 2rem 2rem;
    max-width: 960px;
    margin: 0 auto;
}

/* ── ヘッダー ── */
.baby-header {
    background: linear-gradient(135deg, #FFB6C1 0%, #FFDDE8 50%, #FFE8B0 100%);
    border-radius: 24px;
    padding: 1.8rem 1.5rem 1.4rem;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 6px 24px rgba(255, 107, 157, 0.25);
}
.baby-header .header-icon {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    border: 4px solid white;
    box-shadow: 0 4px 16px rgba(255,107,157,0.4);
    object-fit: cover;
    margin-bottom: 0.6rem;
}
.baby-header h1 {
    color: #C2185B !important;
    font-size: 1.9rem !important;
    margin: 0 0 0.2rem !important;
    letter-spacing: 0.04em;
    font-weight: 800 !important;
}
.baby-header .date-text {
    color: #AD1457;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}
.baby-header .social-links {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
}
.baby-header .social-links a {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 20px;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 700;
    color: white;
    transition: transform 0.15s, box-shadow 0.15s;
}
.baby-header .social-links a:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}
.social-ig {
    background: linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);
    box-shadow: 0 3px 10px rgba(220,39,67,0.35);
}
.social-threads {
    background: #000;
    box-shadow: 0 3px 10px rgba(0,0,0,0.25);
}
.social-rakuten {
    background: linear-gradient(135deg,#BF0000,#FF0000);
    box-shadow: 0 3px 10px rgba(191,0,0,0.3);
}

/* ── ボタン ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF6B9D, #FF8FAB) !important;
    border: none !important;
    border-radius: 25px !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.6rem 1.2rem !important;
    box-shadow: 0 4px 12px rgba(255, 107, 157, 0.35) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    width: 100% !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(255, 107, 157, 0.45) !important;
}
.stButton > button[kind="secondary"] {
    border-radius: 20px !important;
    border: 2px solid #FF6B9D !important;
    color: #FF6B9D !important;
    font-weight: 600 !important;
}

/* ── タブ ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(255,182,193,0.15);
    border-radius: 14px;
    padding: 5px;
    flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    color: #AD1457 !important;
    font-size: 0.9rem !important;
    padding: 6px 12px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FF6B9D, #FF8FAB) !important;
    color: white !important;
}

/* ── コードブロック（コピー用） ── */
.stCode {
    border-radius: 12px !important;
    border: 1px solid #FFB6C1 !important;
    font-size: 0.85rem !important;
}

/* ── アラート ── */
.stAlert { border-radius: 12px !important; }

/* ── divider ── */
hr { border-color: #FFD6E7 !important; }

/* ── リンクボタン ── */
.stLinkButton > a {
    border-radius: 20px !important;
    font-weight: 600 !important;
}

/* ── 見出し ── */
h2, h3 { color: #C2185B !important; }

/* ────────────────────────────────
   モバイルレスポンシブ（768px以下）
   ──────────────────────────────── */
@media screen and (max-width: 768px) {
    .main .block-container {
        padding: 0.5rem 0.6rem 1.5rem !important;
    }
    .baby-header {
        padding: 1.2rem 1rem 1rem !important;
        border-radius: 16px !important;
    }
    .baby-header .header-icon {
        width: 70px !important;
        height: 70px !important;
    }
    .baby-header h1 {
        font-size: 1.4rem !important;
    }
    .baby-header .social-links a {
        padding: 6px 12px !important;
        font-size: 0.78rem !important;
    }
    /* Streamlitのカラムをモバイルで縦積み */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    .stButton > button {
        font-size: 0.9rem !important;
        padding: 0.5rem 1rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.8rem !important;
        padding: 5px 8px !important;
    }
    h2, h3 { font-size: 1.1rem !important; }
    .stCode { font-size: 0.78rem !important; }
}

/* スマホ縦（480px以下） */
@media screen and (max-width: 480px) {
    .baby-header h1 { font-size: 1.2rem !important; }
    .baby-header .social-links { gap: 6px !important; }
    .baby-header .social-links a {
        padding: 5px 10px !important;
        font-size: 0.75rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ── セッション状態の初期化
_defaults = {
    "generated":            False,
    "posts":                None,
    "scripts":              None,
    "threads_script":       None,
    "all_products":         None,
    "content_mode":         "normal",
    "video_url":            None,
    "instagram_posted":     False,
    "threads_text_posted":  False,
    "threads_video_posted": False,
    "youtube_posted":       False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── ヘッダー（アイコン画像 + タイトル + SNSリンク）
today_str  = datetime.now(tz=JST).strftime("%Y年%m月%d日")
icon_img   = f'<img src="data:image/png;base64,{_icon_b64}" class="header-icon">' if _icon_b64 else '<div style="font-size:4rem;">🍼</div>'

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
        <a href="https://www.threads.com/@aibaby.jp" target="_blank" class="social-threads">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 192 192" fill="white">
                <path d="M141.537 88.9883C140.71 88.5919 139.87 88.2104 139.019 87.8451C137.537 60.5382 122.616 44.905 97.5619 44.745C97.4484 44.7443 97.3355 44.7443 97.222 44.7443C82.2364 44.7443 69.7731 51.1409 62.102 62.7807L75.881 72.2328C81.6116 63.5383 90.6052 61.6848 97.2286 61.6848C97.3051 61.6848 97.3819 61.6848 97.4576 61.6855C105.707 61.7381 111.932 64.1366 115.961 68.814C118.893 72.2193 120.854 76.925 121.825 82.8638C114.511 81.6207 106.601 81.2385 98.145 81.7233C74.3247 83.0954 59.0111 96.9879 60.0396 116.292C60.5615 126.084 65.4397 134.508 73.775 140.011C80.8224 144.663 89.899 146.938 99.3323 146.423C111.79 145.74 121.563 140.987 128.381 132.296C133.559 125.696 136.834 117.143 138.28 106.366C144.217 109.949 148.617 114.664 151.047 120.332C155.179 129.967 155.42 145.8 142.501 158.708C131.182 170.016 117.576 174.908 97.0135 175.059C74.2042 174.89 56.9538 167.575 45.7381 153.317C35.2355 139.966 29.8077 120.682 29.6052 96C29.8077 71.3178 35.2355 52.0336 45.7381 38.6827C56.9538 24.4249 74.2039 17.11 97.0132 16.9405C119.988 17.1113 137.539 24.4614 149.184 38.788C154.894 45.8136 159.199 54.6488 162.037 64.9503L178.184 60.6422C174.744 47.9622 169.331 37.0357 161.965 27.974C147.036 9.60668 125.202 0.195148 97.0695 0H96.9569C68.8816 0.19447 47.2921 9.6418 32.7883 28.0793C19.8819 44.4864 13.2244 67.3157 13.0007 95.9325L13 96L13.0007 96.0675C13.2244 124.684 19.8819 147.514 32.7883 163.921C47.2921 182.358 68.8816 191.806 96.9569 192H97.0695C122.03 191.827 139.624 185.292 154.118 170.811C173.081 151.866 172.51 128.119 166.26 113.541C161.776 103.087 153.227 94.5962 141.537 88.9883ZM98.4405 129.507C88.0005 130.095 77.1544 125.409 76.6196 115.372C76.2232 107.93 81.9158 99.626 99.0812 98.6368C101.047 98.5234 102.976 98.468 104.871 98.468C111.106 98.468 116.939 99.0737 122.242 100.233C120.264 124.935 108.662 128.946 98.4405 129.507Z"/>
            </svg>
            @aibaby.jp
        </a>
        <a href="https://room.rakuten.co.jp/room_3b6e1ab198/items" target="_blank" class="social-rakuten">
            🛍️ 楽天ROOM
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── タブ
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 コンテンツ生成", "🔍 商品分析", "📋 プロンプト", "📤 投稿", "📊 履歴"
])


# ──────────────────────────────────────────────────────
# TAB 1: コンテンツ生成（ウィザード形式）
# ──────────────────────────────────────────────────────
with tab1:
    st.markdown("### 🌸 今日のコンテンツを生成する")

    if st.session_state.generated and st.session_state.posts:
        # ── 生成済みサマリー
        _p0 = st.session_state.posts[0]
        st.success("✅ 生成完了！「プロンプト」タブで内容を確認できます。")
        st.markdown("""
        <div style="background:#FFF0F8; border-radius:12px; padding:1rem 1.2rem; border:1px solid #FFB6C1;">
        """, unsafe_allow_html=True)
        if _p0.get("is_buzz_mode"):
            st.markdown("**🎉 バズmode** — せなっちが踊る・ふざける動画")
        else:
            st.markdown(f"**📦 商品：** {_p0['name'][:50]}")
            st.markdown(f"**💴 価格：** ¥{_p0.get('price', 0):,}")
        if st.session_state.threads_script:
            _th_prev = st.session_state.threads_script.get("captions", {}).get("threads", "")
            st.markdown(f"**🧵 Threads投稿文：** {_th_prev[:40]}…")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 再生成する", use_container_width=True):
            for k, v in _defaults.items():
                st.session_state[k] = v
            st.rerun()

    else:
        # ── STEP 1: 今日の出来事
        st.markdown("""
        <div style="background:#FFF0F8; border-radius:12px; padding:0.8rem 1rem;
                    border:1px solid #FFB6C1; margin-bottom:0.3rem;">
            <b>STEP 1　📝 今日のせなっちとの出来事を教えてください</b><br>
            <span style="font-size:0.82rem; color:#AD1457;">Threads育児投稿文の元ネタになります（空欄でも自動生成します）</span>
        </div>
        """, unsafe_allow_html=True)
        _today_event = st.text_area(
            "",
            placeholder="例）夜泣きが3回あった　/　初めて離乳食を食べた　/　抱っこしたら笑いかけてきた",
            key="today_event_input",
            height=90,
            label_visibility="collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── STEP 2: モード選択
        st.markdown("""
        <div style="background:#FFF0F8; border-radius:12px; padding:0.8rem 1rem;
                    border:1px solid #FFB6C1; margin-bottom:0.3rem;">
            <b>STEP 2　🎬 今日の動画スタイルを選んでください</b>
        </div>
        """, unsafe_allow_html=True)
        _mode_label = st.radio(
            "",
            [
                "通常（商品紹介）― 楽天商品をせなっちが使う動画",
                "バズmode ― せなっちが踊る・ふざける動画（商品なし）",
            ],
            key="mode_radio",
            label_visibility="collapsed",
        )
        _mode = "normal" if "通常" in _mode_label else "buzz"
        st.session_state.content_mode = _mode

        st.markdown("<br>", unsafe_allow_html=True)

        # ── STEP 3: 生成ボタン
        st.markdown("""
        <div style="background:#FFF0F8; border-radius:12px; padding:0.8rem 1rem;
                    border:1px solid #FFB6C1; margin-bottom:0.5rem;">
            <b>STEP 3　🚀 生成スタート</b><br>
            <span style="font-size:0.82rem; color:#AD1457;">約30〜60秒で全コンテンツが揃います</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 今日のコンテンツをすべて生成する", type="primary", use_container_width=True):
            try:
                from agents import image_agent, instagram_agent, youtube_agent, threads_agent

                if _mode == "normal":
                    from agents import rakuten_agent, analyzer_agent, writer_agent, quality_agent
                    with st.status("🍼 コンテンツを生成中...", expanded=True) as status:
                        st.write("① 楽天で売れ筋商品を取得中...")
                        from utils.sheets_helper import (
                            get_product_history, get_recent_codes, upsert_product,
                        )
                        history      = get_product_history()
                        recent_codes = get_recent_codes(history, days=7)
                        products     = rakuten_agent.run()
                        # Amazon商品も取得して混合（設定済みの場合）
                        try:
                            from agents import amazon_agent
                            if amazon_agent.is_configured():
                                st.write("   Amazon商品も取得中...")
                                amazon_products = amazon_agent.run(max_per_keyword=2)
                                products = products + amazon_products
                        except Exception:
                            pass
                        top3         = analyzer_agent.run(products, history=history, recent_codes=recent_codes)
                        all_scored = sorted(
                            [p for p in products if "score" in p],
                            key=lambda x: x["score"], reverse=True,
                        )
                        posts = writer_agent.run(top3)
                        st.write(f"   ✅ 商品選出完了：{posts[0]['name'][:30]}")

                        st.write("② 画像・動画プロンプトを生成中...")
                        posts = image_agent.run(posts)
                        posts = quality_agent.run(posts)
                        st.write("   ✅ GPT Image 2 / Kling AIプロンプト完了")

                        st.write("③ Instagram・YouTube キャプションを生成中...")
                        reel_script = instagram_agent.run(product=posts[0])
                        reel_script = youtube_agent.run(instagram_script=reel_script, product=posts[0])
                        st.write("   ✅ Instagram・YouTube キャプション完了")

                        st.write("④ Threads 育児投稿文を生成中...")
                        threads_script = threads_agent.run(today_event=_today_event)
                        st.write("   ✅ Threads投稿文完了")

                        status.update(label="🎉 全コンテンツ生成完了！", state="complete")

                    st.session_state.posts         = posts
                    st.session_state.scripts       = [reel_script]
                    st.session_state.threads_script = threads_script
                    st.session_state.all_products  = all_scored
                    st.session_state.generated     = True
                    st.session_state.threads_text_posted = False
                    upsert_product(posts[0])

                else:  # buzz mode
                    with st.status("🎉 バズmodeコンテンツを生成中...", expanded=True) as status:
                        st.write("① バズmode 画像・動画プロンプトを生成中...")
                        buzz_post = image_agent.run_buzz()
                        st.write("   ✅ プロンプト完了")

                        st.write("② Instagram・YouTube キャプションを生成中...")
                        reel_script = instagram_agent.run_buzz()
                        reel_script = youtube_agent.run(instagram_script=reel_script, product=None)
                        st.write("   ✅ キャプション完了")

                        st.write("③ Threads 育児投稿文を生成中...")
                        threads_script = threads_agent.run(today_event=_today_event)
                        st.write("   ✅ Threads投稿文完了")

                        status.update(label="🎉 バズmodeコンテンツ生成完了！", state="complete")

                    st.session_state.posts          = [buzz_post]
                    st.session_state.scripts        = [reel_script]
                    st.session_state.threads_script = threads_script
                    st.session_state.all_products   = []
                    st.session_state.generated      = True
                    st.session_state.threads_text_posted = False

                st.balloons()
                st.rerun()

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                raise


# ──────────────────────────────────────────────────────
# TAB 2: 商品分析
# ──────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🔍 商品分析レポート")

    if not st.session_state.generated or not st.session_state.all_products:
        st.info("💡 まず「コンテンツ生成」タブで生成してください。")
    else:
        import plotly.express as px
        import plotly.graph_objects as go
        import pandas as pd

        all_p      = st.session_state.all_products
        top3_codes = {p.get("item_code", "") for p in (st.session_state.posts or []) if p.get("item_code")}
        selected_p = (st.session_state.posts or [None])[0]

        # ── スコア算出の説明
        st.markdown("""
        <div style="background:linear-gradient(135deg,#FFF0F8,#FFE8EF); border-radius:14px;
                    padding:1rem 1.2rem; margin-bottom:1rem; border:1px solid #FFB6C1; font-size:0.88rem;">
            📐 <b>スコア計算式</b>：レビュー数 × 0.6 ＋ レビュー評価 × 10 × 0.4<br>
            <span style="color:#AD1457;">スコアが最も高い商品を今回のコンテンツ対象として選出しています</span>
        </div>
        """, unsafe_allow_html=True)

        # ── DataFrame 準備
        df = pd.DataFrame(all_p)
        df["選出"] = df["item_code"].apply(lambda c: "🏆 選出" if c in top3_codes else "その他")
        df["商品名（短）"] = df["name"].str[:22] + df["name"].str[22:].apply(lambda x: "…" if x else "")
        df["スコア"] = df["score"].astype(float)
        df["レビュー数"] = df["review_count"].astype(int)
        df["レビュー評価"] = df["review_average"].astype(float)
        df["価格"] = df["price"].astype(int)

        COLOR_MAP = {"🏆 選出": "#FF6B9D", "その他": "#FFAECB"}

        # ── グラフ① スコアランキング横棒グラフ
        st.markdown("#### 📊 スコアランキング（上位15件）")
        top15 = df.head(15).iloc[::-1].copy()
        fig_bar = px.bar(
            top15,
            x="スコア",
            y="商品名（短）",
            orientation="h",
            color="選出",
            color_discrete_map=COLOR_MAP,
            hover_data={"レビュー数": True, "レビュー評価": True, "価格": True, "選出": False},
            height=max(320, len(top15) * 28),
        )
        fig_bar.update_layout(
            plot_bgcolor="rgba(255,245,248,0.6)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="sans-serif", size=12, color="#3D2B3D"),
            legend_title_text="",
            margin=dict(l=10, r=20, t=10, b=10),
            xaxis=dict(gridcolor="#FFD6E7", title="スコア"),
            yaxis=dict(title=""),
        )
        fig_bar.update_traces(marker_line_width=0)
        st.plotly_chart(fig_bar, use_container_width=True)

        # ── グラフ② レビュー数 × レビュー評価 散布図
        st.markdown("#### 🫧 レビュー数 × レビュー評価（バブル = スコア）")
        st.caption("右上ほど高スコア。バブルが大きいほどスコアが高い商品です")
        fig_scatter = px.scatter(
            df,
            x="レビュー数",
            y="レビュー評価",
            size="スコア",
            color="選出",
            color_discrete_map=COLOR_MAP,
            hover_name="商品名（短）",
            hover_data={"スコア": ":.1f", "価格": True, "選出": False},
            size_max=40,
            height=380,
        )
        fig_scatter.update_layout(
            plot_bgcolor="rgba(255,245,248,0.6)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="sans-serif", size=12, color="#3D2B3D"),
            legend_title_text="",
            margin=dict(l=10, r=20, t=10, b=10),
            xaxis=dict(gridcolor="#FFD6E7", title="レビュー数（件）"),
            yaxis=dict(gridcolor="#FFD6E7", title="レビュー評価（5点満点）"),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # ── 選出商品のスコア内訳
        if selected_p:
            st.markdown("#### 🏆 選出商品のスコア内訳")
            rc  = selected_p.get("review_count", 0)
            ra  = selected_p.get("review_average", 0.0)
            s_review = round(rc * 0.6, 1)
            s_rating = round(ra * 10 * 0.4, 1)
            total    = round(s_review + s_rating, 1)

            c1, c2, c3 = st.columns(3)
            c1.metric("レビュー数スコア", f"{s_review}", f"({rc:,}件 × 0.6)")
            c2.metric("評価スコア",       f"{s_rating}", f"({ra} × 10 × 0.4)")
            c3.metric("合計スコア",       f"{total}")

            fig_pie = go.Figure(go.Pie(
                labels=["レビュー数の寄与", "評価の寄与"],
                values=[s_review, s_rating],
                hole=0.55,
                marker_colors=["#FF6B9D", "#FFB6C1"],
                textinfo="label+percent",
                textfont_size=13,
            ))
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=240,
                showlegend=False,
                annotations=[dict(text=f"<b>{total}</b>", x=0.5, y=0.5,
                                  font_size=22, font_color="#C2185B", showarrow=False)],
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.divider()

        # ── 全商品リスト（既存の詳細表示）
        st.markdown("#### 📋 全商品一覧")
        st.caption(f"楽天APIで取得した {len(all_p)} 件をスコア順に表示")

        for rank, p in enumerate(all_p, 1):
            is_selected = p.get("item_code", "") in top3_codes and p.get("item_code", "")
            badge = "🏆 選出" if is_selected else ""
            score_color = "#FF6B9D" if rank <= 3 else "#888"

            with st.container():
                col_rank, col_info, col_score = st.columns([1, 6, 2])

                with col_rank:
                    medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
                    st.markdown(
                        f'<div style="font-size:1.4rem; text-align:center; padding-top:0.5rem;">{medal}</div>',
                        unsafe_allow_html=True,
                    )

                with col_info:
                    name_display = p["name"][:55] + ("…" if len(p["name"]) > 55 else "")
                    st.markdown(
                        f'<div style="font-weight:700; font-size:0.95rem; color:#3D2B3D;">'
                        f'{name_display} {badge}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div style="font-size:0.82rem; color:#888;">'
                        f'🔑 {p.get("keyword","—")} ｜ 🏪 {p.get("shop_name","")[:20]}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    url = p.get("affiliate_url") or p.get("url", "")
                    if url:
                        st.markdown(
                            f'<a href="{url}" target="_blank" style="font-size:0.78rem; color:#FF6B9D;">🔗 商品を見る</a>',
                            unsafe_allow_html=True,
                        )

                with col_score:
                    st.markdown(
                        f'<div style="text-align:center;">'
                        f'<div style="font-size:1.3rem; font-weight:800; color:{score_color};">'
                        f'{p["score"]:.1f}</div>'
                        f'<div style="font-size:0.75rem; color:#888;">スコア</div>'
                        f'<div style="font-size:0.85rem; font-weight:700; color:#3D2B3D;">¥{p["price"]:,}</div>'
                        f'<div style="font-size:0.75rem; color:#888;">⭐ {p.get("review_average",0)} ({p.get("review_count",0):,}件)</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            st.markdown('<hr style="border-color:#FFD6E7; margin:0.4rem 0;">', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
# TAB 3: プロンプト表示・コピー
# ──────────────────────────────────────────────────────
with tab3:
    st.markdown("### 📋 プロンプト・投稿文")

    if not st.session_state.generated:
        st.info("💡 まず「コンテンツ生成」タブで生成してください。")
    else:
        posts   = st.session_state.posts or []
        scripts = st.session_state.scripts or []
        today   = datetime.now(tz=JST).strftime("%Y%m%d")

        is_buzz = (st.session_state.content_mode == "buzz") or (posts and posts[0].get("is_buzz_mode"))

        if posts:
            p = posts[0]
            if not is_buzz:
                st.markdown(f"**📦 本日の商品：** {p['name'][:50]}　|　¥{p.get('price',0):,}")
            else:
                st.markdown("**🎉 バズmode** - せなっちが踊る・ふざける動画")
            st.divider()

            # 楽天ROOM（通常modeのみ）
            if not is_buzz:
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
                        if st.button("🏠 楽天ROOM 投稿済みにする", use_container_width=True):
                            from utils.sheets_helper import increment_count
                            increment_count(p.get("item_code", ""), "楽天ROOM投稿数")
                            st.session_state[_room_key] = True
                            st.rerun()
                st.code(p.get("room_description", ""), language=None)
                if p.get("affiliate_url"):
                    st.caption(f"アフィリエイトURL: `{p['affiliate_url']}`")
                st.divider()

                st.markdown("#### 🖼️ GPT Image プロンプト（文字あり・楽天ROOM用）")
                st.caption(f"せなっち写真＋商品写真を添付 → `{today}.png` として保存")
                st.link_button("🤖 ChatGPTを開く", "https://chatgpt.com")
                st.code(p.get("gpt_image_prompt", ""), language=None)
                st.divider()

            # 動画用画像プロンプト（全mode共通）
            if is_buzz:
                st.markdown("#### 🎉 GPT Image プロンプト（バズmode・コスチューム）")
                st.markdown("""
                <div style="background:#FFF8E7; border-radius:10px; padding:0.7rem 1rem;
                            border:1px solid #FFCC80; font-size:0.84rem; margin-bottom:0.4rem;">
                    📎 <b>ChatGPTへ添付する画像は2枚</b><br>
                    　① せなっちの写真<br>
                    　② 着させたいコスチューム画像（アニメ服・野菜コス・果物コスなど）<br>
                    <span style="color:#E65100;">コスチューム画像を変えるだけで毎回違う動画が作れます</span>
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"生成後 `{today}_buzz.png` として保存 → Kling AIで動画化")
            else:
                st.markdown("#### 🎬 GPT Image プロンプト（文字なし・動画用）")
                st.caption(f"せなっち写真＋商品写真を添付 → `{today}_video.png` として保存 → Kling AIで動画化")
            st.link_button("🤖 ChatGPTを開く ", "https://chatgpt.com")
            st.code(p.get("gpt_image_prompt_notxt", ""), language=None)
            st.divider()

            # Kling AI動画プロンプト
            st.markdown("#### 🎥 Kling AI 動画プロンプト")
            st.caption("上記で生成した画像をKling AIにアップロード → Image to Video で使用")
            st.link_button("🎬 Kling AIを開く", "https://klingai.com")
            st.code(p.get("video_prompt", ""), language=None)

        if scripts:
            st.divider()
            for s in scripts:
                ctype    = s.get("type", "")
                captions = s.get("captions", {})

                if ctype == "reel":
                    # コンテンツ設計スコア + BGM表示
                    _dm  = s.get("dm_trigger", "")
                    _hook = s.get("hook", "")
                    _bgm = s.get("bgm_style", "")
                    if _dm or _hook or _bgm:
                        st.markdown("""
                        <div style="background:#FFF0F8; border-radius:10px; padding:0.8rem 1rem;
                                    border:1px solid #FFB6C1; font-size:0.82rem; margin-bottom:0.5rem;">
                        """, unsafe_allow_html=True)
                        if _hook:
                            st.markdown(f"**🎬 Hook（冒頭0〜2秒）：** {_hook}")
                        if _dm:
                            st.markdown(f"**📤 DMシェア設計：** {_dm}")
                        if _bgm:
                            st.markdown(f"**🎵 AI推奨BGMスタイル：** {_bgm}")
                        st.markdown("</div>", unsafe_allow_html=True)

                    # ── BGMトレンド情報
                    st.markdown("#### 🎵 BGM・音源トレンド（2026年5月）")
                    st.markdown("""
                    <div style="background:linear-gradient(135deg,#F3E5F5,#EDE7F6); border-radius:12px;
                                padding:0.9rem 1.1rem; border:1px solid #CE93D8; font-size:0.84rem; margin-bottom:0.4rem;">
                    <b>📈 今週のReelsバズり音源カテゴリ</b><br><br>
                    🥇 <b>LoFi / Nostalgic系（最推奨）</b> — Quiet Comfort・Oldies系。赤ちゃんスローモーション映像に最もマッチ。<br>
                    🥈 <b>Warm Strings / Gentle Piano</b> — 60〜90 BPMで感情的。育児日常記録に定番。<br>
                    🥉 <b>K-Pop キャッチー系</b> — IVE "BANG BANG"等。ポジティブ・バズ動画向け。<br>
                    ✨ <b>バイラル急上昇</b> — Everything Hallelujah（Justin Bieber）特徴紹介リール形式に人気。<br><br>
                    <b>🎬 Kling AIでのBGM選択コツ</b><br>
                    キーワード: <code>Warm</code> / <code>Nostalgic</code> / <code>Gentle</code> / <code>Heartwarming</code><br>
                    テンポ: Slow〜Medium（60〜90 BPM）を優先<br><br>
                    <b>⚡ Instagram内でトレンド音源確認 → Kling AIで近いカテゴリを選択</b><br>
                    Reels投稿時に「↗（上昇中）」マーク付き音源を使うとリールタブへの表示が優先されます
                    </div>
                    """, unsafe_allow_html=True)
                    _col_buf, _col_lat = st.columns(2)
                    with _col_buf:
                        st.link_button("📊 Buffer トレンド音源", "https://buffer.com/resources/trending-audio-instagram/")
                    with _col_lat:
                        st.link_button("📊 Later トレンド情報", "https://later.com/blog/instagram-reels-trends/")
                    st.divider()

                    st.markdown("#### 📱 Instagram Reel キャプション")
                    st.code(captions.get("instagram", ""), language=None)

                    st.markdown("#### ▶️ YouTube Shorts")
                    _yt_title   = captions.get("youtube_title", "")
                    _yt_desc    = captions.get("youtube", "")
                    _pin_comment = captions.get("pin_comment", "")
                    if _yt_title:
                        st.caption("タイトル")
                        st.code(_yt_title, language=None)
                        st.caption("説明文（#Shorts・ハッシュタグ含む）")
                        st.code(_yt_desc, language=None)
                        if _pin_comment:
                            st.caption("ピン留めコメント")
                            st.code(_pin_comment, language=None)
                    else:
                        st.info("再生成するとYouTube Shortsコンテンツが追加されます")

                st.divider()

        # Threads 育児投稿文（threads_agentが生成したテキスト投稿）
        if st.session_state.threads_script:
            _th_text = st.session_state.threads_script.get("captions", {}).get("threads", "")
            if _th_text:
                st.markdown("#### 🧵 Threads 育児投稿文（テキスト）")
                st.caption("動画なしのテキスト投稿です。「投稿」タブからBufferに予約できます。")
                st.code(_th_text, language=None)
                st.divider()


# ──────────────────────────────────────────────────────
# TAB 4: 投稿
# ──────────────────────────────────────────────────────
with tab4:
    st.markdown("### 📤 投稿")

    if not st.session_state.generated:
        st.info("💡 まず「コンテンツ生成」タブで生成してください。")
    else:
        _now = datetime.now(tz=JST)
        _t3  = (_now + timedelta(minutes=3)).strftime("%H:%M")
        _t48 = (_now + timedelta(minutes=48)).strftime("%H:%M")
        _th_text = (st.session_state.threads_script or {}).get("captions", {}).get("threads", "")

        # ─────────────────────────────────────────
        # ① 動画アップロード（共通）
        # ─────────────────────────────────────────
        st.markdown("""
        <div style="background:linear-gradient(135deg,#F3E5F5,#EDE7F6); border-radius:16px;
                    padding:1.2rem 1.4rem; margin-bottom:0.8rem; border:1px solid #CE93D8;">
            <div style="font-size:1.1rem; font-weight:800; color:#6A1B9A; margin-bottom:0.3rem;">
                ☁️ 動画アップロード
            </div>
            <div style="font-size:0.85rem; color:#7B1FA2;">
                Instagram / YouTube / Threads 動画投稿に使います。Kling AIで生成した動画（MP4）を選択してください。
            </div>
        </div>
        """, unsafe_allow_html=True)

        video_file = st.file_uploader(
            "動画ファイルを選択（MP4 / MOV）",
            type=["mp4", "mov"],
            key="vid_uploader",
        )
        if video_file:
            st.video(video_file)
            if not st.session_state.video_url:
                if st.button("☁️ Cloudinaryにアップロード", type="primary", use_container_width=True):
                    with st.spinner("アップロード中...（動画は少し時間がかかります）"):
                        from utils.cloudinary_helper import upload_bytes
                        url = upload_bytes(video_file.read(), resource_type="video")
                    if url:
                        st.session_state.video_url = url
                        st.success("✅ 動画のアップロード完了！")
                        st.rerun()
                    else:
                        st.error("アップロードに失敗しました。Cloudinaryの設定を確認してください。")
            else:
                st.success("✅ 動画アップロード済み")

        st.divider()

        # ─────────────────────────────────────────
        # ② Instagram Reel 投稿
        # ─────────────────────────────────────────
        st.markdown("""
        <div style="background:linear-gradient(135deg,#FFF0F8,#FFE8EF); border-radius:16px;
                    padding:1.2rem 1.4rem; margin-bottom:0.8rem; border:1px solid #FFB6C1;">
            <div style="font-size:1.1rem; font-weight:800; color:#C2185B; margin-bottom:0.3rem;">
                📱 Instagram Reel 投稿
            </div>
            <div style="font-size:0.85rem; color:#AD1457;">動画必須 / 上でアップロードしてから投稿</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.instagram_posted:
            st.success(f"✅ Instagram Reel 投稿済み（{_t3} 頃）")
        elif not st.session_state.video_url:
            st.button("📱 Instagram Reel に投稿する", use_container_width=True, disabled=True)
            st.caption("⚠️ 先に動画をアップロードしてください")
        else:
            if st.button("📱 Instagram Reel に投稿する", type="primary", use_container_width=True):
                with st.spinner("Bufferに予約中..."):
                    from agents.buffer_agent import run as buf_run
                    results = buf_run(
                        [s.copy() for s in st.session_state.scripts],
                        video_url=st.session_state.video_url,
                        platforms=["instagram"],
                    )
                ok_ig = any(r.get("buffer_posts", {}).get("instagram", {}).get("success") for r in results)
                if ok_ig:
                    st.session_state.instagram_posted = True
                    _ic = (st.session_state.posts or [{}])[0].get("item_code", "")
                    if _ic:
                        from utils.sheets_helper import increment_count as _inc
                        _inc(_ic, "Instagram投稿数")
                    st.success(f"✅ Instagram Reel {_t3} 頃に投稿されます")
                    st.rerun()
                else:
                    errs = [r.get("buffer_posts", {}).get("instagram", {}).get("error", "") for r in results]
                    st.error(f"失敗: {' | '.join(e for e in errs if e) or '不明なエラー'}")

        st.divider()

        # ─────────────────────────────────────────
        # ③ YouTube Shorts 投稿
        # ─────────────────────────────────────────
        st.markdown("""
        <div style="background:linear-gradient(135deg,#FFF3E0,#FFE0B2); border-radius:16px;
                    padding:1.2rem 1.4rem; margin-bottom:0.8rem; border:1px solid #FFB74D;">
            <div style="font-size:1.1rem; font-weight:800; color:#E65100; margin-bottom:0.3rem;">
                ▶️ YouTube Shorts 投稿
            </div>
            <div style="font-size:0.85rem; color:#BF360C;">動画必須 / Bufferにチャンネル連携済みが前提</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.youtube_posted:
            st.success("✅ YouTube Shorts 投稿済み")
        elif not st.session_state.video_url:
            st.button("▶️ YouTube Shorts に投稿する", use_container_width=True, disabled=True)
            st.caption("⚠️ 先に動画をアップロードしてください")
        else:
            _yt_reel = next((s for s in (st.session_state.scripts or []) if s.get("type") == "reel"), None)
            _yt_title_preview = (_yt_reel or {}).get("captions", {}).get("youtube_title", "（タイトル未生成）")
            st.caption(f"タイトル: {_yt_title_preview}")
            if st.button("▶️ YouTube Shorts に投稿する", type="primary", use_container_width=True):
                with st.spinner("Bufferに予約中..."):
                    from agents.buffer_agent import run as buf_run_yt
                    results_yt = buf_run_yt(
                        [s.copy() for s in st.session_state.scripts],
                        video_url=st.session_state.video_url,
                        platforms=["youtube"],
                    )
                ok_yt = any(r.get("buffer_posts", {}).get("youtube", {}).get("success") for r in results_yt)
                if ok_yt:
                    st.session_state.youtube_posted = True
                    st.success(f"✅ YouTube Shorts {_t3} 頃に投稿されます")
                    st.rerun()
                else:
                    errs_yt = [r.get("buffer_posts", {}).get("youtube", {}).get("error", "") for r in results_yt]
                    st.error(f"失敗: {' | '.join(e for e in errs_yt if e) or '不明なエラー'}")

        st.divider()

        # ─────────────────────────────────────────
        # ④ Threads 投稿（育児投稿文 / 動画あり or なし選択）
        # ─────────────────────────────────────────
        st.markdown("""
        <div style="background:linear-gradient(135deg,#E8F5E9,#DCEDC8); border-radius:16px;
                    padding:1.2rem 1.4rem; margin-bottom:0.8rem; border:1px solid #A5D6A7;">
            <div style="font-size:1.1rem; font-weight:800; color:#2E7D32; margin-bottom:0.3rem;">
                🧵 Threads 投稿（育児投稿文）
            </div>
            <div style="font-size:0.85rem; color:#388E3C;">
                テキストのみ / 動画と一緒に、を投稿タイミングで選べます
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not _th_text:
            st.caption("⚠️ 「コンテンツ生成」タブで Threads投稿文を先に生成してください")
        else:
            st.caption(f"投稿内容：{_th_text[:60]}…")
            col_txt, col_vid = st.columns(2)

            with col_txt:
                if st.session_state.threads_text_posted:
                    st.success("✅ テキスト投稿済み")
                else:
                    if st.button("🧵 テキストのみ投稿", type="primary", use_container_width=True):
                        with st.spinner("Bufferに予約中..."):
                            from agents.buffer_agent import run as buf_run_th
                            results_th = buf_run_th(
                                [st.session_state.threads_script.copy()],
                                platforms=["threads"],
                            )
                        ok_th = any(r.get("buffer_posts", {}).get("threads", {}).get("success") for r in results_th)
                        if ok_th:
                            st.session_state.threads_text_posted = True
                            _ic = (st.session_state.posts or [{}])[0].get("item_code", "")
                            if _ic:
                                from utils.sheets_helper import increment_count as _inc_th
                                _inc_th(_ic, "Threads投稿数")
                            st.success(f"✅ {_t3} 頃に投稿されます")
                            st.rerun()
                        else:
                            err = next((r["buffer_posts"].get("threads", {}).get("error", "") for r in results_th if r.get("buffer_posts")), "不明なエラー")
                            st.error(f"失敗: {err}")

            with col_vid:
                if st.session_state.threads_video_posted:
                    st.success("✅ 動画投稿済み")
                elif not st.session_state.video_url:
                    st.button("📹 動画と一緒に投稿", use_container_width=True, disabled=True)
                    st.caption("動画アップロード後に有効")
                else:
                    if st.button("📹 動画と一緒に投稿", type="primary", use_container_width=True):
                        # reelスクリプトに育児投稿文を注入してThreadsのみ投稿
                        _scripts_vid = [s.copy() for s in (st.session_state.scripts or [])]
                        for _s in _scripts_vid:
                            if _s.get("type") == "reel":
                                _s.setdefault("captions", {})
                                _s["captions"]["threads"] = _th_text
                        with st.spinner("Bufferに予約中..."):
                            from agents.buffer_agent import run as buf_run_thv
                            results_thv = buf_run_thv(
                                _scripts_vid,
                                video_url=st.session_state.video_url,
                                platforms=["threads"],
                            )
                        ok_thv = any(r.get("buffer_posts", {}).get("threads_reel", {}).get("success") for r in results_thv)
                        if ok_thv:
                            st.session_state.threads_video_posted = True
                            _ic = (st.session_state.posts or [{}])[0].get("item_code", "")
                            if _ic:
                                from utils.sheets_helper import increment_count as _inc_thv
                                _inc_thv(_ic, "Threads投稿数")
                            st.success(f"✅ {_t48} 頃に投稿されます")
                            st.rerun()
                        else:
                            errs_thv = [r.get("buffer_posts", {}).get("threads_reel", {}).get("error", "") for r in results_thv]
                            st.error(f"失敗: {' | '.join(e for e in errs_thv if e) or '不明なエラー'}")


# ──────────────────────────────────────────────────────
# TAB 5: 投稿履歴
# ──────────────────────────────────────────────────────
with tab5:
    st.markdown("### 📊 投稿履歴")
    st.caption("商品ごとの生成回数・各プラットフォーム投稿数を管理します（生成3回でその商品はスキップ）")

    if st.button("🔍 履歴を読み込む", use_container_width=True):
        with st.spinner("Google Sheetsから取得中..."):
            from utils.sheets_helper import get_history
            df = get_history()

        if df is None:
            st.error("Google Sheetsの設定を確認してください（GOOGLE_CREDENTIALS_JSON / GOOGLE_SHEETS_ID）")
        elif df.empty:
            st.info("📭 まだ投稿履歴がありません。")
        else:
            # 投稿済み件数サマリ
            try:
                s_col1, s_col2, s_col3, s_col4 = st.columns(4)
                with s_col1:
                    st.metric("商品数", len(df))
                with s_col2:
                    st.metric("楽天ROOM投稿", int(df["楽天ROOM投稿数"].astype(int).sum()) if "楽天ROOM投稿数" in df.columns else "-")
                with s_col3:
                    st.metric("Instagram投稿", int(df["Instagram投稿数"].astype(int).sum()) if "Instagram投稿数" in df.columns else "-")
                with s_col4:
                    st.metric("Threads投稿", int(df["Threads投稿数"].astype(int).sum()) if "Threads投稿数" in df.columns else "-")
            except Exception:
                pass

            st.divider()

            # カラムの表示順を整理
            display_cols = [c for c in [
                "最終生成日", "商品名", "価格", "キーワード",
                "生成回数", "楽天ROOM投稿数", "Instagram投稿数", "Threads投稿数",
            ] if c in df.columns]
            st.dataframe(
                df[display_cols] if display_cols else df,
                use_container_width=True,
                hide_index=True,
            )
            st.caption(f"合計 {len(df)} 商品")
