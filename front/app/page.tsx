'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Header from '@components/TopPage/Header';
import Card from '@components/TopPage/Card';
import ActionButton from '@components/TopPage/ActionButton';
import AssignmentIcon from '@mui/icons-material/Assignment';
import SearchIcon from '@mui/icons-material/Search';
import LabelImportantIcon from '@mui/icons-material/LabelImportant'; // 新しく追加

const RegisterLostItem: React.FC = () => {
  const router = useRouter();

  const handleRegisterClick = () => {
    router.push('/registration');
  };

  const handleSearchClick = () => {
    router.push('/item');
  };

  const handleLabelCheckClick = () => {
    router.push('/labelCheck');
  };

  return (
    <div>
      <Header />
      <div className="flex justify-center flex-wrap my-4">
        <Card number={486} label="拾得物総数" />
        <Card number={198} label="警察届出数" />
        <Card number={97} label="返還済み" />
        <Card number={19} label="廃棄済み" />
      </div>
      <div className="flex justify-center flex-wrap my-4">
        <ActionButton
          icon={AssignmentIcon}
          title="遺失物の登録"
          description="拾得した遺失物の情報を登録できます。"
          onClick={handleRegisterClick}
        />
        <div className="m-4"></div> {/* ボタン間のスペース */}
        <ActionButton
          icon={SearchIcon}
          title="遺失物の検索"
          description="色や外見から遺失物を検索できます。"
          onClick={handleSearchClick}
        />
        <div className="m-4"></div> {/* ボタン間のスペース */}
        <ActionButton
          icon={LabelImportantIcon}
          title="ラベルチェック"
          description="遺失物のラベルを確認・編集できます。"
          onClick={handleLabelCheckClick}
        />
      </div>
    </div>
  );
};

export default RegisterLostItem;
