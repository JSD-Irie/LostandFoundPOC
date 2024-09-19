namespace MaterializedViews {

    public class LostItem {    
        public string id { get; set; }  = Guid.NewGuid().ToString();
        public string Municipality { get; set; }  = default!; // 市区町村
        public string Subcategory { get; set; } = default!; // 中分類（例: 手提げかばん、財布）
        public DateTime DateFound {get; set;} = DateTime.UtcNow; // 拾得日
        public string Description { get; set; } = default!; // 忘れ物の説明
        public string ContactInfo { get; set; } = default!; // 問い合わせ先
    }

    public class LostItemHelper {

        // 10種類の中分類（忘れ物の種類） - 日本語のみ
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

        // 10種類の市区町村
        internal static List<string> Municipalities = new List<string>{
            "札幌市白石区", 
            "札幌市中央区", 
            "札幌市豊平区", 
            "旭川市", 
            "函館市",
            "小樽市", 
            "千歳市", 
            "苫小牧市", 
            "室蘭市", 
            "北見市"
        };

        public static LostItem GenerateLostItem() {
            var lostItem = new LostItem();
            Random random = new Random();

            // 市区町村をランダムに選択
            lostItem.Municipality = Municipalities[random.Next(Municipalities.Count)];
            // 日本語の中分類をランダムに選択
            lostItem.Subcategory = Subcategories[random.Next(Subcategories.Count)];
            // 説明文の生成
            lostItem.Description = $"{lostItem.Subcategory}が見つかりました。";
            // 問い合わせ先の例
            lostItem.ContactInfo = "問い合わせ先: 011-814-0110";

            return lostItem;
        }
    }
}
