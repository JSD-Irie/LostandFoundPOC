// components/search/FilterSection.tsx
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

// 色のマッピング
const colorMapping = {
  black: { id: 'black', name: '黒（ブラック）系', url: '/colors/black.png' },
  red: { id: 'red', name: '赤（レッド）系', url: '/colors/red.png' },
  blue: { id: 'blue', name: '青（ブルー）系', url: '/colors/blue.png' },
  green: { id: 'green', name: '緑（グリーン）系', url: '/colors/green.png' },
  yellow: { id: 'yellow', name: '黄色（イエロー）系', url: '/colors/yellow.png' },
  white: { id: 'white', name: '白（ホワイト）系', url: '/colors/white.png' },
  gray: { id: 'gray', name: '灰色（グレー）系', url: '/colors/gray.png' },
  brown: { id: 'brown', name: '茶色（ブラウン）系', url: '/colors/brown.png' },
  purple: { id: 'purple', name: '紫（パープル）系', url: '/colors/purple.png' },
  pink: { id: 'pink', name: 'ピンク系', url: '/colors/pink.png' },
  orange: { id: 'orange', name: 'オレンジ系', url: '/colors/orange.png' },
};

// 取得時期の選択肢
const dateOptions = [
  { label: '今日', value: 'today' },
  { label: '昨日', value: 'yesterday' },
  { label: '一週間以内', value: 'last_week' },
  { label: '一か月以内', value: 'last_month' },
];

interface FilterSectionProps {
  onFilterChange: (color: string | null, date: string | null) => void; // フィルター変更のコールバック
  selectedColor: string | null; // 選択されたカラー
  selectedDate: string | null;   // 選択された日付
}

const FilterSection: React.FC<FilterSectionProps> = ({ onFilterChange, selectedColor, selectedDate }) => {
  const handleColorChange = (colorId: string) => {
    if (selectedColor === colorId) {
      onFilterChange(null, selectedDate); // 同じフィルターを再度クリックした場合、解除
    } else {
      onFilterChange(colorId, selectedDate); // 新しいフィルターを設定
    }
  };

  const handleDateChange = (value: string) => {
    if (selectedDate === value) {
      onFilterChange(selectedColor, null); // 同じフィルターを再度クリックした場合、解除
    } else {
      onFilterChange(selectedColor, value); // 新しいフィルターを設定
    }
  };

  return (
    <div>
      {/* 色のフィルター */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">色で探す</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {Object.values(colorMapping).map(color => (
            <FormControlLabel
              key={color.id}
              control={
                <Checkbox
                  checked={selectedColor === color.id}
                  onChange={() => handleColorChange(color.id)}
                />
              }
              label={color.name}
            />
          ))}
        </AccordionDetails>
      </Accordion>

      {/* 取得時期のフィルター */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">取得時期で探す</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {dateOptions.map(option => (
            <FormControlLabel
              key={option.value}
              control={
                <Checkbox
                  checked={selectedDate === option.value}
                  onChange={() => handleDateChange(option.value)}
                />
              }
              label={option.label}
            />
          ))}
        </AccordionDetails>
      </Accordion>
    </div>
  );
};

export default FilterSection;
