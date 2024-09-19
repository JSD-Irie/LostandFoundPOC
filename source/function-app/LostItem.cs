using System;

namespace MaterializedViews {

    // 忘れ物データクラス
    public class LostItem {    
        public string id { get; set; } = Guid.NewGuid().ToString();
        public string Municipality { get; set; } = default!; // 市区町村
        public string Subcategory { get; set; } = default!; // 中分類
        public DateTime DateFound { get; set; } = DateTime.UtcNow; // 拾得日
        public string Description { get; set; } = default!; // 説明
        public string ContactInfo { get; set; } = default!; // 問い合わせ先
    }

    // 忘れ物の中分類ごとのビュー
    public class LostItemBySubcategory {
        public string id { get; set; } = Guid.NewGuid().ToString();
        public string Subcategory { get; set; } = default!; // 中分類
        public string Municipality { get; set; } = default!; // 市区町村
        public DateTime DateFound { get; set; } // 拾得日
        public string Description { get; set; } = default!; // 説明
        public string ContactInfo { get; set; } = default!; // 問い合わせ先

        // デフォルトコンストラクタ
        public LostItemBySubcategory() {}

        // `LostItem` から `LostItemBySubcategory` へのコンストラクタ
        public LostItemBySubcategory(LostItem lostItem) {
            this.Subcategory = lostItem.Subcategory;
            this.Municipality = lostItem.Municipality;
            this.DateFound = lostItem.DateFound;
            this.Description = lostItem.Description;
            this.ContactInfo = lostItem.ContactInfo;
        }
    }
}
