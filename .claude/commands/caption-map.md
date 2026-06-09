# /caption-map

全媒体・全モードのキャプション構成を一覧表示する。コードを読んで最新の状態を確認する。

## 引数
なし（または媒体名: "instagram" / "tiktok" / "youtube"）

## 実行手順

1. 以下のファイルを読み込む
   - `agents/instagram_agent.py` — Instagram・TikTokキャプション
   - `agents/youtube_agent.py` — YouTubeキャプション

2. 各モードのキャプション構成を読み解き、以下の形式でまとめる

```
## Instagram
### バズmode
- キャプション: [構成]
- ハッシュタグ: [固定値]
- 生成方式: [プール/Claude API]

### 通常mode
...

### マイルストーン
...

## TikTok
...

## YouTube
...
```

3. プール（BUZZ_IG_ONELINER_POOL等）の現在の件数も表示する

## 用途
- どの媒体がどんなキャプションを生成するか把握したいとき
- CLAUDE.md の記載が古くなった場合の確認
- 新しい媒体追加前の現状把握
