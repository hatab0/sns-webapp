"""
Amazon Creators API エージェント（PA-API v5廃止対応）
ベビー商品を検索してアフィリエイトリンク付きで返す。
rakuten_agent と同一フォーマットのリストを返すため analyzer_agent に直接渡せる。

必要な環境変数:
  AMAZON_ACCESS_KEY   : Creators API アクセスキー
  AMAZON_SECRET_KEY   : Creators API シークレットキー
  AMAZON_PARTNER_TAG  : アソシエイト トラッキングID（例: yoursite-22）

注意:
  - Amazon Creators API は30日間売上ゼロだとAPIアクセスが停止される
  - FEリージョン（日本）は credential_version="2.3" が必須
  - pip install amazon-creatorsapi-python-sdk が必要
"""
import os
from dotenv import load_dotenv

load_dotenv()

BABY_KEYWORDS_AMAZON = [
    "ベビーモニター カメラ",
    "抱っこ紐 新生児",
    "ベビーチェア テーブル",
    "哺乳瓶 消毒",
    "赤ちゃん おもちゃ 知育",
    "ベビーカー 軽量",
    "チャイルドシート 新生児",
    "赤ちゃん 保湿クリーム",
]


def is_configured() -> bool:
    return all([
        os.getenv("AMAZON_ACCESS_KEY"),
        os.getenv("AMAZON_SECRET_KEY"),
        os.getenv("AMAZON_PARTNER_TAG"),
    ])


def run(keywords: list = None, max_per_keyword: int = 3) -> list:
    """
    Amazon商品を検索して返す。
    戻り値は rakuten_agent と同一フォーマット（source="amazon" キー付き）。
    """
    if not is_configured():
        print("⚠️  Amazon Creators API 認証情報が未設定（AMAZON_ACCESS_KEY 等）")
        return []

    try:
        from creatorsapi import AmazonCreatorsApi
        from creatorsapi.models import SearchItemsRequest, SearchItemsResource
    except ImportError:
        print("⚠️  amazon-creatorsapi-python-sdk が未インストール（pip install amazon-creatorsapi-python-sdk）")
        return []

    from utils.moshimo_helper import wrap_amazon

    api = AmazonCreatorsApi(
        access_key=os.getenv("AMAZON_ACCESS_KEY"),
        secret_key=os.getenv("AMAZON_SECRET_KEY"),
        partner_tag=os.getenv("AMAZON_PARTNER_TAG"),
        marketplace="www.amazon.co.jp",
        credential_version="2.3",  # FEリージョン（日本）必須
    )

    search_keywords = keywords or BABY_KEYWORDS_AMAZON
    products = []

    for keyword in search_keywords[:6]:
        try:
            req = SearchItemsRequest(
                keywords=keyword,
                search_index="Baby",
                resources=[
                    SearchItemsResource.ITEMINFO_TITLE,
                    SearchItemsResource.OFFERS_LISTINGS_PRICE,
                    SearchItemsResource.IMAGES_PRIMARY_LARGE,
                    SearchItemsResource.ITEMINFO_PRODUCTINFO,
                    SearchItemsResource.CUSTOMERREVIEWS_COUNT,
                    SearchItemsResource.CUSTOMERREVIEWS_STARRATING,
                ],
                item_count=max_per_keyword,
            )
            resp = api.search_items(req)
            if not resp.search_result:
                continue

            for item in resp.search_result.items:
                # 価格
                price = 0
                if item.offers and item.offers.listings:
                    amt = item.offers.listings[0].price.amount
                    try:
                        price = int(float(amt))
                    except (TypeError, ValueError):
                        price = 0

                # レビュー
                review_count = 0
                review_avg = 0.0
                try:
                    if item.customer_reviews:
                        review_count = int(item.customer_reviews.count or 0)
                        review_avg = float(item.customer_reviews.star_rating.value or 0)
                except Exception:
                    pass

                # 画像
                image_url = ""
                try:
                    if item.images and item.images.primary and item.images.primary.large:
                        image_url = item.images.primary.large.url
                except Exception:
                    pass

                # アフィリエイトURL（もしもでラップ）
                base_url = item.detail_page_url or ""
                affiliate_url = wrap_amazon(base_url) if base_url else ""

                products.append({
                    "name": (item.item_info.title.display_value
                             if item.item_info and item.item_info.title else "Amazon商品"),
                    "price": price,
                    "url": base_url,
                    "affiliate_url": affiliate_url or base_url,
                    "image_url": image_url,
                    "shop_name": "Amazon",
                    "item_code": f"amz_{item.asin}",
                    "review_count": review_count,
                    "review_average": review_avg,
                    "catch_copy": "",
                    "description": "",
                    "keyword": keyword,
                    "source": "amazon",
                })
        except Exception as e:
            print(f"  Amazon検索エラー ({keyword}): {e}")

    print(f"✅ Amazon: {len(products)} 件取得")
    return products
