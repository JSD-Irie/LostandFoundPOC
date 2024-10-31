// components/labelCheck/KeywordEditPopup.tsx
import React, { useState } from 'react';
import { Modal, Box, Typography, TextField, Button, CircularProgress } from '@mui/material';
import { ItemData } from '../../types'; // パスを適宜調整してください
import axios from 'axios';

interface KeywordEditPopupProps {
  item: ItemData;
  isOpen: boolean;
  onClose: () => void;
}

const KeywordEditPopup: React.FC<KeywordEditPopupProps> = ({ item, isOpen, onClose }) => {
  const [keywords, setKeywords] = useState<string>(item.keyword ? item.keyword.join(', ') : '');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleKeywordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setKeywords(event.target.value);
  };

  const handleSubmit = async (updateKeywords: boolean) => {
    setLoading(true);
    setError(null);
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    const apiUrl = `${apiBaseUrl}/lostitems/${item.id}/process-image`;

    let keywordArray: string[] | null = null;

    if (updateKeywords) {
      // キーワードをカンマで分割し、トリムして配列にする
      keywordArray = keywords.split(',').map((kw) => kw.trim()).filter((kw) => kw !== '');
    }

    const payload = {
      keyword: keywordArray,
    };

    try {
      const response = await axios.post(apiUrl, payload);
      console.log('Response:', response.data);
      // 成功したらポップアップを閉じてデータをリフレッシュするなどの処理
      onClose();
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        setError(`エラーが発生しました: ${error.response.statusText}`);
      } else {
        setError('エラーが発生しました。');
      }
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose}>
      <Box
        sx={{
          position: 'absolute' as const,
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: 400,
          bgcolor: 'background.paper',
          borderRadius: '8px',
          boxShadow: 24,
          p: 4,
        }}
      >
        <Typography variant="h6" component="h2" gutterBottom>
          キーワードの編集
        </Typography>
        <img
          src={item.imageUrl[0]} // 最初の画像を表示
          alt={item.item.itemName}
          style={{ width: '100%', height: 'auto', marginBottom: '16px' }}
        />
        <Typography variant="body1" gutterBottom>
          現在のキーワード: {item.keyword ? item.keyword.join(', ') : 'なし'}
        </Typography>
        <TextField
          label="キーワードを編集 (カンマ区切り)"
          variant="outlined"
          fullWidth
          value={keywords}
          onChange={handleKeywordChange}
          margin="normal"
        />
        {error && (
          <Typography color="error" variant="body2" gutterBottom>
            {error}
          </Typography>
        )}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', marginTop: '16px' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => handleSubmit(false)} // キーワードを更新せずに送信
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'このままでOK'}
          </Button>
          <Button
            variant="contained"
            color="secondary"
            onClick={() => handleSubmit(true)} // キーワードを更新して送信
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'キーワードの更新'}
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};

export default KeywordEditPopup;
