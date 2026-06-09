# /status

Baby Boo SNSアカウントの現在状況をまとめて表示する。

## 引数
なし

## 実行手順

1. `utils/sheets_helper.py` の関数一覧を確認する

2. 以下の情報をコードベースから読み取る
   - `utils/baby_config.py`: せなっちの現在の月齢
   - `agents/image_agent.py`: 現在の衣装プール・背景プールのサイズ
   - `agents/instagram_agent.py`: キャプションプールのサイズ

3. git logで直近の変更を確認する (`git log --oneline -10`)

4. 以下の形式でまとめて表示する

```
## Baby Boo SNS 現在状況
📅 今日: [日付]
👶 せなっちの月齢: [X]ヶ月

## コードベース
- 衣装プール: XX種
- 背景プール: XX種
- Instagram英語一言プール: XX種
- TikTok英語一言プール: XX種

## 直近の変更（git log）
[直近10件]

## 次にやること
[CLAUDE.mdの将来ロードマップから現在フェーズを確認して表示]
```

## 用途
- 定期的な状況把握
- 新しいセッション開始時の確認
- 自動化の進捗確認
