# /new-product

新しい楽天商品をRakuten ROOMに追加し、通常modeで投稿準備を行う。

## 引数
`$ARGUMENTS` — 商品情報（例: "おむつ Merries さらさらエアスルー Lサイズ 54枚"）

## 実行手順

1. `agents/rakuten_agent.py` と `utils/sheets_helper.py` を読み込んで仕様確認

2. 商品情報から以下を整理する
   - 商品名（日本語）
   - カテゴリ推定（おむつ/ミルク/おもちゃ/スキンケア/離乳食/抱っこ紐/ベビーカー/その他）
   - せなっちの月齢との関連性コメント

3. ユーザーに以下を確認する
   - 楽天ROOMのアフィリエイトURLはすでにお持ちですか？
   - 商品の実際のレビュー・使用感を教えてください（キャプション生成に使います）

4. 確認後、通常modeで使えるよう `product` 辞書の雛形を提示する
   ```python
   {
       "name": "商品名",
       "category": "カテゴリ",
       "affiliate_url": "https://room.rakuten.co.jp/...",
       "user_review": "ユーザーのコメント",
       "month_age": 月齢数値
   }
   ```

5. Streamlitアプリを通常modeで起動して商品URLを入力するよう案内する

## 注意
- アフィリエイトURLは `moshimo_helper.py` を通じて生成する場合もある
- 商品はGoogle Sheets「メインシート」に記録される
- #PRハッシュタグは通常modeで自動付与される
