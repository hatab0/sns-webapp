#!/usr/bin/env python3
"""
Baby Boo SNS CLI — 対話式コンテンツ生成・投稿ツール

使い方:
  python cli/run.py               # 対話式で生成・投稿
  python cli/run.py --post FILE   # pendingファイルを読み込んで投稿
  python cli/run.py --list        # pending一覧を表示
"""
import sys
import os
import json
import argparse
import textwrap
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

PENDING_DIR = Path(__file__).parent / "pending"
PENDING_DIR.mkdir(exist_ok=True)


# ── 表示ヘルパー ──────────────────────────────────────────

def header():
    console.print(Panel.fit(
        "[bold cyan]Baby Boo SNS CLI[/bold cyan]  🍼\n"
        "[dim]Streamlitなしで生成・レビュー・投稿できます[/dim]",
        border_style="cyan",
    ))


def ask(prompt: str, default: str = None) -> str:
    return Prompt.ask(f"[bold]{prompt}[/bold]", default=default)


def confirm(prompt: str, default: bool = True) -> bool:
    return Confirm.ask(f"[bold]{prompt}[/bold]", default=default)


def show_captions(script: dict):
    captions = script.get("captions", {})

    if captions.get("instagram"):
        console.print(Panel(
            captions["instagram"],
            title="[bold]Instagram[/bold]",
            border_style="magenta",
            padding=(1, 2),
        ))

    if captions.get("tiktok"):
        console.print(Panel(
            captions["tiktok"],
            title="[bold]TikTok[/bold]",
            border_style="red",
            padding=(1, 2),
        ))

    if captions.get("youtube_title"):
        yt_body = f"[bold]タイトル:[/bold] {captions['youtube_title']}\n\n{captions.get('youtube', '')}"
        console.print(Panel(
            yt_body,
            title="[bold]YouTube[/bold]",
            border_style="red3",
            padding=(1, 2),
        ))


# ── モード選択 ────────────────────────────────────────────

def select_mode() -> str:
    console.print("\n[bold]投稿モードを選択:[/bold]")
    console.print("  [cyan]1[/cyan]  バズmode  — フォロワー獲得特化")
    console.print("  [cyan]2[/cyan]  通常mode  — 楽天商品紹介（#PR）")
    console.print("  [cyan]3[/cyan]  マイルストーン — 週次成長記録")
    choice = Prompt.ask("\n選択", choices=["1", "2", "3"])
    return {"1": "buzz", "2": "normal", "3": "milestone"}[choice]


# ── 商品情報（通常modeのみ）────────────────────────────────

def get_product() -> dict:
    console.print("\n[bold]商品情報を入力してください[/bold]  ([dim]Enterでスキップ可[/dim])")
    name      = ask("商品名（日本語）")
    catch_copy = ask("キャッチコピー / 一言説明", default="")
    url       = ask("楽天ROOMのURL", default="")
    return {"name": name, "catch_copy": catch_copy, "url": url}


# ── コンテンツ生成 ─────────────────────────────────────────

def generate(mode: str, product: dict = None) -> dict:
    from agents.instagram_agent import run as ig_run, run_buzz as ig_run_buzz
    from agents.youtube_agent import run as yt_run

    with console.status("[bold cyan]キャプション生成中...[/bold cyan]", spinner="dots"):
        if mode == "buzz":
            script = ig_run_buzz()
        elif mode == "milestone":
            script = ig_run_buzz(is_milestone=True)
        else:
            script = ig_run(product=product)

        script = yt_run(script, product=product)

    return script


# ── キャプション編集 ──────────────────────────────────────

def edit_captions(script: dict) -> dict:
    captions = script.setdefault("captions", {})
    platforms = [k for k in ["instagram", "tiktok", "youtube", "youtube_title"] if captions.get(k)]

    console.print("\n[bold]編集するキャプションを選択（複数可: 1,2 など / Enterでスキップ）:[/bold]")
    label_map = {
        "instagram":    "Instagram",
        "tiktok":       "TikTok",
        "youtube":      "YouTube 説明文",
        "youtube_title": "YouTube タイトル",
    }
    for i, key in enumerate(platforms, 1):
        console.print(f"  [cyan]{i}[/cyan]  {label_map[key]}")

    raw = Prompt.ask("選択", default="")
    if not raw.strip():
        return script

    selected_indices = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(platforms):
                selected_indices.append(idx)

    for idx in selected_indices:
        key = platforms[idx]
        console.print(f"\n[dim]現在の {label_map[key]}:[/dim]")
        console.print(captions[key])
        console.print("\n[dim]新しいテキストを入力（複数行は \\n で改行）:[/dim]")
        new_text = input("> ").replace("\\n", "\n").strip()
        if new_text:
            captions[key] = new_text

    return script


# ── pending保存・一覧 ─────────────────────────────────────

def save_pending(script: dict, mode: str, video_url: str = None) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    fpath = PENDING_DIR / f"{ts}_{mode}.json"
    data = {
        "generated_at": ts,
        "mode": mode,
        "video_url": video_url,
        "script": script,
    }
    fpath.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return fpath


def load_pending(fpath: Path) -> dict:
    return json.loads(fpath.read_text())


def list_pending():
    files = sorted(PENDING_DIR.glob("*.json"), reverse=True)
    if not files:
        console.print("[dim]pendingファイルはありません[/dim]")
        return

    table = Table(title="Pending コンテンツ一覧", box=box.SIMPLE_HEAVY)
    table.add_column("No.", style="cyan", width=4)
    table.add_column("ファイル名", style="white")
    table.add_column("モード", style="magenta")
    table.add_column("生成日時", style="dim")
    table.add_column("動画URL", style="dim")

    for i, f in enumerate(files, 1):
        try:
            data = json.loads(f.read_text())
            table.add_row(
                str(i),
                f.name,
                data.get("mode", "?"),
                data.get("generated_at", "?"),
                "あり" if data.get("video_url") else "なし",
            )
        except Exception:
            table.add_row(str(i), f.name, "?", "?", "?")

    console.print(table)


# ── 動画アップロード ──────────────────────────────────────

def upload_video() -> str | None:
    console.print("\n[bold]動画ファイルをアップロード[/bold]  ([dim]スキップは Enter[/dim])")
    raw = Prompt.ask("動画ファイルのパス", default="")
    if not raw.strip():
        return None

    fpath = Path(raw.strip().strip('"').strip("'"))
    if not fpath.exists():
        console.print(f"[red]ファイルが見つかりません: {fpath}[/red]")
        return None

    from utils.cloudinary_helper import upload_bytes
    with console.status("[bold]Cloudinaryにアップロード中...[/bold]"):
        url = upload_bytes(fpath.read_bytes(), resource_type="video")

    if url:
        console.print(f"[green]✅ アップロード完了[/green]  [dim]{url}[/dim]")
    else:
        console.print("[red]❌ アップロード失敗[/red]")
    return url or None


# ── 媒体選択 ───────────────────────────────────────────────

def select_platforms() -> list[str]:
    console.print("\n[bold]投稿する媒体を選択[/bold]  ([dim]例: 1,3  / Enter で全て[/dim])")
    console.print("  [cyan]1[/cyan]  Instagram")
    console.print("  [cyan]2[/cyan]  TikTok")
    console.print("  [cyan]3[/cyan]  YouTube")
    raw = Prompt.ask("選択", default="1,2,3")
    mapping = {"1": "instagram", "2": "tiktok", "3": "youtube"}
    result = [mapping[c.strip()] for c in raw.split(",") if c.strip() in mapping]
    return result or ["instagram", "tiktok", "youtube"]


# ── Buffer投稿 ────────────────────────────────────────────

def post_to_buffer(script: dict, video_url: str, platforms: list[str]):
    from agents.buffer_agent import run as buf_run

    with console.status("[bold]Bufferに予約投稿中...[/bold]"):
        results = buf_run([script], video_url=video_url, platforms=platforms)

    table = Table(title="投稿結果", box=box.SIMPLE_HEAVY)
    table.add_column("媒体", style="cyan")
    table.add_column("結果", style="white")
    table.add_column("予約日時 (JST)", style="dim")

    for res in results:
        for platform, r in res.get("buffer_posts", {}).items():
            if r.get("success"):
                table.add_row(platform, "[green]✅ 成功[/green]", r.get("scheduled_at", "?"))
            else:
                table.add_row(platform, f"[red]❌ {r.get('error', '不明')}[/red]", "—")

    console.print(table)


# ── メインフロー ──────────────────────────────────────────

def flow_generate():
    """対話式 生成 → レビュー → 投稿 フロー"""
    mode = select_mode()

    product = None
    if mode == "normal":
        product = get_product()

    script = generate(mode, product)

    while True:
        console.print()
        show_captions(script)

        console.print("\n[bold]次のアクション:[/bold]")
        console.print("  [cyan]1[/cyan]  このまま投稿へ進む")
        console.print("  [cyan]2[/cyan]  キャプションを編集する")
        console.print("  [cyan]3[/cyan]  Pendingに保存してあとで投稿")
        console.print("  [cyan]4[/cyan]  キャプションをやり直す（再生成）")
        console.print("  [cyan]5[/cyan]  キャンセル")

        action = Prompt.ask("選択", choices=["1", "2", "3", "4", "5"])

        if action == "2":
            script = edit_captions(script)
            continue

        if action == "4":
            console.print()
            script = generate(mode, product)
            continue

        if action == "3":
            fpath = save_pending(script, mode)
            console.print(f"\n[green]✅ 保存しました:[/green] {fpath}")
            console.print(f"[dim]あとで投稿するとき: python cli/run.py --post {fpath.name}[/dim]")
            return

        if action == "5":
            console.print("[dim]キャンセルしました[/dim]")
            return

        break  # action == "1"

    video_url = upload_video()
    platforms = select_platforms()

    console.print()
    labels = ", ".join(platforms)
    if not confirm(f"[{labels}] に予約投稿しますか？"):
        fpath = save_pending(script, mode, video_url)
        console.print(f"[green]✅ pendingに保存しました:[/green] {fpath}")
        return

    post_to_buffer(script, video_url, platforms)


def flow_post(filename: str):
    """--post: pendingファイルを読み込んで投稿"""
    fpath = PENDING_DIR / filename if not Path(filename).is_absolute() else Path(filename)
    if not fpath.exists():
        console.print(f"[red]ファイルが見つかりません: {fpath}[/red]")
        return

    data = load_pending(fpath)
    script = data["script"]
    mode = data.get("mode", "?")
    existing_url = data.get("video_url")

    console.print(f"\n[bold]Pending: {fpath.name}[/bold]  mode=[cyan]{mode}[/cyan]")
    show_captions(script)

    if existing_url:
        console.print(f"\n[green]動画URL（保存済み）:[/green] [dim]{existing_url}[/dim]")
        use_existing = confirm("この動画URLで投稿しますか？")
        video_url = existing_url if use_existing else upload_video()
    else:
        video_url = upload_video()

    platforms = select_platforms()

    if not confirm(f"[{', '.join(platforms)}] に予約投稿しますか？"):
        console.print("[dim]キャンセルしました[/dim]")
        return

    post_to_buffer(script, video_url, platforms)

    if confirm("投稿完了。このpendingファイルを削除しますか？"):
        fpath.unlink()
        console.print("[dim]削除しました[/dim]")


# ── エントリポイント ──────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Baby Boo SNS CLI")
    parser.add_argument("--post",  metavar="FILE",  help="pendingファイルを投稿")
    parser.add_argument("--list",  action="store_true", help="pending一覧を表示")
    args = parser.parse_args()

    header()

    if args.list:
        list_pending()
    elif args.post:
        flow_post(args.post)
    else:
        flow_generate()


if __name__ == "__main__":
    main()
