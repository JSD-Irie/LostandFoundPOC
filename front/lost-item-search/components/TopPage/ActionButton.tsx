import React from 'react';
import SvgIcon from '@mui/material/SvgIcon';
import { ElementType } from 'react';

interface ActionButtonProps {
  icon: ElementType;
  title: string;
  description: string;
  onClick?: () => void;
}

const ActionButton: React.FC<ActionButtonProps> = ({ icon, title, description, onClick }) => {
  return (
    <div
      className="bg-green-500 hover:bg-green-400 border border-green-700 rounded-lg shadow-md p-4 m-2 w-1/3 max-w-sm cursor-pointer flex flex-col items-center"
      onClick={onClick}
      role="button"
      aria-label={`${title}ボタン`}
    >
      <SvgIcon component={icon} style={{ fontSize: '48px', color: '#FFFFFF' }} />
      <span className="text-lg font-bold text-white mt-2">{title}</span>
      <span className="text-sm text-white">{description}</span>
    </div>
  );
};

export default ActionButton;
