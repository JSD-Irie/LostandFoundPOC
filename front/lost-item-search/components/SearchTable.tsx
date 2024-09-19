// components/SearchTable.tsx
import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

interface SearchResult {
  Municipality: string;
  Subcategory: string;
  DateFound: string;
  Description: string;
}

interface SearchTableProps {
  results: SearchResult[];
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
              <TableCell>{row.Municipality}</TableCell>
              <TableCell>{row.Subcategory}</TableCell>
              <TableCell>{row.Description}</TableCell>
              <TableCell>{formatDate(row.DateFound)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
