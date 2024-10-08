'use client';

// pages/search.tsx
import React, { useEffect, useState } from 'react';
import Header from '@components/search/Header';
import SearchBar from '@components/search/SearchBar';
import FilterSection from '@components/search/FilterSection';
import ItemGrid from '@components/search/ItemGrid';
import DetailSidebar from '@components/search/DetailSidebar';
import { Container, Grid } from '@mui/material';

const SearchPage: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<any | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [subcategory, setSubcategory] = useState<string | null>(null);
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  useEffect(() => {
    fetchData(); // 初期ロード時にデータを取得
  }, [subcategory, selectedColor, selectedDate]);

  const fetchData = async () => {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    let apiUrl = `${apiBaseUrl}/lostitems`;

    // フィルター条件をURLに追加
    const filters = [];
    if (subcategory) {
      filters.push(`categoryName=${subcategory}`);
    }
    if (selectedColor) {
      filters.push(`color=${selectedColor}`);
    }
    if (selectedDate) {
      filters.push(`findDate=${selectedDate}`); // 日付フィルターの条件を追加
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
      const data = await res.json();
      setItems(data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError(error.message || 'データ取得中にエラーが発生しました');
    } finally {
      setLoading(false); // ローディングを終了
    }
  };

  const handleItemClick = (item: any) => {
    setSelectedItem(item);
    setSidebarOpen(true);
  };

  const handleCloseSidebar = () => {
    setSidebarOpen(false);
    setSelectedItem(null);
  };

  const handleSearch = (subcategory: string) => {
    setSubcategory(subcategory); // サブカテゴリを設定
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

    // フィルターが変更されたときにデータを再取得
    fetchData();
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
            selectedDate={selectedDate}   // 現在の選択された日付を渡す
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
