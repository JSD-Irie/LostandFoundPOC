// types.ts
export interface ItemData {
    id: number;
    imageUrl: string[];
    item: {
      itemName: string;
      categoryName: string;
    };
    color: {
      name: string;
    };
    findPlace: string;
    findDateTime: string;
    memo: string;
    keyword: string[];
  }
  