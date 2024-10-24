import React from 'react';

interface CardProps {
  number: number;
  label: string;
}

const Card: React.FC<CardProps> = ({ number, label }) => {
  return (
    <div className="bg-white border border-gray-300 rounded-lg shadow-md p-4 m-2 flex flex-col items-center w-1/4 max-w-xs">
      <span className="text-4xl font-bold text-green-600">{number}</span>
      <span className="text-lg text-black">{label}</span>
    </div>
  );
};

export default Card;
