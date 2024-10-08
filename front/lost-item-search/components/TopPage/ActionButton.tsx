import React from 'react';
import SvgIcon from '@mui/material/SvgIcon';
import { ElementType } from 'react';

interface ActionButtonProps {
  icon: ElementType;
  title: string;
  description: string;
  onClick?: () => void; // 遷移時のハンドラ
  onUpload?: (file: File) => void; // 画像アップロード時のハンドラ
}

const ActionButton: React.FC<ActionButtonProps> = ({ icon, title, description, onClick, onUpload }) => {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files[0]) {
      onUpload?.(files[0]); // 画像アップロードハンドラを呼び出し
    }
  };

  return (
    <div className="flex items-center bg-green-700 hover:bg-green-600 transition-colors p-3 rounded-md cursor-pointer" onClick={onClick}>
      <SvgIcon component={icon} className="mr-2" />
      <div className="flex flex-col">
        <span className="text-md text-white">{title}</span>
        <span className="text-sm text-white">{description}</span>
      </div>
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden" // 非表示にする
      />
    </div>
  );
};

export default ActionButton;
