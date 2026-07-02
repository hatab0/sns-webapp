# Baby Boo SNS管理アプリ — Claude向け知識ベース

## プロジェクト概要
AIで生成した赤ちゃん「せなっち」の画像・動画をInstagram/TikTok/YouTubeへ自動投稿するStreamlitアプリ。
- せなっちは**実在する子供**。プライバシー保護のためAI画像を使用。
- 運営者は**二次のパパ**（育休中）。
- 収益化はRakuten ROOMアフィリエイト＋将来的に自社商品販売。

## ターゲット戦略
| 媒体 | 言語 | 対象 |
|---|---|---|
| Instagram | 英語メイン + 日本語説明 | 海外（北米）|
| YouTube | 英語全体 | 海外（北米）|
| TikTok | 日本語 + 英語一言 | 国内 |

## ファイル構成
```
app.py                        # Streamlit メインUI
agents/
  image_agent.py              # GPT Image 2プロンプト生成・バズmodeシーン管理
  instagram_agent.py          # Instagram/TikTokキャプション生成
  youtube_agent.py            # YouTube Shortsキャプション生成（英語）
  buffer_agent.py             # Buffer API予約投稿（Instagram/YouTube）
  rakuten_agent.py            # 楽天商品取得・アフィリエイトURL生成
  analyzer_agent.py           # 商品分析
  writer_agent.py             # 通常mode商品紹介スクリプト生成
  quality_agent.py            # コンテンツ品質チェック
utils/
  baby_config.py              # せなっちの生年月日・月齢計算
  sheets_helper.py            # Google Sheets読み書き（履歴・buzz_history等）
  cloudinary_helper.py        # 動画アップロード
  seasonal_events.py          # 季節イベント定義
```

## 投稿モード
| モード | 説明 | 商品 |
|---|---|---|
| **バズmode** | フォロワー獲得特化。せなっちのかわいい瞬間 | なし |
| **通常mode** | 楽天商品紹介。アフィリエイト収益化 | あり |
| **マイルストーン** | 週1成長記録。毎週固定 | なし |

## キャプション構成（最新）

### Instagram
| モード | 言語 | 構成 | ハッシュタグ |
|---|---|---|---|
| バズ | 英語 | プールからランダム一言 | `#baby #babyboo #babylove #cutebaby #kawaii` |
| 通常 | 英語+日本語 | 英語hook → 🇯🇵日本語商品説明 | `#babyboo #baby #PR #育児 #赤ちゃんのいる生活` |
| マイルストーン | 英語 | 週次成長記録 | `#baby #babyboo #babymonths #babygrowth #{月齢}monthsold` |

### TikTok
| モード | 言語 | 構成 | ハッシュタグ |
|---|---|---|---|
| バズ | 日本語+英語一言 | 日本語本文 → 英語プール一言 | `#赤ちゃん #育児vlog #babyboo #赤ちゃんのいる暮らし #育休パパ` |
| 通常 | 日本語+英語一言 | 同上 | 同上 + `#PR` |
| マイルストーン | 日本語 | 固定文 | `#赤ちゃん #育児vlog #babyboo #赤ちゃんのいる暮らし #生後{月齢}ヶ月` |

### YouTube
| モード | 言語 | 構成 | ハッシュタグ |
|---|---|---|---|
| バズ | 英語 | kawaii+Japanese dad角度 タイトル+説明 | `#Shorts #cutebaby #kawaii #baby #babyboo` |
| 通常 | 英語+日本語 | 英語商品紹介 → 🇯🇵日本語商品説明 | `#Shorts #baby #babyboo #PR #babyproducts` |
| マイルストーン | 英語 | 週次成長記録 | `#Shorts #baby #babyboo #babymonths #babygrowth` |

## 画像生成（バズmode）
- モデル: ChatGPT GPT Image 2
- スタイル: baby_cubo_official参考。iPhoneで撮ったようなリアルな写真
- 照明: 窓からの自然光・ゴールデンライティング固定
- 表情優先: ぽかん顔40% / ガグ20% / その他40%
- **帽子必須**（常にニット帽やビーニーを着用）
- プールサイズ: 衣装49種(window=7) / 背景13種(window=5) / アクセサリー13種(window=5)
- 選択履歴はGoogle Sheets `buzz_history` シートに永続保存

## Buffer投稿スケジュール（JST）
| 媒体 | 投稿時間（JST）| 対応時間帯 |
|---|---|---|
| Instagram | 01:00 / 09:00 / 11:00 | EDT 12:00 / 20:00 / 22:00（北米ピーク）|
| TikTok | 12:00 / 15:00 / 18:00 / 19:00 / 21:00 | 国内ピーク |
| YouTube | 12:00 / 20:00 / 22:00 | 国内ピーク |

## Google Sheets構成
| シート | 用途 |
|---|---|
| メインシート（GID: 748487579）| 商品履歴・投稿カウント |
| `buzz_history` | バズmode衣装/背景/ポーズの選択履歴（重複防止）|
| `hashtags` | ハッシュタグ管理（現在未使用・コードに直書き）|
| `senacchi_profile` | せなっちの基準写真URL（月齢別）|
| `post_metrics` | 投稿ごとの成果記録（投稿時に自動で行追加、数字は週1手入力）|
| `follower_history` | フォロワー数の推移（週1手入力、同日は上書き）|

## 開発ルール
- バズmodeへの変更は `image_agent.py` と `instagram_agent.py` のバズmode関連のみ
- TikTokキャプションは日本語のまま変更しない
- ハッシュタグはコードに直書き（Sheets管理廃止）
- 変更後は必ず `git push origin main`
- コメントは書かない。書くなら「なぜ」のみ

## 将来の自動化ロードマップ
1. **Phase 1（完了）**: Streamlitアプリによる半自動化
2. **Phase 2（進行中）**: CLAUDE.md + カスタムコマンド + Cron自動生成
3. **Phase 3（予定）**: MCP経由でCloudinary/Buffer直接制御。人間レビュー後に自動投稿
4. **Phase 4（予定）**: Kling AI API対応。動画生成まで完全自動化
