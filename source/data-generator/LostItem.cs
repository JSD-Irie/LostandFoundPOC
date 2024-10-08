using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace MaterializedViews
{
    /// <summary>
    /// 忘れ物の基本情報を表すクラス
    /// </summary>
    public class LostItem
    {
        [JsonProperty("id")]
        public string Id { get; set; } = Guid.NewGuid().ToString(); // 一意のID

        [JsonProperty("createUserPlace")] // 小文字スタートで設定
        public string CreateUserPlace { get; set; } = default!; // 市区町村（必須）

        [JsonProperty("createUserID")]
        public string? CreateUserID { get; set; } // 作成ユーザーID（オプショナル）

        [JsonProperty("dateFound")]
        public DateTime DateFound { get; set; } = DateTime.UtcNow; // 拾得日（必須）

        [JsonProperty("dateUpdated")]
        public DateTime? DateUpdated { get; set; } // 更新日時（オプショナル）

        [JsonProperty("memo")]
        public string? Memo { get; set; } // メモ（オプショナル）

        [JsonProperty("contact")]
        public string? Contact { get; set; } // 連絡先（オプショナル）

        [JsonProperty("color")]
        public Color? Color { get; set; } // カラー情報（オプショナル）

        [JsonProperty("currency")]
        public Currency? Currency { get; set; } // 通貨情報（オプショナル）

        [JsonProperty("findPlace")]
        public string? FindPlace { get; set; } // 発見場所（オプショナル）

        [JsonProperty("imageUrl")]
        public List<string> ImageUrl { get; set; } = new List<string>(); // 画像URL（オプショナル）

        [JsonProperty("isValuables")]
        public bool? IsValuables { get; set; } // 貴重品かどうか（オプショナル）

        [JsonProperty("item")]
        public Item? Item { get; set; } // アイテム情報（オプショナル）

        [JsonProperty("keyword")]
        public List<string> Keyword { get; set; } = new List<string>(); // キーワード（オプショナル）

        [JsonProperty("mngmtNo")]
        public string? MngmtNo { get; set; } // 管理番号（オプショナル）

        [JsonProperty("personal")]
        public string? Personal { get; set; } // 個人情報（オプショナル）

        [JsonProperty("status")]
        public Status? Status { get; set; } // ステータス（オプショナル）
    }

    /// <summary>
    /// カラー情報を表すクラス
    /// </summary>
    public class Color
    {
        [JsonProperty("id")]
        public string Id { get; set; } = default!; // カラーID（必須）

        [JsonProperty("name")]
        public string Name { get; set; } = default!; // カラー名（必須）

        [JsonProperty("url")]
        public string Url { get; set; } = default!; // カラー画像URL（必須）
    }

    /// <summary>
    /// 通貨情報を表すクラス
    /// </summary>
    public class Currency
    {
        [JsonProperty("foreignCurrency")]
        public string? ForeignCurrency { get; set; } // 外貨（オプショナル）

        [JsonProperty("japaneseCurrency")]
        public List<JapaneseCurrency>? JapaneseCurrency { get; set; } // 日本円情報（オプショナル）
    }

    /// <summary>
    /// 日本円情報を表すクラス
    /// </summary>
    public class JapaneseCurrency
    {
        [JsonProperty("count")]
        public int Count { get; set; } // 数量（必須）

        [JsonProperty("id")]
        public string Id { get; set; } = default!; // 日本円ID（必須）
    }

    /// <summary>
    /// アイテム情報を表すクラス
    /// </summary>
    public class Item
    {
        [JsonProperty("categoryCode")]
        public string? CategoryCode { get; set; } // カテゴリコード（オプショナル）

        [JsonProperty("categoryName")]
        public string? CategoryName { get; set; } // カテゴリ名（オプショナル）

        [JsonProperty("itemName")]
        public string? ItemName { get; set; } // アイテム名（オプショナル）

        [JsonProperty("valuableFlg")]
        public int? ValuableFlg { get; set; } // 貴重フラグ（オプショナル）
    }

    /// <summary>
    /// ステータス情報を表すクラス
    /// </summary>
    public class Status
    {
        [JsonProperty("id")]
        public string Id { get; set; } = default!; // "hold" または "release"

        [JsonProperty("name")]
        public string Name { get; set; } = default!; // "保管中" または "返却済み"
    }

    /// <summary>
    /// 忘れ物データを生成するヘルパークラス
    /// </summary>
    public static class LostItemHelper
    {
        // 中分類のリスト
        internal static List<string> Subcategories = new List<string>{
            "手提げかばん",
            "財布",
            "傘",
            "時計",
            "メガネ",
            "携帯電話",
            "カメラ",
            "鍵",
            "本",
            "アクセサリー"
        };

        // 市区町村のリスト
        internal static List<string> Municipalities = new List<string>{
            "旭川市",
            "函館市",
            "小樽市",
            "千歳市",
            "苫小牧市",
            "室蘭市",
            "北見市"
        };

        // ステータスのリスト（限定された2種類）
        internal static List<Status> Statuses = new List<Status>{
            new Status { Id = "hold", Name = "保管中" },
            new Status { Id = "release", Name = "返却済み" },
            new Status { Id = "police", Name = "警察届出済" },
            new Status { Id = "discard", Name = "廃棄済み" }
        };

        // カラーのリスト
        internal static List<Color> Colors = new List<Color>{
            new Color { Id = "black", Name = "黒（ブラック）系", Url = "/colors/black.png" },
            new Color { Id = "red", Name = "赤（レッド）系", Url = "/colors/red.png" },
            new Color { Id = "blue", Name = "青（ブルー）系", Url = "/colors/blue.png" },
            new Color { Id = "green", Name = "緑（グリーン）系", Url = "/colors/green.png" },
            new Color { Id = "yellow", Name = "黄色（イエロー）系", Url = "/colors/yellow.png" },
            new Color { Id = "white", Name = "白（ホワイト）系", Url = "/colors/white.png" },
            new Color { Id = "gray", Name = "灰色（グレー）系", Url = "/colors/gray.png" },
            new Color { Id = "brown", Name = "茶色（ブラウン）系", Url = "/colors/brown.png" },
            new Color { Id = "purple", Name = "紫（パープル）系", Url = "/colors/purple.png" },
            new Color { Id = "pink", Name = "ピンク系", Url = "/colors/pink.png" },
            new Color { Id = "orange", Name = "オレンジ系", Url = "/colors/orange.png" }
        };

        // アイテムのリスト
        internal static List<Item> Items = new List<Item>{
            new Item { CategoryCode = "2601", CategoryName = "手提げかばん", ItemName = "トートバッグ", ValuableFlg = 1 },
            new Item { CategoryCode = "2602", CategoryName = "財布", ItemName = "二つ折り財布", ValuableFlg = 1 },
            new Item { CategoryCode = "2603", CategoryName = "傘", ItemName = "折りたたみ傘", ValuableFlg = 0 },
            new Item { CategoryCode = "2604", CategoryName = "時計", ItemName = "腕時計", ValuableFlg = 1 },
            new Item { CategoryCode = "2605", CategoryName = "メガネ", ItemName = "サングラス", ValuableFlg = 1 },
            new Item { CategoryCode = "2606", CategoryName = "携帯電話", ItemName = "スマートフォン", ValuableFlg = 1 },
            new Item { CategoryCode = "2607", CategoryName = "カメラ", ItemName = "デジタルカメラ", ValuableFlg = 1 },
            new Item { CategoryCode = "2608", CategoryName = "鍵", ItemName = "カギ", ValuableFlg = 0 },
            new Item { CategoryCode = "2609", CategoryName = "本", ItemName = "文庫本", ValuableFlg = 0 },
            new Item { CategoryCode = "2610", CategoryName = "アクセサリー", ItemName = "ネックレス", ValuableFlg = 1 }
        };

        // キーワードのリスト
        internal static List<string> Keywords = new List<string>{
            "ブランドロゴあり",
            "レンズ",
            "ファインダー",
            "シャッターボタン",
            "ダイヤル",
            "フラッシュ",
            "液晶ディスプレイ",
            "金属製",
            "黒色と銀色のデザイン",
            "レンズキャップ"
        };

        /// <summary>
        /// ランダムにLostItemオブジェクトを生成します。
        /// </summary>
        /// <returns>生成されたLostItemオブジェクト</returns>
        public static LostItem GenerateLostItem()
        {
            var lostItem = new LostItem();
            Random random = new Random();

            // 市区町村をランダムに選択
            lostItem.CreateUserPlace = Municipalities[random.Next(Municipalities.Count)];

            // サブカテゴリをランダムに選択
            string subcategory = Subcategories[random.Next(Subcategories.Count)];
            var selectedItem = Items[random.Next(Items.Count)];
            selectedItem.CategoryName = subcategory;
            lostItem.Item = selectedItem;

            // 説明文の生成
            lostItem.Memo = $"{subcategory}が見つかりました。";

            // 問い合わせ先の設定
            lostItem.Contact = "問い合わせ先: 011-814-0110";

            // 貴重品フラグをアイテムに基づいて設定
            lostItem.IsValuables = selectedItem.ValuableFlg == 1 ? true : false;

            // カラーをランダムに設定
            lostItem.Color = Colors[random.Next(Colors.Count)];

            // 通貨情報をランダムに設定
            if (random.NextDouble() > 0.5)
            {
                lostItem.Currency = new Currency
                {
                    ForeignCurrency = "USD",
                    JapaneseCurrency = new List<JapaneseCurrency>
                    {
                        new JapaneseCurrency { Count = random.Next(1, 1000), Id = "JPY" }
                    }
                };
            }

            // 発見場所をランダムに設定
            if (random.NextDouble() > 0.5)
            {
                lostItem.FindPlace = "待合室";
            }

            // 画像URLをランダムに追加
            if (random.NextDouble() > 0.3)
            {
                lostItem.ImageUrl.Add("image1.jpg");
                lostItem.ImageUrl.Add("image2.jpg");
            }

            // キーワードをランダムに追加
            int keywordCount = random.Next(1, 5);
            for (int i = 0; i < keywordCount; i++)
            {
                string keyword = Keywords[random.Next(Keywords.Count)];
                if (!lostItem.Keyword.Contains(keyword))
                {
                    lostItem.Keyword.Add(keyword);
                }
            }

            // 管理番号をランダムに設定
            lostItem.MngmtNo = Guid.NewGuid().ToString().Substring(0, 8);

            // 個人情報をランダムに設定
            if (random.NextDouble() > 0.7)
            {
                lostItem.Personal = "個人情報が含まれます。";
            }

            // ステータスをランダムに設定（限定された2種類）
            Status selectedStatus = Statuses[random.Next(Statuses.Count)];
            lostItem.Status = selectedStatus;

            return lostItem;
        }
    }
}
