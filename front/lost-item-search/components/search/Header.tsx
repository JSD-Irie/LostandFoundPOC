// components/search/Header.tsx
import React from 'react';
import { Typography } from '@mui/material';
import Link from 'next/link';

const Header: React.FC = () => {
  return (
    <header style={{ textAlign: 'center', padding: '16px 0', backgroundColor: '#fff' }}>
      <Typography variant="h4" style={{ color: '#4CAF50', fontWeight: 'bold', cursor: 'pointer' }}>
        <Link href="/" passHref>
          Lupe
        </Link>
      </Typography>
    </header>
  );
};

export default Header;
