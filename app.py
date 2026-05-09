"""
せなっち SNS管理 Webアプリ
Streamlit製。Streamlit Community Cloudで無料ホスティング。
"""
import os
import sys
import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path

# ── Streamlit Cloud の secrets を環境変数に注入（agent内のos.getenv()と互換）
if hasattr(st, "secrets"):
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ.setdefault(_k, _v)

# agents/ を import パスに追加
sys.path.insert(0, str(Path(__file__).parent))

# ── ページ設定
st.set_page_config(
    page_title="せなっち SNS管理",
    page_icon="👶",
    layout="wide",
)

# ── セッション状態の初期化
_defaults = {
    "generated": False,
    "posts": None,
    "scripts": None,
    "image_url": None,
    "video_url": None,
    "threads_posted": False,
    "instagram_posted": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── ヘッダー
st.title("👶 せなっち SNS管理")
st.caption(f"実行日: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
st.divider()

# ── タブ
tab1, tab2, tab3, tab4 = st.tabs(["🚀 生成", "📋 プロンプト", "📤 投稿", "📊 履歴"])


# ──────────────────────────────────────────────────────
# TAB 1: コンテンツ生成
# ──────────────────────────────────────────────────────
with tab1:
    st.header("コンテンツ生成")
    st.caption("楽天APIで商品を取得し、Claude APIで全コンテンツを自動生成します。")

    if st.session_state.generated and st.session_state.posts:
        p = st.session_state.posts[0]
        st.success(f"✅ 生成済み: **{p['name'][:40]}** | ¥{p.get('price', 0):,}")
        if st.button("再生成する", use_container_width=True):
            for k in ["generated", "posts", "scripts", "image_url", "video_url",
                      "threads_posted", "instagram_posted"]:
                st.session_state[k] = _defaults[k]
            st.rerun()
    else:
        if st.button("今日のコンテンツを生成", type="primary", use_container_width=True):
            try:
                from agents import (
                    rakuten_agent, analyzer_agent, writer_agent,
                    image_agent, quality_agent, script_agent, caption_agent,
                )

                with st.status("生成中...", expanded=True) as status:
                    st.write("📦 楽天APIで商品を取得中...")
                    products = rakuten_agent.run()
                    scored = analyzer_agent.run(products)
                    posts = writer_agent.run(scored)
                    st.write(f"✅ 商品取得・紹介文生成完了（{len(posts)}件）")

                    st.write("🖼️  画像・動画プロンプトを生成中...")
                    posts = image_agent.run(posts)
                    posts = quality_agent.run(posts)
                    st.write("✅ プロンプト生成完了")

                    st.write("📱 Threads・Instagramコンテンツを生成中...")
                    scripts = script_agent.run(product=posts[0])
                    scripts = caption_agent.run(scripts, product=posts[0])
                    st.write("✅ キャプション生成完了")

                    status.update(label="✅ 全コンテンツ生成完了！", state="complete")

                st.session_state.posts = posts
                st.session_state.scripts = scripts
                st.session_state.generated = True
                st.rerun()

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                raise


# ──────────────────────────────────────────────────────
# TAB 2: プロンプト表示・コピー
# ──────────────────────────────────────────────────────
with tab2:
    st.header("プロンプト・投稿文")

    if not st.session_state.generated:
        st.info("「生成」タブでコンテンツを生成してください。")
    else:
        posts = st.session_state.posts or []
        scripts = st.session_state.scripts or []
        today = datetime.now().strftime("%Y%m%d")

        if posts:
            p = posts[0]

            # 楽天ROOM
            st.subheader("🛍️ 楽天ROOM 紹介文")
            st.caption("📱 楽天ROOMアプリから手動投稿してください")
            st.code(p.get("room_description", ""), language=None)
            if p.get("affiliate_url"):
                st.caption(f"アフィリエイトURL: `{p['affiliate_url']}`")

            st.divider()

            # GPT Image（文字あり）
            st.subheader("🖼️ GPT Image プロンプト（文字あり）")
            st.caption(f"ChatGPTにせなっち写真＋商品写真を添付 → `images/{today}.png` として保存")
            st.code(p.get("gpt_image_prompt", ""), language=None)

            st.divider()

            # GPT Image（文字なし）
            st.subheader("🖼️ GPT Image プロンプト（文字なし）")
            st.caption(f"InsMind動画用 → `images/{today}_video.png` として保存")
            st.code(p.get("gpt_image_prompt_notxt", ""), language=None)

            st.divider()

            # InsMind
            st.subheader("🎬 InsMind 動画プロンプト")
            st.caption("文字なし画像をInsMindにアップロードして使用")
            st.code(p.get("video_prompt", ""), language=None)

        if scripts:
            st.divider()
            for s in scripts:
                ctype = s.get("type", "")
                captions = s.get("captions", {})

                if ctype == "threads_product":
                    st.subheader("🧵 Threads ① 商品投稿")
                    st.code(captions.get("threads", ""), language=None)

                elif ctype == "threads_buzz":
                    st.subheader("🧵 Threads ② バズ投稿")
                    st.caption(f"テーマ: {s.get('theme', '')}")
                    st.code(captions.get("threads", ""), language=None)

                elif ctype == "reel":
                    st.subheader("📱 Instagram Reel キャプション")
                    st.code(captions.get("instagram", ""), language=None)
                    st.subheader("🧵 Threads 動画投稿キャプション")
                    st.code(captions.get("threads", ""), language=None)

                st.divider()


# ──────────────────────────────────────────────────────
# TAB 3: 投稿
# ──────────────────────────────────────────────────────
with tab3:
    st.header("投稿")

    if not st.session_state.generated:
        st.info("「生成」タブでコンテンツを生成してください。")
    else:
        # ── ファイルアップロード
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🖼️ 画像アップロード")
            st.caption("ChatGPTで生成した画像（PNG）")
            image_file = st.file_uploader(
                "画像を選択", type=["png", "jpg", "jpeg"], key="img_uploader"
            )
            if image_file:
                st.image(image_file, width=280)
                if not st.session_state.image_url:
                    if st.button("Cloudinaryにアップロード", key="btn_img", use_container_width=True):
                        with st.spinner("アップロード中..."):
                            from utils.cloudinary_helper import upload_bytes
                            url = upload_bytes(image_file.read(), resource_type="image")
                        if url:
                            st.session_state.image_url = url
                            st.success("✅ 画像アップロード完了")
                            st.rerun()
                        else:
                            st.error("アップロードに失敗しました")
                else:
                    st.success("✅ アップロード済み")

        with col2:
            st.subheader("🎬 動画アップロード")
            st.caption("InsMindで生成した動画（MP4）")
            video_file = st.file_uploader(
                "動画を選択", type=["mp4", "mov"], key="vid_uploader"
            )
            if video_file:
                st.video(video_file)
                if not st.session_state.video_url:
                    if st.button("Cloudinaryにアップロード", key="btn_vid", use_container_width=True):
                        with st.spinner("アップロード中（動画は数分かかります）..."):
                            from utils.cloudinary_helper import upload_bytes
                            url = upload_bytes(video_file.read(), resource_type="video")
                        if url:
                            st.session_state.video_url = url
                            st.success("✅ 動画アップロード完了")
                            st.rerun()
                        else:
                            st.error("アップロードに失敗しました")
                else:
                    st.success("✅ アップロード済み")

        st.divider()

        # ── 投稿ボタン
        post_time = (datetime.now() + timedelta(minutes=3)).strftime("%H:%M")
        st.subheader(f"📤 Buffer投稿（約3分後 {post_time} に自動投稿）")

        col3, col4 = st.columns(2)

        with col3:
            btn_label = "✅ Threads投稿済み" if st.session_state.threads_posted else "🧵 Threadsに投稿"
            if st.button(btn_label, type="primary", use_container_width=True,
                         disabled=st.session_state.threads_posted):
                with st.spinner("Bufferに予約中..."):
                    from agents.buffer_agent import run as buf_run
                    results = buf_run(
                        [s.copy() for s in st.session_state.scripts],
                        platforms=["threads"]
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
                         for r in results if r.get("buffer_posts")), ""
                    )
                    st.error(f"失敗: {err}")

        with col4:
            if not st.session_state.video_url:
                st.button("📱 Instagramに投稿", use_container_width=True, disabled=True)
                st.caption("⚠️ 先に動画をアップロードしてください")
            else:
                btn_label2 = "✅ Instagram投稿済み" if st.session_state.instagram_posted else "📱 Instagramに投稿"
                if st.button(btn_label2, type="primary", use_container_width=True,
                             disabled=st.session_state.instagram_posted):
                    with st.spinner("Bufferに予約中..."):
                        from agents.buffer_agent import run as buf_run
                        results = buf_run(
                            [s.copy() for s in st.session_state.scripts],
                            video_url=st.session_state.video_url,
                            platforms=["instagram"]
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
                             for r in results if r.get("buffer_posts")), ""
                        )
                        st.error(f"失敗: {err}")


# ──────────────────────────────────────────────────────
# TAB 4: 投稿履歴
# ──────────────────────────────────────────────────────
with tab4:
    st.header("投稿履歴")

    if st.button("履歴を読み込む", use_container_width=True):
        with st.spinner("Google Sheetsから取得中..."):
            from utils.sheets_helper import get_history
            df = get_history()

        if df is None:
            st.error("Google Sheetsの設定を確認してください（GOOGLE_CREDENTIALS_JSON / GOOGLE_SHEETS_ID）")
        elif df.empty:
            st.info("履歴データがまだありません。")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"合計 {len(df)} 件")
