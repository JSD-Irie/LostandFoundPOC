// components/search/ItemGrid.tsx
import React from 'react';
import ItemCard from './ItemCard';
import { Grid, CircularProgress, Typography } from '@mui/material';
import { ItemData } from '@/types/types'; // パスを適宜調整してください

interface ItemGridProps {
  items: ItemData[];
  loading: boolean;
  onItemClick: (item: ItemData) => void;
}

const ItemGrid: React.FC<ItemGridProps> = ({ items, loading, onItemClick }) => {
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <CircularProgress />
        <Typography variant="body1">読み込み中...</Typography>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <Typography variant="body1" style={{ textAlign: 'center', padding: '20px' }}>
        アイテムが見つかりませんでした。
      </Typography>
    );
  }

  return (
    <Grid container spacing={2}>
      {items.map((item) => (
        <Grid item xs={12} sm={6} md={4} key={item.id}>
          <ItemCard item={item} onClick={onItemClick} />
        </Grid>
      ))}
    </Grid>
  );
};

export default ItemGrid;
