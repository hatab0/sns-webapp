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
    "generated":           False,
    "posts":               None,
    "scripts":             None,
    "all_products":        None,   # 全商品スコア一覧（商品分析タブ用）
    "video_url":           None,
    "threads_text_posted": False,
    "video_posted":        False,
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
# TAB 1: コンテンツ生成
# ──────────────────────────────────────────────────────
with tab1:
    st.markdown("### 🌸 今日のコンテンツを自動生成")
    st.caption("楽天APIで売れ筋商品を取得し、Claude APIで全コンテンツを生成します。")

    if st.session_state.generated and st.session_state.posts:
        p = st.session_state.posts[0]
        st.success(f"✅ 生成済み！　**{p['name'][:40]}** | ¥{p.get('price', 0):,}")
        col_a, col_b = st.columns([1, 3])
        with col_a:
            if st.button("🔄 再生成", use_container_width=True):
                for k, v in _defaults.items():
                    st.session_state[k] = v
                st.rerun()
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        col_c, col_d, col_e = st.columns([1, 2, 1])
        with col_d:
            if st.button("💫 今日のコンテンツを生成する", type="primary", use_container_width=True):
                try:
                    from agents import (
                        rakuten_agent, analyzer_agent, writer_agent,
                        image_agent, quality_agent, script_agent, caption_agent,
                    )
                    with st.status("🍼 Baby Boo のコンテンツを準備中...", expanded=True) as status:
                        st.write("🛍️ 楽天APIで売れ筋商品を取得中...")
                        products = rakuten_agent.run()
                        top3     = analyzer_agent.run(products)
                        # 全商品（スコア付き）をソートして保存
                        all_scored = sorted(
                            [p for p in products if "score" in p],
                            key=lambda x: x["score"], reverse=True
                        )
                        posts    = writer_agent.run(top3)
                        st.write(f"✅ {len(posts)}件の商品を選出・紹介文生成完了")

                        st.write("🖼️  画像・動画プロンプトを生成中...")
                        posts = image_agent.run(posts)
                        posts = quality_agent.run(posts)
                        st.write("✅ プロンプト生成完了")

                        st.write("📱 Threads・Instagramコンテンツを生成中...")
                        scripts = script_agent.run(product=posts[0])
                        scripts = caption_agent.run(scripts, product=posts[0])
                        st.write("✅ キャプション生成完了")

                        status.update(label="🎉 全コンテンツ生成完了！", state="complete")

                    st.session_state.posts        = posts
                    st.session_state.scripts      = scripts
                    st.session_state.all_products = all_scored
                    st.session_state.generated    = True
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    raise

        st.markdown("""
        <div style="text-align:center; color:#FF6B9D; font-size:0.85rem; margin-top:1rem;">
            🌸 生成には約30〜60秒かかります 🌸
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
# TAB 2: 商品分析
# ──────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🔍 商品分析レポート")

    if not st.session_state.generated or not st.session_state.all_products:
        st.info("💡 まず「コンテンツ生成」タブで生成してください。")
    else:
        all_p   = st.session_state.all_products
        top3_codes = {p.get("item_code", "") for p in (st.session_state.posts or [])}

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

        if posts:
            p = posts[0]
            st.markdown(f"**📦 本日の商品：** {p['name'][:50]}　|　¥{p.get('price',0):,}")
            st.divider()

            st.markdown("#### 🛍️ 楽天ROOM 紹介文")
            st.caption("📱 楽天ROOMアプリから手動投稿してください")
            st.link_button("🏠 楽天ROOMを開く", "https://room.rakuten.co.jp/room_3b6e1ab198/items")
            st.code(p.get("room_description", ""), language=None)
            if p.get("affiliate_url"):
                st.caption(f"アフィリエイトURL: `{p['affiliate_url']}`")
            st.divider()

            st.markdown("#### 🖼️ GPT Image プロンプト（文字あり）")
            st.caption(f"せなっち写真＋商品写真を添付 → `{today}.png` として保存（楽天ROOM用）")
            st.link_button("🤖 ChatGPTを開く", "https://chatgpt.com")
            st.code(p.get("gpt_image_prompt", ""), language=None)
            st.divider()

            st.markdown("#### 🎬 GPT Image プロンプト（文字なし・動画生成用）")
            st.caption(f"せなっち写真＋商品写真を添付 → `{today}_video.png` として保存 → InsMindで動画化")
            st.link_button("🤖 ChatGPTを開く ", "https://chatgpt.com")
            st.code(p.get("gpt_image_prompt_notxt", ""), language=None)
            st.divider()

            st.markdown("#### 🎥 InsMind 動画プロンプト")
            st.caption(f"`{today}_video.png` をInsMindにアップロードして使用")
            st.link_button("🎬 InsMindを開く", "https://www.insmind.com")
            st.code(p.get("video_prompt", ""), language=None)

        if scripts:
            st.divider()
            for s in scripts:
                ctype    = s.get("type", "")
                captions = s.get("captions", {})

                if ctype == "threads_product":
                    st.markdown("#### 🧵 Threads ① 商品投稿")
                    st.code(captions.get("threads", ""), language=None)

                elif ctype == "threads_buzz":
                    st.markdown("#### 🧵 Threads ② バズ投稿")
                    st.caption(f"テーマ: {s.get('theme', '')}")
                    st.code(captions.get("threads", ""), language=None)

                elif ctype == "reel":
                    st.markdown("#### 📱 Instagram Reel キャプション")
                    st.code(captions.get("instagram", ""), language=None)
                    st.markdown("#### 🧵 Threads 動画投稿キャプション")
                    st.caption("同じ動画をThreadsにも投稿する場合はこちら")
                    st.code(captions.get("threads", ""), language=None)

                st.divider()


# ──────────────────────────────────────────────────────
# TAB 4: 投稿
# ──────────────────────────────────────────────────────
with tab4:
    st.markdown("### 📤 投稿")

    if not st.session_state.generated:
        st.info("💡 まず「コンテンツ生成」タブで生成してください。")
    else:
        post_time_text  = (datetime.now(tz=JST) + timedelta(minutes=3)).strftime("%H:%M")
        post_time_buzz  = (datetime.now(tz=JST) + timedelta(minutes=33)).strftime("%H:%M")
        post_time_video = (datetime.now(tz=JST) + timedelta(minutes=3)).strftime("%H:%M")

        # ── ① Threads テキスト投稿（動画不要）
        st.markdown("""
        <div style="background:linear-gradient(135deg,#FFF0F8,#FFE8EF); border-radius:16px;
                    padding:1.2rem 1.4rem; margin-bottom:0.8rem; border:1px solid #FFB6C1;">
            <div style="font-size:1.1rem; font-weight:800; color:#C2185B; margin-bottom:0.3rem;">
                🧵 Threads テキスト投稿（① ②）
            </div>
            <div style="font-size:0.85rem; color:#AD1457;">
                動画不要・コンテンツ生成後すぐに予約できます
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.threads_text_posted:
            st.success(f"✅ Threads①② 投稿済み　（① {post_time_text} / ② {post_time_buzz} 頃）")
        else:
            if st.button("🧵 Threads に①②を投稿する", type="primary", use_container_width=True):
                with st.spinner("Bufferに予約中..."):
                    from agents.buffer_agent import run as buf_run
                    results = buf_run(
                        [s.copy() for s in st.session_state.scripts],
                        platforms=["threads"],
                    )
                ok = any(
                    r.get("buffer_posts", {}).get("threads", {}).get("success")
                    for r in results
                )
                if ok:
                    st.session_state.threads_text_posted = True
                    st.success(f"✅ ① {post_time_text} 頃・② {post_time_buzz} 頃に投稿されます")
                    st.rerun()
                else:
                    err = next(
                        (r["buffer_posts"].get("threads", {}).get("error", "")
                         for r in results if r.get("buffer_posts")),
                        "不明なエラー"
                    )
                    st.error(f"失敗: {err}")

        st.divider()

        # ── ② 動画投稿（Instagram Reel + Threads 動画）
        st.markdown("""
        <div style="background:linear-gradient(135deg,#FFF8E7,#FFE8D0); border-radius:16px;
                    padding:1.2rem 1.4rem; margin-bottom:0.8rem; border:1px solid #FFCC80;">
            <div style="font-size:1.1rem; font-weight:800; color:#C2185B; margin-bottom:0.3rem;">
                🎬 動画投稿（Instagram Reel + Threads）
            </div>
            <div style="font-size:0.85rem; color:#AD1457;">
                InsMindで生成した動画（MP4）をアップロードしてから投稿
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

        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

        if st.session_state.video_posted:
            st.success(f"✅ 動画投稿済み（Instagram Reel + Threads 動画）")
        elif not st.session_state.video_url:
            st.button(
                "📹 動画を投稿する（Instagram Reel + Threads）",
                use_container_width=True,
                disabled=True,
            )
            st.caption("⚠️ 先に動画ファイルをアップロードしてください")
        else:
            if st.button(
                "📹 動画を投稿する（Instagram Reel + Threads）",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner("Bufferに予約中..."):
                    from agents.buffer_agent import run as buf_run
                    results = buf_run(
                        [s.copy() for s in st.session_state.scripts],
                        video_url=st.session_state.video_url,
                    )
                ok_ig = any(r.get("buffer_posts", {}).get("instagram", {}).get("success") for r in results)
                ok_th = any(r.get("buffer_posts", {}).get("threads_reel", {}).get("success") for r in results)
                if ok_ig or ok_th:
                    st.session_state.video_posted = True
                    parts = []
                    if ok_ig:
                        parts.append(f"Instagram Reel {post_time_video}頃")
                    if ok_th:
                        parts.append(f"Threads動画 {(datetime.now(tz=JST) + timedelta(minutes=48)).strftime('%H:%M')}頃")
                    st.success(f"✅ {' / '.join(parts)} に投稿されます")
                    st.rerun()
                else:
                    errs = []
                    for r in results:
                        bp = r.get("buffer_posts", {})
                        for k in ("instagram", "threads_reel"):
                            e = bp.get(k, {}).get("error")
                            if e:
                                errs.append(e)
                    st.error(f"失敗: {' | '.join(errs) or '不明なエラー'}")


# ──────────────────────────────────────────────────────
# TAB 5: 投稿履歴
# ──────────────────────────────────────────────────────
with tab5:
    st.markdown("### 📊 投稿履歴")

    if st.button("🔍 履歴を読み込む", use_container_width=True):
        with st.spinner("Google Sheetsから取得中..."):
            from utils.sheets_helper import get_history
            df = get_history()

        if df is None:
            st.error("Google Sheetsの設定を確認してください（GOOGLE_CREDENTIALS_JSON / GOOGLE_SHEETS_ID）")
        elif df.empty:
            st.info("📭 まだ投稿履歴がありません。")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"合計 {len(df)} 件")
