import React, { useState } from 'react';
import { Card, CardMedia, Typography } from '@mui/material';
import { ItemData } from '../../types/types'; // パスを適宜調整してください

const ItemCard: React.FC<{ item: ItemData; onClick: (item: ItemData) => void }> = ({ item, onClick }) => {
  const [hovered, setHovered] = useState(false);

  return (
    <Card
      className="relative border border-green-600 rounded-lg overflow-hidden cursor-pointer w-72 h-72 shadow-md transition-transform transform hover:scale-105"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={() => onClick(item)} // アイテムカードがクリックされたときにonClickを呼び出す
    >
      <CardMedia
        component="img"
        image={item.imageUrl[0]}
        alt="Item"
        className="w-full h-full object-cover" // Tailwind CSSを使用して画像をトリミング
      />
      {hovered && (
        <div className="absolute inset-0 bg-black bg-opacity-60 flex flex-col justify-center items-center text-white p-2 text-center">
          <Typography variant="body1">物品名: {item.item.itemName}</Typography>
          <Typography variant="body1">色: {item.color.name}</Typography>
          <Typography variant="body1">拾得場所: {item.findPlace}</Typography>
          <Typography variant="body1">
            日時: {new Date(item.findDateTime).toLocaleString()}
          </Typography>
        </div>
      )}
    </Card>
  );
};

export default ItemCard;
