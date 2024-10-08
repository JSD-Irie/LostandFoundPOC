// components/search/DetailSidebar.tsx
import React from 'react';
import Image from 'next/image';
import { Grid, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { ItemData } from '@/types/types'; // パスを適宜調整してください

interface DetailSidebarProps {
  item: ItemData | null;
  isOpen: boolean;
  onClose: () => void;
}

const DetailSidebar: React.FC<DetailSidebarProps> = ({ item, isOpen, onClose }) => {
  if (!isOpen || !item) return null; // サイドバーが開いていないか、アイテムがない場合は何も表示しない

  return (
    <div className="fixed top-0 right-0 bg-white w-96 h-full shadow-lg p-4 z-30">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">アイテム詳細</h2>
        <IconButton onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </div>
      <div className="w-full h-48 mb-4 relative">
        <Image
          src={item.imageUrl[0]}
          alt="Item"
          layout="fill"
          objectFit="cover"
          className="rounded"
        />
      </div>
      <div className="flex flex-col">
        <Grid container spacing={1} className="mb-2">
          <Grid item xs={3}>
            <span>色:</span>
          </Grid>
          <Grid item xs={9}>
            <span>{item.color.name}</span>
          </Grid>
        </Grid>
        <Grid container spacing={1} className="mb-2">
          <Grid item xs={3}>
            <span>ID:</span>
          </Grid>
          <Grid item xs={9}>
            <span>{item.id}</span>
          </Grid>
        </Grid>
        <Grid container spacing={1} className="mb-2">
          <Grid item xs={3}>
            <span>品名:</span>
          </Grid>
          <Grid item xs={9}>
            <span>{item.item.itemName}</span>
          </Grid>
        </Grid>
        <Grid container spacing={1} className="mb-2">
          <Grid item xs={3}>
            <span>カテゴリー:</span>
          </Grid>
          <Grid item xs={9}>
            <span>{item.item.categoryName}</span>
          </Grid>
        </Grid>
        <Grid container spacing={1} className="mb-2">
          <Grid item xs={3}>
            <span>特徴:</span>
          </Grid>
          <Grid item xs={9}>
            <span>{item.memo}</span>
          </Grid>
        </Grid>
        <Grid container spacing={1} className="mb-2">
          <Grid item xs={3}>
            <span>場所:</span>
          </Grid>
          <Grid item xs={9}>
            <span>{item.findPlace}</span>
          </Grid>
        </Grid>
      </div>
    </div>
  );
};

export default DetailSidebar;
