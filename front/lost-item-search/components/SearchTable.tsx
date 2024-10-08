// components/SearchTable.tsx
import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

interface SearchResult {
  color: {
    id: string;
    name: string;
    url: string;
  };
  createUserID: string;
  createUserPlace: string;
  currency: {
    foreignCurrency: string;
    japaneseCurrency: Array<{
      count: number;
      id: string;
    }>;
  };
  findDateTime: string;
  findPlace: string;
  id: string;
  imageUrl: string[];
  isValuables: boolean;
  item: {
    categoryCode: string;
    categoryName: string;
    itemName: string;
    valuableFlg: number;
  };
  keyword: string[];
  lostItemPartitionKey: string;
  memo: string;
  mngmtNo: string;
  personal: string;
  status: {
    id: string;
    name: string;
  };
}

// 日付を見やすい形式にフォーマットする関数
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ja-JP', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
};

interface SearchTableProps {
  results: SearchResult[];
}

export const SearchTable: React.FC<SearchTableProps> = ({ results }) => {
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>場所</TableCell>
            <TableCell>カテゴリ</TableCell>
            <TableCell>特徴</TableCell>
            <TableCell>見つけた日</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {results.map((row, index) => (
            <TableRow key={index}>
              <TableCell>{row.createUserPlace}</TableCell>
              <TableCell>{row.item.categoryName}</TableCell>
              <TableCell>{row.memo}</TableCell>
              <TableCell>{formatDate(row.findDateTime)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};