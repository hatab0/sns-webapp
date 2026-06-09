# /add-oneliner

InstagramまたはTikTokの英語一言プールに新しいフレーズを追加する。

## 引数
`$ARGUMENTS` — 追加したいフレーズ（例: "ig: This baby just made my whole week. 🥺" または "tiktok: Pure kawaii, no filter needed. 🇯🇵"）

## 実行手順

1. 引数の先頭が "ig:" か "tiktok:" かを確認する
   - `ig:` → `agents/instagram_agent.py` の `BUZZ_IG_ONELINER_POOL` に追加
   - `tiktok:` → `agents/instagram_agent.py` の `TIKTOK_EN_ONELINER_POOL` に追加
   - 指定なし → 両方のプールに追加を確認してからどちらか選択
2. 対象ファイルを読み込んで対象プールを見つける
3. フレーズを追加する
   - 末尾に絵文字があること
   - 既存フレーズと重複・類似しすぎないか確認
   - "kawaii" または日本語要素が入っているとベター
4. 追加したことをユーザーに報告する（プール名と総数）

## プールの特徴
- `BUZZ_IG_ONELINER_POOL`: Instagram向け。"kawaii", "Japan", "Japanese dad" のキーワード推奨
- `TIKTOK_EN_ONELINER_POOL`: TikTok向け。日本語コンテンツに添える一言。POV形式も可
