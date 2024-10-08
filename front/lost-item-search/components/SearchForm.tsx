import React, { useState } from 'react';
import { TextField, Button, Grid, Container, Typography } from '@mui/material';

interface SearchFormProps {
  onSearch: (query: { location: string; subcategory: string }) => void;
}

// カテゴリはvalueも日本語にしておく
const categories = [
  { label: '手提げかばん', value: '手提げかばん' },
  { label: '財布', value: '財布' },
  { label: '傘', value: '傘' },
  { label: '時計', value: '時計' },
  { label: 'メガネ', value: 'メガネ' },
  { label: '携帯電話', value: '携帯電話' },
  { label: 'カメラ', value: 'カメラ' },
  { label: '鍵', value: '鍵' },
  { label: '本', value: '本' },
  { label: 'アクセサリー', value: 'アクセサリー' },
];

export const SearchForm: React.FC<SearchFormProps> = ({ onSearch }) => {
  const [location, setLocation] = useState<string>('');
  const [subcategory, setSubcategory] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // 親コンポーネントにクエリを渡す
    onSearch({ location, subcategory });
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" gutterBottom align="center" style={{ marginTop: '20px' }}>
        忘れ物検索
      </Typography>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              label="場所"
              variant="outlined"
              fullWidth
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="例: 札幌市中央区"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              label="中分類"
              variant="outlined"
              fullWidth
              value={subcategory}
              onChange={(e) => setSubcategory(e.target.value)}
              placeholder="例: メガネ"
            />
            {/* <TextField
              select
              label="中分類"
              variant="outlined"
              fullWidth
              value={subcategory}
              onChange={(e) => setSubcategory(e.target.value)}
            >
              {categories.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField> */}
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              style={{ padding: '10px' }}
            >
              検索
            </Button>
          </Grid>
        </Grid>
      </form>
    </Container>
  );
};
