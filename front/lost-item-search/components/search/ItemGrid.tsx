// components/search/ItemGrid.tsx
import React from 'react';
import { Grid, CircularProgress } from '@mui/material';
import ItemCard from './ItemCard';

interface ItemGridProps {
  items: any[];
  loading: boolean; // ローディング状態を受け取る
  onItemClick: (item: any) => void; // アイテムクリック時のハンドラ
}

const ItemGrid: React.FC<ItemGridProps> = ({ items, loading, onItemClick }) => {
  return (
    <div>
      {loading ? (
        <div className="flex justify-center items-center" style={{ height: '300px' }}> {/* 高さを調整 */}
          <CircularProgress /> {/* ぐるぐるローディング */}
        </div>
      ) : (
        <Grid container spacing={2}>
          {items.map((item) => (
            <Grid item xs={12} sm={6} md={4} key={item.id}>
              <ItemCard item={item} onClick={() => onItemClick(item)} /> {/* onClickを渡す */}
            </Grid>
          ))}
        </Grid>
      )}
    </div>
  );
};

export default ItemGrid;
