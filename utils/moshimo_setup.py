"""
もしもアフィリエイト ID抽出ツール

使い方:
  python utils/moshimo_setup.py

もしも管理画面から広告リンクURLを2つ貼り付けるだけで
.env / Streamlit Secrets 用のテキストを自動生成します。
"""
from urllib.parse import urlparse, parse_qs


def extract_ids(url: str) -> dict:
    """もしもアフィリエイトURLからパラメータを抽出"""
    qs = parse_qs(urlparse(url).query)
    return {
        "a_id":  qs.get("a_id",  [""])[0],
        "p_id":  qs.get("p_id",  [""])[0],
        "pc_id": qs.get("pc_id", [""])[0],
        "pl_id": qs.get("pl_id", [""])[0],
    }


def main():
    print("=" * 60)
    print("  もしもアフィリエイト ID抽出ツール")
    print("=" * 60)
    print()
    print("【手順】")
    print("  もしも管理画面 → 広告を探す → 楽天/Amazonを検索")
    print("  → 提携済みプログラムを選択 → 広告リンクを表示")
    print("  → リンクHTMLの href= 部分のURLをコピーして貼り付け")
    print()

    # ---------- 楽天 ----------
    print("▼ 楽天の広告リンクURL を貼り付けてください（Enterで確定）:")
    rakuten_url = input("  楽天URL > ").strip()
    r = extract_ids(rakuten_url)

    if not r["a_id"]:
        print("  ⚠️  URLからIDを取得できませんでした。URLを確認してください。")
        r = {k: "（取得失敗）" for k in r}

    # ---------- Amazon ----------
    print()
    print("▼ Amazonの広告リンクURL を貼り付けてください（Enterで確定）:")
    amazon_url = input("  AmazonURL > ").strip()
    a = extract_ids(amazon_url)

    if not a["a_id"]:
        print("  ⚠️  URLからIDを取得できませんでした。URLを確認してください。")
        a = {k: "（取得失敗）" for k in a}

    # ---------- 結果表示 ----------
    print()
    print("=" * 60)
    print("  ✅ 抽出結果")
    print("=" * 60)

    env_block = f"""
# もしもアフィリエイト
MOSHIMO_A_ID="{r['a_id']}"
MOSHIMO_RAKUTEN_P_ID="{r['p_id']}"
MOSHIMO_RAKUTEN_PC_ID="{r['pc_id']}"
MOSHIMO_RAKUTEN_PL_ID="{r['pl_id']}"
MOSHIMO_AMAZON_P_ID="{a['p_id']}"
MOSHIMO_AMAZON_PC_ID="{a['pc_id']}"
MOSHIMO_AMAZON_PL_ID="{a['pl_id']}"
""".strip()

    toml_block = f"""
# Streamlit Secrets (secrets.toml) に貼り付け
MOSHIMO_A_ID = "{r['a_id']}"
MOSHIMO_RAKUTEN_P_ID = "{r['p_id']}"
MOSHIMO_RAKUTEN_PC_ID = "{r['pc_id']}"
MOSHIMO_RAKUTEN_PL_ID = "{r['pl_id']}"
MOSHIMO_AMAZON_P_ID = "{a['p_id']}"
MOSHIMO_AMAZON_PC_ID = "{a['pc_id']}"
MOSHIMO_AMAZON_PL_ID = "{a['pl_id']}"
""".strip()

    print()
    print("【.env ファイル用】")
    print(env_block)
    print()
    print("【Streamlit Secrets (secrets.toml) 用】")
    print(toml_block)

    # .env に書き込むか確認
    print()
    ans = input("📝 .env ファイルに追記しますか？ [y/N] > ").strip().lower()
    if ans == "y":
        with open(".env", "a", encoding="utf-8") as f:
            f.write("\n" + env_block + "\n")
        print("✅ .env に追記しました。")
    else:
        print("スキップしました。上のテキストを手動でコピーしてください。")

    print()
    print("Streamlit Cloud の場合は：")
    print("  アプリ管理画面 → Settings → Secrets に上の TOML 形式を貼り付け")


if __name__ == "__main__":
    main()
