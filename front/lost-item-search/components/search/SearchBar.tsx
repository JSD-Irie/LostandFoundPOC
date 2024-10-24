// components/search/SearchBar.tsx
import React, { useState } from 'react';
import { TextField, InputAdornment } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

interface SearchBarProps {
  onSearch: (subcategory: string) => void; // 親コンポーネントに検索ワードを渡す関数
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      onSearch(searchTerm.trim()); // Enterキーが押されたら検索
    }
  };

  return (
    <div style={{ marginTop: '16px', marginBottom: '8px', textAlign: 'center' }}>
      <TextField
        variant="outlined"
        placeholder="検索..."
        fullWidth
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)} // 入力を状態に保存
        onKeyDown={handleKeyDown} // Enterキーのイベントをハンドル
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon style={{ color: '#888888' }} />
            </InputAdornment>
          ),
        }}
        style={{
          maxWidth: '600px',
          borderRadius: '4px',
          backgroundColor: '#F9F9F9', // 薄いグレー
          border: '1px solid #DDDDDD',
          boxShadow: '1px 1px 5px rgba(0, 0, 0, 0.1)',
        }}
      />
    </div>
  );
};

export default SearchBar;
