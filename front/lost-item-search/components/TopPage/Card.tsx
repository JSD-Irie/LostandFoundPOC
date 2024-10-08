import React from 'react';

interface CardProps {
  number: number;
  label: string;
}

const Card: React.FC<CardProps> = ({ number, label }) => {
  return (
    <div className="bg-green-200 border border-green-800 rounded-lg shadow-md p-4 m-2 flex flex-col items-center">
      <span className="text-4xl font-bold text-green-800">{number}</span>
      <span className="text-lg">{label}</span>
    </div>
  );
};

export default Card;
