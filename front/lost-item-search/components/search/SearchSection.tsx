// components/search/FilterSection.tsx
import React from 'react';
import { Typography, FormControlLabel, Checkbox, Grid } from '@mui/material';

const FilterSection: React.FC = () => {
  return (
    <div style={{ margin: '16px 0' }}>
      <Typography variant="h5" style={{ color: '#000' }}>
        探す
      </Typography>
      <Grid container spacing={2}>
        <Grid item>
          <FormControlLabel control={<Checkbox />} label="特長から探す" />
        </Grid>
        <Grid item>
          <FormControlLabel control={<Checkbox />} label="色" />
        </Grid>
        <Grid item>
          <FormControlLabel control={<Checkbox />} label="カテゴリー" />
        </Grid>
        <Grid item>
          <FormControlLabel control={<Checkbox />} label="携帯電話" />
        </Grid>
        <Grid item>
          <FormControlLabel control={<Checkbox />} label="場所" />
        </Grid>
        <Grid item>
          <FormControlLabel control={<Checkbox />} label="拾得時期" />
        </Grid>
      </Grid>
    </div>
  );
};

export default FilterSection;
