"""
せなっち SNS管理 Webアプリ
Streamlit製。Streamlit Community Cloudで無料ホスティング。
"""
import os
import sys
import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path

# ── Streamlit Cloud の secrets を環境変数に注入
if hasattr(st, "secrets"):
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ.setdefault(_k, _v)

sys.path.insert(0, str(Path(__file__).parent))

# ── ページ設定
st.set_page_config(
    page_title="せなっち SNS管理",
    page_icon="🍼",
    layout="wide",
)

# ── カスタムCSS（ベビーテーマ）
st.markdown("""
<style>
/* 全体背景 */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* ヘッダーグラデーション */
.baby-header {
    background: linear-gradient(135deg, #FFB6C1 0%, #FFDDE8 50%, #FFE8B0 100%);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(255, 107, 157, 0.2);
}
.baby-header h1 {
    color: #C2185B !important;
    font-size: 2rem !important;
    margin: 0 !important;
    letter-spacing: 0.05em;
}
.baby-header p {
    color: #AD1457 !important;
    margin: 0.3rem 0 0 !important;
    font-size: 0.9rem;
}

/* セクションカード */
.baby-card {
    background: white;
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin: 0.8rem 0;
    border-left: 5px solid #FF6B9D;
    box-shadow: 0 2px 10px rgba(255, 107, 157, 0.1);
}
.baby-card h3 {
    color: #C2185B !important;
    margin-top: 0 !important;
}

/* プライマリボタン */
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
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(255, 107, 157, 0.45) !important;
}

/* セカンダリボタン */
.stButton > button[kind="secondary"] {
    border-radius: 20px !important;
    border: 2px solid #FF6B9D !important;
    color: #FF6B9D !important;
    font-weight: 600 !important;
}

/* リンクボタン */
.stLinkButton > a {
    border-radius: 20px !important;
    font-weight: 600 !important;
}

/* タブ */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,182,193,0.15);
    border-radius: 14px;
    padding: 6px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    color: #AD1457 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FF6B9D, #FF8FAB) !important;
    color: white !important;
}

/* コードブロック（コピー用） */
.stCode {
    border-radius: 12px !important;
    border: 1px solid #FFB6C1 !important;
}

/* info / success / warning */
.stAlert {
    border-radius: 12px !important;
}

/* divider */
hr {
    border-color: #FFD6E7 !important;
}

/* ステータスバー */
.stStatus {
    border-radius: 12px !important;
}

/* 外部リンクボタン行 */
.link-row {
    display: flex;
    gap: 0.5rem;
    margin: 0.4rem 0 1rem;
    flex-wrap: wrap;
}
</style>
""", unsafe_allow_html=True)

# ── セッション状態の初期化
_defaults = {
    "generated": False,
    "posts": None,
    "scripts": None,
    "video_url": None,
    "threads_posted": False,
    "instagram_posted": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── ヘッダー
today_str = datetime.now().strftime("%Y年%m月%d日")
st.markdown(f"""
<div class="baby-header">
    <h1>🍼 せなっち SNS管理 👶</h1>
    <p>✨ {today_str} ✨</p>
</div>
""", unsafe_allow_html=True)

# ── タブ
tab1, tab2, tab3, tab4 = st.tabs(["🚀 コンテンツ生成", "📋 プロンプト", "📤 投稿", "📊 履歴"])


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
                    with st.status("🍼 せなっちのコンテンツを準備中...", expanded=True) as status:
                        st.write("🛍️ 楽天APIで売れ筋商品を取得中...")
                        products = rakuten_agent.run()
                        scored   = analyzer_agent.run(products)
                        posts    = writer_agent.run(scored)
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

                    st.session_state.posts    = posts
                    st.session_state.scripts  = scripts
                    st.session_state.generated = True
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    raise

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; color:#FF6B9D; font-size:0.85rem;">
            🌸 生成には約30〜60秒かかります 🌸
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
# TAB 2: プロンプト表示・コピー
# ──────────────────────────────────────────────────────
with tab2:
    st.markdown("### 📋 プロンプト・投稿文")

    if not st.session_state.generated:
        st.info("💡 まず「コンテンツ生成」タブで生成してください。")
    else:
        posts   = st.session_state.posts or []
        scripts = st.session_state.scripts or []
        today   = datetime.now().strftime("%Y%m%d")

        if posts:
            p = posts[0]
            st.markdown(f"**📦 本日の商品：** {p['name'][:50]}　|　¥{p.get('price',0):,}")
            st.divider()

            # ── 楽天ROOM
            st.markdown("#### 🛍️ 楽天ROOM 紹介文")
            st.caption("📱 楽天ROOMアプリから手動投稿してください")
            st.link_button("🏠 楽天ROOMを開く", "https://room.rakuten.co.jp")
            st.code(p.get("room_description", ""), language=None)
            if p.get("affiliate_url"):
                st.caption(f"アフィリエイトURL: `{p['affiliate_url']}`")

            st.divider()

            # ── GPT Image 文字あり
            st.markdown("#### 🖼️ GPT Image プロンプト（文字あり）")
            st.caption(f"せなっち写真＋商品写真を添付 → `{today}.png` として保存（楽天ROOM用）")
            st.link_button("🤖 ChatGPTを開く", "https://chatgpt.com")
            st.code(p.get("gpt_image_prompt", ""), language=None)

            st.divider()

            # ── GPT Image 文字なし
            st.markdown("#### 🎬 GPT Image プロンプト（文字なし・動画生成用）")
            st.caption(f"せなっち写真＋商品写真を添付 → `{today}_video.png` として保存　→ InsMindで動画化")
            st.link_button("🤖 ChatGPTを開く ", "https://chatgpt.com")
            st.code(p.get("gpt_image_prompt_notxt", ""), language=None)

            st.divider()

            # ── InsMind
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
                    st.caption("同じ動画を Threads にも投稿する場合はこちら")
                    st.code(captions.get("threads", ""), language=None)

                st.divider()


# ──────────────────────────────────────────────────────
# TAB 3: 投稿
# ──────────────────────────────────────────────────────
with tab3:
    st.markdown("### 📤 動画をアップロードして投稿")

    if not st.session_state.generated:
        st.info("💡 まず「コンテンツ生成」タブで生成してください。")
    else:
        # ── 動画アップロード
        st.markdown("""
        <div style="background:#FFF0F8; border-radius:14px; padding:1rem 1.2rem; margin-bottom:1rem;
                    border: 1px solid #FFB6C1;">
            🎬 <b>InsMindで生成した動画（MP4）をアップロード</b><br>
            <span style="font-size:0.85rem; color:#AD1457;">
                この動画は Threads・Instagram Reel の両方に使用されます
            </span>
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
                col_v1, col_v2, col_v3 = st.columns([1, 2, 1])
                with col_v2:
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
                st.success("✅ 動画アップロード済み　投稿できます！")

        st.divider()

        # ── 投稿ボタン
        post_time = (datetime.now() + timedelta(minutes=3)).strftime("%H:%M")
        st.markdown(f"""
        <div style="text-align:center; background:linear-gradient(135deg,#FFE0EC,#FFD6B0);
                    border-radius:14px; padding:0.8rem; margin-bottom:1rem;">
            ⏰ <b>投稿予定時刻：約 {post_time}（3分後）</b>
        </div>
        """, unsafe_allow_html=True)

        col_t, col_i = st.columns(2)

        with col_t:
            st.markdown("""
            <div style="text-align:center; font-size:1.5rem; margin-bottom:0.3rem;">🧵</div>
            <div style="text-align:center; font-weight:700; color:#C2185B; margin-bottom:0.8rem;">Threads</div>
            """, unsafe_allow_html=True)

            if st.session_state.threads_posted:
                st.success("✅ 投稿済み")
            else:
                if st.button("Threadsに投稿する", type="primary", use_container_width=True):
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
                        st.session_state.threads_posted = True
                        st.success(f"✅ {post_time}頃に投稿されます")
                        st.rerun()
                    else:
                        err = next(
                            (r["buffer_posts"].get("threads", {}).get("error", "")
                             for r in results if r.get("buffer_posts")), "不明なエラー"
                        )
                        st.error(f"失敗: {err}")

        with col_i:
            st.markdown("""
            <div style="text-align:center; font-size:1.5rem; margin-bottom:0.3rem;">📱</div>
            <div style="text-align:center; font-weight:700; color:#C2185B; margin-bottom:0.8rem;">Instagram Reel</div>
            """, unsafe_allow_html=True)

            if st.session_state.instagram_posted:
                st.success("✅ 投稿済み")
            elif not st.session_state.video_url:
                st.button("Instagramに投稿する", use_container_width=True, disabled=True)
                st.caption("⚠️ 先に動画をアップロードしてください")
            else:
                if st.button("Instagramに投稿する", type="primary", use_container_width=True):
                    with st.spinner("Bufferに予約中..."):
                        from agents.buffer_agent import run as buf_run
                        results = buf_run(
                            [s.copy() for s in st.session_state.scripts],
                            video_url=st.session_state.video_url,
                            platforms=["instagram"],
                        )
                    ok = any(
                        r.get("buffer_posts", {}).get("instagram", {}).get("success")
                        for r in results
                    )
                    if ok:
                        st.session_state.instagram_posted = True
                        st.success(f"✅ {post_time}頃に投稿されます")
                        st.rerun()
                    else:
                        err = next(
                            (r["buffer_posts"].get("instagram", {}).get("error", "")
                             for r in results if r.get("buffer_posts")), "不明なエラー"
                        )
                        st.error(f"失敗: {err}")


# ──────────────────────────────────────────────────────
# TAB 4: 投稿履歴
# ──────────────────────────────────────────────────────
with tab4:
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
