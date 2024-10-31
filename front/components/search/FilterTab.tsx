// components/search/FilterTab.tsx
import React from 'react';
import { Button } from '@mui/material';

const FilterTab: React.FC<{ label: string; selected: boolean; onClick: () => void }> = ({ label, selected, onClick }) => {
  return (
    <Button
      variant="outlined"
      style={{
        borderColor: selected ? '#4CAF50' : '#DDDDDD',
        backgroundColor: selected ? '#4CAF50' : '#FFFFFF',
        color: selected ? '#FFFFFF' : '#000000',
      }}
      onClick={onClick}
    >
      {label}
    </Button>
  );
};

export default FilterTab;
