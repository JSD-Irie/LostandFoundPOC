'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Header from '@components/TopPage/Header';
import Card from '@components/TopPage/Card';
import ActionButton from '@components/TopPage/ActionButton';
import AssignmentIcon from '@mui/icons-material/Assignment';
import SearchIcon from '@mui/icons-material/Search';

const RegisterLostItem: React.FC = () => {
  const router = useRouter();

  const handleRegisterClick = () => {
    router.push('/registration'); // 遺失物登録ページに遷移
  };

  const handleSearchClick = () => {
    router.push('/search'); // 検索ページに遷移
  };

  return (
    <div>
      <Header />
      <div className="flex justify-center my-4">
        <Card number={486} label="拾得物総数" />
        <Card number={198} label="警察届出数" />
        <Card number={97} label="返還済み" />
        <Card number={19} label="廃棄済み" />
      </div>
      <div className="flex justify-center my-4">
        <ActionButton
          icon={AssignmentIcon}
          title="遺失物の登録"
          description="拾得した遺失物の情報を登録"
          onClick={handleRegisterClick} // 遺失物登録ページに遷移
        />
        <ActionButton
          icon={SearchIcon}
          title="遺失物の検索"
          description="色や外見から遺失物を検索"
          onClick={handleSearchClick} // 検索ページに遷移
        />
      </div>
    </div>
  );
};

export default RegisterLostItem;
