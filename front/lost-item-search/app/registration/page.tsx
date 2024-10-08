'use client';

import React, { useState } from 'react';
import {
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  Grid,
  Typography,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import { useRouter } from 'next/navigation';
import Header from '@components/TopPage/Header';

// カラー情報のマッピング
type ColorKey = keyof typeof colorMapping;

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

// カテゴリー情報のマッピング
const categoryMapping = {
  '手提げかばん': { categoryCode: '2601', categoryName: '手提げかばん', itemName: 'トートバッグ', valuableFlg: 1 },
  '財布': { categoryCode: '2602', categoryName: '財布', itemName: '二つ折り財布', valuableFlg: 1 },
  '傘': { categoryCode: '2603', categoryName: '傘', itemName: '折りたたみ傘', valuableFlg: 0 },
  '時計': { categoryCode: '2604', categoryName: '時計', itemName: '腕時計', valuableFlg: 1 },
  'メガネ': { categoryCode: '2605', categoryName: 'メガネ', itemName: 'サングラス', valuableFlg: 1 },
  '携帯電話': { categoryCode: '2606', categoryName: '携帯電話', itemName: 'スマートフォン', valuableFlg: 1 },
  'カメラ': { categoryCode: '2607', categoryName: 'カメラ', itemName: 'デジタルカメラ', valuableFlg: 1 },
  '鍵': { categoryCode: '2608', categoryName: '鍵', itemName: 'カギ', valuableFlg: 0 },
  '本': { categoryCode: '2609', categoryName: '本', itemName: '文庫本', valuableFlg: 0 },
  'アクセサリー': { categoryCode: '2610', categoryName: 'アクセサリー', itemName: 'ネックレス', valuableFlg: 1 },
  '携帯音響品': { categoryCode: '2611', categoryName: '携帯音響品', itemName: 'Bluetoothスピーカー', valuableFlg: 1 },
};

// ユニークIDを生成する関数
const generateUniqueId = () => {
  return `LP${Date.now()}`; // 現在のタイムスタンプを基にしたユニークID
};

const DetailRegistration: React.FC = () => {
  const router = useRouter();

  // ステートの初期化
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
  const [color, setColor] = useState<string>('');
  const [categoryName, setCategoryName] = useState<keyof typeof categoryMapping | undefined>(undefined); // カテゴリー名のステート
  const [memo, setMemo] = useState<string>('');
  const [deliveryLocation, setDeliveryLocation] = useState<string>('');
  const [retrievalLocation, setRetrievalLocation] = useState<string>('');
  const [retrievalTime, setRetrievalTime] = useState<string>('');
  const [itemName, setItemName] = useState<string>('');
  const [keywords, setKeywords] = useState<string[]>([]); // キーワード用の配列
  const [, setLoading] = useState<boolean>(false); // ローディング状態
  const [, setError] = useState<string | null>(null); // エラーメッセージ
  const [openDialog, setOpenDialog] = useState<boolean>(false); // ポップアップ状態

  // 画像のアップロード処理
  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files[0]) {
      const file = files[0];
      setImageFile(file);
      setImagePreviewUrl(URL.createObjectURL(file)); // 画像のプレビューURLを作成
      setError(null);
    }
  };

  // キーワードの追加処理
  const handleKeywordSubmit = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      const keyword = (event.target as HTMLInputElement).value.trim();
      if (keyword && !keywords.includes(keyword)) {
        setKeywords([...keywords, keyword]); // キーワードを追加
        (event.target as HTMLInputElement).value = ''; // 入力をクリア
      }
    }
  };

  // 画像をAzure Blob Storageにアップロードする関数
  const uploadImageToBlobStorage = async (file: File): Promise<string> => {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    const apiUrl = `${apiBaseUrl}/upload-image`; // 画像アップロード用のAPIエンドポイント

    const formData = new FormData();
    formData.append('image', file);

    try {
      const res = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error('画像アップロードに失敗しました');
      }

      const { imageUrl } = await res.json(); // APIから返される画像URLを取得
      return imageUrl; // 取得したURLを返す
    } catch (error) {
      console.error('Error uploading image:', error);
      throw error; // エラーを投げる
    }
  };

  // 画像をスキャンして情報を取得する関数
  const handleScanImage = async () => {
    if (!imageFile) {
      console.error('画像が選択されていません');
      return;
    }

    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    const apiUrl = `${apiBaseUrl}/imagescan`; // 画像スキャン用のAPIエンドポイント

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
      console.log('Scan successful:', responseData);

      // 取得したデータでフォームを埋める
      setColor(responseData.color);
      setCategoryName(responseData.categoryName); // APIから取得したcategoryNameを設定
      setMemo(responseData.memo);
    } catch (error) {
      console.error('Error scanning image:', error);
    }
  };

  // データ登録処理
  const handleDataRegistration = async () => {
    if (!imageFile) {
      setError('画像が選択されていません');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. 画像をアップロードしてURLを取得
      const imageUrl = await uploadImageToBlobStorage(imageFile);
      const colorInfo = colorMapping[color as ColorKey] || { id: '', name: '', url: '' };
      // 2. カラー情報をマッピング

      // 3. カテゴリー情報をマッピング
      const categoryInfo = categoryMapping[categoryName as keyof typeof categoryMapping] || {
        categoryCode: '',
        categoryName: categoryName,
        itemName: itemName,
        valuableFlg: 0,
      };

      const lostItemData = {
        createUserPlace: deliveryLocation,
        findDateTime: retrievalTime,
        memo: memo,
        color: colorInfo,
        item: {
          categoryCode: categoryInfo.categoryCode,
          categoryName: categoryInfo.categoryName,
          itemName: itemName,
          valuableFlg: categoryInfo.valuableFlg,
        },
        findPlace: retrievalLocation,
        keyword: keywords,
        imageUrl: [imageUrl], // 画像URLを追加
      };

      console.log('Data to be registered:', lostItemData);

      // 5. データ登録APIにデータを送信
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
      const apiUrl = `${apiBaseUrl}/lostitems`;

      const res = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(lostItemData),
      });

      if (!res.ok) {
        throw new Error('データ登録に失敗しました');
      }

      const createdItem = await res.json();
      console.log('Data registered successfully:', createdItem);

      // 成功後の処理：ポップアップを表示
      setOpenDialog(true);
    } catch (error: unknown) {
      setError((error as Error).message || 'データ登録中にエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  // ポップアップを閉じる関数
  const handleDialogClose = () => {
    setOpenDialog(false);
    window.location.reload();
  };

  // トップページに戻る
  const handleGoHome = () => {
    router.push('/'); // トップページへのリダイレクト
  };

  return (
    <div>
      <Header />
      <h2 className="text-center text-2xl my-4">情報の入力</h2>
      {imagePreviewUrl && (
        <img
          src={imagePreviewUrl}
          alt="Uploaded Image"
          className="w-4/5 h-auto mb-4 border border-gray-300 rounded mx-auto" // 中央寄せ
        />
      )}
      <div className="flex flex-col items-center">
        <label htmlFor="file-upload" className="cursor-pointer">
          <Button variant="contained" component="span" color="primary" startIcon={<CloudUploadIcon />}>
            画像をアップロード
          </Button>
          <input
            id="file-upload"
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            style={{ display: 'none' }} // ボタンがクリックされたときにファイル選択
          />
        </label>
      </div>
      <div className="flex flex-col items-center mt-2">
        <Button
          variant="contained"
          color="secondary"
          startIcon={<PhotoCameraIcon />}
          onClick={handleScanImage}
        >
          スキャン画像
        </Button>
      </div>

      <div className="flex flex-col max-w-md mx-auto mt-4">
        <TextField
          label="ID"
          value={generateUniqueId()} // 自動生成されたユニークID
          fullWidth
          margin="normal"
          InputProps={{
            readOnly: true,
          }}
        />
        <Grid container spacing={2} alignItems="center" margin="normal">
          <Grid item xs={4}>
            <Typography>届け出先</Typography>
          </Grid>
          <Grid item xs={8}>
            <FormControl fullWidth>
              <Select
                value={deliveryLocation}
                onChange={(e) => setDeliveryLocation(e.target.value)}
              >
                <MenuItem value="旭川市">旭川市</MenuItem>
                <MenuItem value="函館市">函館市</MenuItem>
                <MenuItem value="小樽市">小樽市</MenuItem>
                <MenuItem value="千歳市">千歳市</MenuItem>
                <MenuItem value="苫小牧市">苫小牧市</MenuItem>
                <MenuItem value="室蘭市">室蘭市</MenuItem>
                <MenuItem value="北見市">北見市</MenuItem>
                <MenuItem value="札幌駅">札幌駅</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Grid container spacing={2} alignItems="center" margin="normal">
          <Grid item xs={4}>
            <Typography>カテゴリー</Typography>
          </Grid>
          <Grid item xs={8}>
            <FormControl fullWidth>
              <Select
                value={categoryName}
                onChange={(e) => setCategoryName(e.target.value as keyof typeof categoryMapping)}
              >
                <MenuItem value="手提げかばん">手提げかばん</MenuItem>
                <MenuItem value="財布">財布</MenuItem>
                <MenuItem value="傘">傘</MenuItem>
                <MenuItem value="時計">時計</MenuItem>
                <MenuItem value="メガネ">メガネ</MenuItem>
                <MenuItem value="携帯電話">携帯電話</MenuItem>
                <MenuItem value="カメラ">カメラ</MenuItem>
                <MenuItem value="鍵">鍵</MenuItem>
                <MenuItem value="本">本</MenuItem>
                <MenuItem value="アクセサリー">アクセサリー</MenuItem>
                <MenuItem value="携帯音響品">携帯音響品</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Grid container spacing={2} alignItems="center" margin="normal">
          <Grid item xs={4}>
            <Typography>品名</Typography>
          </Grid>
          <Grid item xs={8}>
            <TextField
              value={itemName}
              onChange={(e) => setItemName(e.target.value)}
              fullWidth
            />
          </Grid>
        </Grid>

        <Grid container spacing={2} alignItems="center" margin="normal">
          <Grid item xs={4}>
            <Typography>取得場所</Typography>
          </Grid>
          <Grid item xs={8}>
            <TextField
              value={retrievalLocation}
              onChange={(e) => setRetrievalLocation(e.target.value)}
              fullWidth
            />
          </Grid>
        </Grid>

        <Grid container spacing={2} alignItems="center" margin="normal">
          <Grid item xs={4}>
            <Typography>取得時間</Typography>
          </Grid>
          <Grid item xs={8}>
            <TextField
              type="date"
              value={retrievalTime}
              onChange={(e) => setRetrievalTime(e.target.value)}
              fullWidth
            />
          </Grid>
        </Grid>

        <Grid container spacing={2} alignItems="center" margin="normal">
          <Grid item xs={4}>
            <Typography>キーワード</Typography>
          </Grid>
          <Grid item xs={8}>
            <TextField
              onKeyDown={handleKeywordSubmit}
              fullWidth
              placeholder="キーワードを入力してEnter"
            />
            <div>
              <Typography variant="h6">登録されたキーワード:</Typography>
              <ul>
                {keywords.map((keyword, index) => (
                  <li key={index}>{keyword}</li>
                ))}
              </ul>
            </div>
          </Grid>
        </Grid>

        <Grid container spacing={2} alignItems="center" margin="normal">
          <Grid item xs={4}>
            <Typography>特徴</Typography>
          </Grid>
          <Grid item xs={8}>
            <TextField
              value={memo}
              fullWidth
              multiline
              rows={4}
              onChange={(e) => setMemo(e.target.value)}
            />
          </Grid>
        </Grid>
      </div>
      <div className="flex justify-center mt-4">
        <Button variant="outlined" color="info" onClick={() => router.back()} className="mr-4">
          戻る
        </Button>
        <Button variant="contained" color="success" onClick={handleDataRegistration}>
          データ登録
        </Button>
      </div>

      {/* ポップアップダイアログ */}
      <Dialog open={openDialog} onClose={handleDialogClose}>
        <DialogTitle>データ登録完了</DialogTitle>
        <DialogContent>
          <DialogContentText>
            データの登録が完了しました。続けてデータの登録を行いますか、それともトップページに戻りますか？
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleDialogClose()}>続けて登録</Button>
          <Button onClick={handleGoHome} color="primary">
            トップページに戻る
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default DetailRegistration;
