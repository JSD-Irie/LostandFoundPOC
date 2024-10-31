'use client';

// pages/search.tsx
import React, { useEffect, useState, useCallback } from 'react';
import Header from '@components/search/Header';
import SearchBar from '@components/search/SearchBar';
import FilterSection from '@components/search/FilterSection';
import ItemGrid from '@components/search/ItemGrid';
import DetailSidebar from '@components/search/DetailSidebar';
import { Container, Grid } from '@mui/material';
import { ItemData } from '../../types'; // パスを適宜調整してください

const SearchPage: React.FC = () => {
  const [items, setItems] = useState<ItemData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<ItemData | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [subcategory] = useState<string | null>(null);
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [freeText, setFreeText] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    let apiUrl = `${apiBaseUrl}/lostitems`;

    // フィルター条件をURLに追加
    const filters = [];
    filters.push(`isChecked=true`); // isChecked が true のものだけを取得
    if (subcategory) {
      filters.push(`itemName=${subcategory}`);
    }
    if (selectedColor) {
      filters.push(`color=${selectedColor}`);
    }
    if (selectedDate) {
      filters.push(`findDate=${selectedDate}`); // 日付フィルターの条件を追加
    }
    if (freeText) {
      filters.push(`free_text=${freeText}`); // free_text フィルターの条件を追加
    }

    if (filters.length > 0) {
      apiUrl += `?${filters.join('&')}`;
    }

    try {
      setLoading(true); // ローディングを開始
      const res = await fetch(apiUrl);
      if (!res.ok) {
        throw new Error('データ取得に失敗しました');
      }
      const data: ItemData[] = await res.json(); // 型を明示
      setItems(data);
    } catch (error: unknown) {
      if (error instanceof Error) {
        console.error('Error fetching data:', error);
        setError(error.message || 'データ取得中にエラーが発生しました');
      } else {
        console.error('Unexpected error:', error);
        setError('データ取得中に予期しないエラーが発生しました');
      }
    } finally {
      setLoading(false); // ローディングを終了
    }
  }, [subcategory, selectedColor, selectedDate, freeText]);

  useEffect(() => {
    fetchData(); // 初期ロード時にデータを取得
  }, [fetchData]);

  const handleItemClick = (item: ItemData) => {
    setSelectedItem(item);
    setSidebarOpen(true);
  };

  const handleCloseSidebar = () => {
    setSidebarOpen(false);
    setSelectedItem(null);
  };

  const handleSearch = (text: string) => {
    setFreeText(text); // free_text を設定
  };

  const handleFilterChange = (color: string | null, date: string | null) => {
    // カラーが選択された場合、現在の選択肢と異なれば設定
    if (selectedColor === color) {
      setSelectedColor(null); // 同じフィルターを再度クリックした場合、解除
    } else {
      setSelectedColor(color);
    }

    // 日付が選択された場合、現在の選択肢と異なれば設定
    if (selectedDate === date) {
      setSelectedDate(null); // 同じフィルターを再度クリックした場合、解除
    } else {
      setSelectedDate(date);
    }

    // フィルターが変更されたときは、useEffectでデータを再取得
  };

  // エラーメッセージを表示
  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <Container>
      <Header />
      <SearchBar onSearch={handleSearch} /> {/* onSearchを渡す */}
      <Grid container spacing={2}>
        <Grid item xs={12} md={3}>
          <FilterSection
            onFilterChange={handleFilterChange}
            selectedColor={selectedColor} // 現在の選択されたカラーを渡す
            selectedDate={selectedDate} // 現在の選択された日付を渡す
          />
        </Grid>
        <Grid item xs={12} md={9}>
          <ItemGrid items={items} loading={loading} onItemClick={handleItemClick} /> {/* loadingを渡す */}
        </Grid>
      </Grid>
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-20" onClick={handleCloseSidebar}></div>
      )}
      <DetailSidebar item={selectedItem} isOpen={sidebarOpen} onClose={handleCloseSidebar} />
    </Container>
  );
};

export default SearchPage;