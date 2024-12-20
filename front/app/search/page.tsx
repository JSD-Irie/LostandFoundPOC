'use client';

import React, { useState } from 'react';
import { SearchForm } from '@components/SearchForm';
import { SearchTable, SearchResult } from '@components/SearchTable';

const Home: React.FC = () => {
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);

  const handleSearch = async (query: { location: string; subcategory: string }) => {
    const { location, subcategory } = query;

    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    let apiUrl;
    if (location && subcategory) {
      apiUrl = `${apiBaseUrl}/lostitems?isChecked=true&municipality=${location}&categoryName=${subcategory}`;
    } else if (location) {
      apiUrl = `${apiBaseUrl}/lostitems?isChecked=true&municipality=${location}`;
    } else if (subcategory) {
      apiUrl = `${apiBaseUrl}/lostitems?isChecked=true&categoryName=${subcategory}`;
    } else {
      apiUrl = `${apiBaseUrl}/lostitems?isChecked=true`;
    }

    try {
      const res = await fetch(apiUrl);
      if (!res.ok) {
        throw new Error('API request failed');
      }
      const data: SearchResult[] = await res.json();
      setSearchResults(data);
    } catch (error) {
      console.error('Error fetching search results:', error);
    }
  };

  return (
    <div>
      <SearchForm onSearch={handleSearch} />

      <div style={{ marginTop: '20px', padding: '0 20px' }}>
        {searchResults.length > 0 ? (
          <SearchTable results={searchResults} />
        ) : (
          <p>検索結果はありません。</p>
        )}
      </div>
    </div>
  );
};

export default Home;
