'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@components/TopPage/Header';
import Image from 'next/image';

const UploadImage: React.FC = () => {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
  const router = useRouter();

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files[0]) {
      const file = files[0];
      setImageFile(file);
      setImagePreviewUrl(URL.createObjectURL(file)); // 画像のプレビューURLを作成
    }
  };

  const handleSubmit = async () => {
    if (!imageFile) {
      console.error('画像が選択されていません');
      return;
    }

    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    const apiUrl = `${apiBaseUrl}/imagescan`;

    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      const res = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error('API request failed');
      }

      const responseData = await res.json();
      console.log('Upload successful:', responseData);

      // 画像アップロード後、詳細登録ページに遷移
      const queryString = new URLSearchParams({
        color: responseData.color,
        categoryName: responseData.categoryName,
        memo: responseData.memo,
        imageUrl: imagePreviewUrl || '', // 画像プレビューURLを渡す
      }).toString();

      router.push(`/detail-registration?${queryString}`); // クエリを文字列として結合して渡す
    } catch (error) {
      console.error('Error uploading image:', error);
    }
  };

  return (
    <div>
      <Header />
      <h2 className="text-center text-2xl my-4">画像アップロード</h2>
      <input type="file" accept="image/*" onChange={handleImageUpload} />
        <Image src={imagePreviewUrl || ''} alt="Uploaded Image Preview" className="my-4" style={{ maxWidth: '100%', height: 'auto' }} layout="responsive" width={500} height={500} />
      <button onClick={handleSubmit} className="mt-4 bg-green-700 hover:bg-green-600 text-white p-2 rounded">
        画像をアップロードする
      </button>
      <button onClick={() => router.back()} className="mt-4 ml-2 p-2 border rounded">
        戻る
      </button>
    </div>
  );
};

export default UploadImage;
