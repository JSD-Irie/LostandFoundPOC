# プロジェクト概要
このプロジェクトは、落とし物を検索するシステムを構築するためのもので、**Cosmos DB** と **Azure OpenAI** を活用しています。検索APIは**Python**で実装、フロントエンドは**Next.js**を使用しています。

# システム構成

### データベース: Cosmos DB
- 落とし物のデータを保存するためにCosmos DBを使用します。
- パフォーマンスとスケーラビリティを考慮して、各データは特定のパーティションキーで管理されます。

### 検索用API: Python
- 検索システムのAPIはPythonで実装されています。Azure OpenAIを使用して、フリーワードから落とし物を検索することができます。

### フロントエンド: Next.js
- フロントエンドは**Next.js**を使用して構築されています。直感的で反応の良いUIを提供し、ユーザーは簡単に検索を行うことができます。

### プロパティリスト保存テーブル: Azure Table Storage
- 落とし物のプロパティリストを補完するために、Azure Table Storageを使用します。

### 画像データ保存: Azure Blob Storage
- 遺失物の画像データを保存するために、Azure Blob Storageを使用します。

### 遺失物のラベル学習: Azure Custom Vision
- 遺失物の画像データを使用して、Azure Custom Visionを使用してラベル学習を行います。これにより、高精度な遺失物へのラベル付けが可能になります。

# セットアップ手順

### 前提条件
このプロジェクトをセットアップするためには、以下のものが必要です。
- Node.js (推奨バージョン: 18.x以上)
- Python (推奨バージョン: 3.10以上)
- Functions Core Tools (4.x以上のバージョンが必須)
- Azure サブスクリプション
- Azure CLI

### Azure リソースの作成
1. Azure にログインします。
    ```bash
    az login
    ```
2. 下記のコマンドでリソースグループを作成します。
    ```bash
    az group create --name <リソースグループ名> --location <リージョン>
    ```
3. 下記のコマンドでAzure OpenAI リソースを作成します。
    ```bash
    az cognitiveservices account create --name <OpenAIリソース名> --resource-group <リソースグループ名> --kind OpenAI --sku S0 --location eastus
    ```
4. 下記のコマンドで、GPT-4o-miniのを作成します。
    ```bash
    az cognitiveservices account deployment create --name <OpenAIのリソース名> --resource-group <リソースグループ名> --deployment-name <GPTのデプロイ名> --model-name gpt-4o-mini --model-version "2024-07-18" --model-format OpenAI --sku-capacity "10" --sku-name "GlobalStandard"
    ```
5. 下記のコマンドでCosmos DB アカウントを作成します。
    ```bash
    az cosmosdb create --name <Cosmos DB アカウント名> --resource-group <リソースグループ名> --kind GlobalDocumentDB --locations regionName=<リージョン> failoverPriority=0 isZoneRedundant=False
    ```
6. 下記のコマンドで、画像保存用のAzure Blob Storageとプロパティリスト保存用のAzure Table Storageを作成するためのストレージアカウントを作成します。
    ```bash
    az storage account create --name <ストレージアカウント名> --resource-group <リソースグループ名> --location <リージョン> --sku Standard_LRS --allow-blob-public-access true
    ```
7. 下記のコマンドで、画像保存用のAzure Blob Storageのコンテナを作成します。
    ```bash
    az storage container create --name <コンテナ名> --account-name <ストレージアカウント名>
    ```

### Csutom Vision のセットアップ
1. [Custom Vision ポータル](https://www.customvision.ai/projects) にアクセスし、NEW PROJECT をクリックしてください。
![image](https://github.com/user-attachments/assets/19ec3657-7056-4a51-8469-087eb1266d18)
2. 下記のテーブルのようにプロジェクトを設定してください。
- プロジェクト作成
    | 項目 | 設定値 |
    | --- | --- |
    | Name | 任意のプロジェクト名 |
    | Resource | 新しいリソースを作成 (リソース作成のテーブルをもとに情報を記載してください) |
    | Project Types | Object Detection |
    | Domains | General [A1] |
- リソース作成
    | 項目 | 設定値 |
    | --- | --- |
    | Name | 任意のリソース名 |
    | Subscription | ご利用のサブスクリプション |
    | Resource Group | 作成したリソースグループ名 |
    | Kind | CognitiveServices |
    | Location | 作成したリソースのリージョン |
    | Pricing Tier | S0 |
3. プロジェクトが作成されたら、下記のようなページに遷移したことを確認してください。
![image](https://github.com/user-attachments/assets/eb2ac64d-7b2d-40c5-9ba1-7cfb262a1025)


### ユーザーへのロールの付与
1. 下記のコマンドでサインインしているユーザーのIDを取得します。
    ```bash
    $objectId = az ad signed-in-user show --query id -o tsv
    ```
2. 下記のコマンドでCosmosDBに対して読み取り書き取りができるロールを付与します。
    ```bash
    #### カスタムロールの定義
    $roleId = az cosmosdb sql role definition create --account-name <CosmosDBのアカウント名> --resource-group <リソースグループ名> --body cosmosreadwriterole.json --output tsv --query id

    #### ロールの割り当て
    az cosmosdb sql role assignment create --account-name <CosmosDBのアカウント名> --resource-group <リソースグループ名> --scope "/" --principal-id $objectId --role-definition-id $roleId
    ```
3. 下記のコマンドで、Azure Table Storage および Azure Blob Storage に対して操作ができるようにロールを付与します。
    ```bash
    ### ストレージ アカウント共同作成者のロールを付与
    az role assignment create --assignee $objectId --role "Storage Account Contributor" --scope /subscriptions/<サブスクリプションID>/resourceGroups/<リソースグループ名>

    ### ストレージ BLOB データ所有者のロールを付与
    az role assignment create --assignee $objectId --role "Storage Blob Data Owner" --scope /subscriptions/<サブスクリプションID>/resourceGroups/<リソースグループ名>

    ### ストレージ テーブル データ共同作成者のロールを付与
    az role assignment create --assignee $objectId --role "Storage Table Data Contributor" --scope /subscriptions/<サブスクリプションID>/resourceGroups/<リソースグループ名>
    ```

### 環境変数に必要な情報の取得
ここで取得した情報は、後でプロジェクトのセットアップで使用します。
そのため、取得した情報は適切な場所に保存してください。

1. 下記のコマンドで、Cosmos DB のエンドポイントを取得します。
    ```bash
    az cosmosdb show --name <CosmosDBアカウント名> --resource-group <リソースグループ名> --query "documentEndpoint" --output tsv
    ```
2. 下記のコマンドでAzure OpenAIのエンドポイント、API キーを取得します。
    ```bash
    ### Azure OpenAI のエンドポイントの取得
    az cognitiveservices account show --name <OpenAIリソース名> --resource-group <リソースグループ名> --query "properties.endpoint" --output tsv

    ### Azure OpenAI のキーの取得
    az cognitiveservices account keys list --name <OpenAIリソース名> --resource-group <リソースグループ名> --query "key1" --output tsv
    ```
3. 下記のコマンドで、Azure Blob Storage と Azure Table Storage のエンドポイントを取得します。
    ```bash
    ### Azure Blob Storage のエンドポイントの取得
    az storage account show --name <ストレージアカウント名> --resource-group <リソースグループ名> --query "primaryEndpoints.blob" --output tsv

    ### Azure Table Storage のエンドポイントの取得
    az storage account show --name <ストレージアカウント名> --resource-group <リソースグループ名> --query "primaryEndpoints.table" --output tsv
    ```
4. [Custom Vision ポータル)](https://www.customvision.ai/)の該当のプロジェクトにアクセスし、プロジェクトの設定画面から、プロジェクトID、エンドポイント、キーを取得してください。
![image](https://github.com/user-attachments/assets/aad35bb4-ec4b-4511-a280-5e84f7c05af8)

### プロジェクトのセットアップ
1. リポジトリをクローンします。
    ```bash
    git clone https://github.com/marumaru1019/POC-LostItemSearch.git
    ```
2. データ検索用関数の設定
`fastapi-on-azure-functions`のディレクトリに移動し、次の内容を含む新しい local.settings.json ファイルを追加します。
    ```json
    {
      "IsEncrypted": false,
      "Values": {
        "AzureWebJobsStorage": "",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
        "COSMOS_ENDPOINT": "取得したCosmos DB のエンドポイント",
        "AZURE_OPENAI_ENDPOINT": "取得したAzure OpenAI のエンドポイント",
        "AZURE_OPENAI_API_KEY": "取得したAzure OpenAI のキー",
        "AZURE_OPENAI_DEPLOYMENT": "GPTのデプロイ名",
        "AZURE_BLOB_ACCOUNT_URL": "取得したAzure Blob Storage のエンドポイント",
        "AZURE_TABLE_ENDPOINT": "取得したAzure Table Storage のエンドポイント",
        "CUSTOM_VISION_PROJECT_ID": "Custom Vision のプロジェクトID",
        "CUSTOM_VISION_ENDPOINT": "Custom Vision のエンドポイント",
        "CUSTOM_VISION_TRAINING_KEY": "Custom Vision のキー"
      },
      "Host": {
        "CORS": "*"
      }
    }
    ```

### プロジェクトの実行
#### バックエンドの起動
1. `fastapi-on-azure-functions` ディレクトリに移動し、次のコマンドを実行してPythonの仮想環境を作成し、必要なパッケージをインストールします。
    ```bash
    python -m venv .venv
    . .\.venv\Scripts\activate
    pip install -r requirements.txt
    ```
2. 次のコマンドを実行して、FastAPIを起動します。
    ```bash
    func start
    ```
3. ブラウザで `http://localhost:7071/docs` にアクセスし、検索APIが正常に動作していることを確認します。
![image](https://github.com/user-attachments/assets/ecb192f1-5469-46b3-acf8-89a6a37c7be2)


#### フロントエンドの起動
1. `front` ディレクトリに移動し、`.env.local` ファイルを作成し、次の内容を追加します。
    ```.env.local
    NEXT_PUBLIC_API_BASE_URL=http://localhost:7071
    ```

2. 次のコマンドを実行して、必要なパッケージをインストールします。
    ```bash
    npm install
    ```
3. 次のコマンドを実行して、フロントエンドを起動します。
    ```bash
    npm run dev
    ```
4. ブラウザで `http://localhost:3000` にアクセスし、フロントエンドが正常に動作していることを確認します。
![image](https://github.com/user-attachments/assets/6f355cd1-4616-4538-8634-2fe969d303a1)

### バックエンドのデプロイ (Option)
1. 下記のコマンドで、Azure Functions用のストレージアカウントを作成します。
    ```bash
    az storage account create --name <ストレージアカウント名> --resource-group <リソースグループ名> --location <リージョン> --sku Standard_LRS
    ```
2. 下記のコマンドで、関数アプリを作成します。
    ```bash
    az functionapp create --resource-group <リソースグループ名> --name <関数アプリ名> --consumption-plan-location <リージョン> --runtime python --functions-version 4 --os-type Linux --storage-account <ストレージアカウント名>
    ```
3. 下記のコマンドで関数アプリのマネージドIDを有効化します。
    ```bash
    az functionapp identity assign --name <関数アプリ名> --resource-group <リソースグループ名>
    ```
4. 下記のコマンドで、関数アプリのマネージドIDを取得します。
    ```bash
    az functionapp identity show --name <関数アプリ名> --resource-group <リソースグループ名> --query principalId -o tsv
    ```
5. ユーザーへのロール付与で作成したCosmosDBのカスタムロールを関数アプリに割り当てます。
    ```bash
    az cosmosdb sql role assignment create --account-name <CosmosDBのアカウント名> --resource-group <リソースグループ名> --scope "/" --principal-id <関数アプリのマネージドID> --role-definition-id $roleId
    ```
6. 下記のコマンドで、関数アプリにストレージアカウントのロールを付与します。
    ```bash
    ### ストレージ アカウント共同作成者のロールを付与
    az role assignment create --assignee <関数アプリのマネージドID> --role "Storage Account Contributor" --scope /subscriptions/<サブスクリプションID>/resourceGroups/<リソースグループ名>

    ### ストレージ BLOB データ所有者のロールを付与
    az role assignment create --assignee <関数アプリのマネージドID> --role "Storage Blob Data Owner" --scope /subscriptions/<サブスクリプションID>/resourceGroups/<リソースグループ名>

    ### ストレージ テーブル データ共同作成者のロールを付与
    az role assignment create --assignee <関数アプリのマネージドID> --role "Storage Table Data Contributor" --scope /subscriptions/<サブスクリプションID>/resourceGroups/<リソースグループ名>
    ```

7. `fastapi-on-azure-functions` ディレクトリに移動し、次のコマンドを実行して関数アプリをデプロイします。
    ```bash
    func azure functionapp publish <関数アプリ名>
    ```
8. 下記のコマンドを実行して、関数アプリに環境変数を設定します。
    ```bash
    az functionapp config appsettings set --name <関数アプリ名> --resource-group <リソースグループ名> --settings COSMOS_ENDPOINT="取得したCosmos DB のUri" AZURE_OPENAI_ENDPOINT="取得したAzure OpenAI のエンドポイント" AZURE_OPENAI_API_KEY="取得したAzure OpenAI のキー" AZURE_OPENAI_DEPLOYMENT="GPTのデプロイ名" AZURE_BLOB_ACCOUNT_URL="取得したAzure Blob Storage のエンドポイント" AZURE_TABLE_ENDPOINT="取得したAzure Table Storage のエンドポイント" CUSTOM_VISION_PROJECT_ID="Custom Vision のプロジェクトID" CUSTOM_VISION_ENDPOINT="Custom Vision のエンドポイント" CUSTOM_VISION_TRAINING_KEY="Custom Vision のキー"
    ```
    
9. ブラウザで `https://<関数アプリ名>.azurewebsites.net/docs` にアクセスし、検索APIが正常に動作していることを確認します。
![image](https://github.com/user-attachments/assets/026b9cef-53fb-4826-8ae6-20d3eadd1a5f)

### フロントエンドのデプロイ (Option)
1. GitHub 経由でデプロイを行うため、事前に GitHub にリポジトリを作成してください。作成したリポジトリにこのプロジェクトをプッシュしてください。
```bash
git remote add origin <作成したGitHubリポジトリURL>
git add .
git commit -m "<任意のコミットメッセージ>"
git push origin main
```

2. Azure Portal にログインし、Azure Static Web Apps を検索して、新しいアプリケーションを作成します。これによりAzure Static Web Apps が GitHub リポジトリと連携され、デプロイが自動的に行われます。
    | 項目 | 設定値 |
    | --- | --- |
    | サブスクリプション | ご利用のサブスクリプション |
    | リソースグループ | 作成したリソースグループ名 |
    | 名前 | 任意のアプリケーション名 |
    | プラン | 任意のプラン |
    | リージョン | 任意のリージョン |
    | ソース | GitHub |
    | GitHub アカウント | ご利用の GitHub アカウント |
    | 組織 | ご利用の GitHub 組織 |
    | リポジトリ | 作成したリポジトリ |
    | ブランチ | main |
    | ビルドのプリセット | Next.js |
    | アプリの場所 | ./front |
    | API の場所 | 空にしておいてください |
    | 出力先 | 空にしておいてください |
    | Deployment authentication policy | GitHub |
    | Azure Functions API とステージング環境のリージョン | 任意のリージョン |


    ![image](https://github.com/user-attachments/assets/cda4819b-d2d4-40d2-90e4-852ad841f2d7)

3. デプロイの自動化の際に、フロントエンドの環境変数を設定します。1の手順で作成したGitHubのリポジトリから、`Settings` > `Secrets & variables` > `Actions` に移動し、次の環境変数を設定します。
    | 環境変数 | 値 |
    | --- | --- |
    | NEXT_PUBLIC_API_BASE_URL | https://<関数アプリ名>.azurewebsites.net |

    ![image](https://github.com/user-attachments/assets/0eba4b5d-cbad-4684-a40d-7fdb7391ca2e)

4. `Code`タブに移動すると、リポジトリに`.github/workflows`ディレクトリが作成されていることを確認してください。この中に`azure-static-web-apps-xxx.yml`ファイルが作成されているはずです。このファイルを下記のように編集して`NEXT_PUBLIC_API_BASE_URL`を環境変数として設定します。
    ```:azure-static-web-apps-xxx.yml
    ...
    ...
    app_location: "./front" # App source code path
        api_location: "" # Api source code path - optional
        output_location: "" # Built app content directory - optional
        ###### End of Repository/Build Configurations ######
    env:　# この箇所を追加
        NEXT_PUBLIC_API_BASE_URL: ${{ secrets.NEXT_PUBLIC_API_BASE_URL }}
    ...
    ...
    ```

    ![image](https://github.com/user-attachments/assets/f138a5f7-c6d1-4b3c-a622-9fe2e79f78b5)

5. この変更を加えた後`main`ブランチにプッシュすると、Azure Static Web Apps に自動デプロイが開始されます。

6. 下記のコマンドで Azure Static Web Apps のマネージド ID を有効化します。
    ```bash
    az staticwebapp identity assign --name <アプリケーション名> --resource-group <リソースグループ名>
    ```
7. 下記のコマンドで、Azure Static Web Apps のマネージド ID を取得します。
    ```bash
    $roleId = az staticwebapp identity show --name <アプリケーション名> --resource-group <リソースグループ名> --query principalId -o tsv
    ```
8. 下記のコマンドで、Azure Static Web Apps に 画像保存用の Azure Blob Storage の閲覧権限を付与します。
    ```bash
    az role assignment create --assignee $roleId --role "Storage Blob Data Reader" --scope /subscriptions/<サブスクリプションID>/resourceGroups/<リソースグループ名>
    ```

### 動作確認
1. まず、ラベル付けのベースとなるデータを Azure Table Storage に登録します。
ブラウザで `https://<関数アプリ名>.azurewebsites.net/docs` にアクセスし、
 `POST /labels` でラベルを登録します。keywordにラベル名(品名やカラーコードなどが該当)を入れてください(imageTypeは空で問題ないです)。ここで登録したラベルが、データ登録の際に画像をスキャンした際にkeywordとしてレコメンドされます(登録シナリオにおいて自動ラベル付けを行うために5-10個ほどサンプルデータを登録しておくと良いです)。登録したラベルは、`GET /labels` で確認できます。
    ```json
    {
    "keyword": "ラベル名",
    "imageType": ""
    }
    ```

    ![image](https://github.com/user-attachments/assets/8dd31a6c-0a47-4530-91a6-be5b67efe87b)

2. 【登録シナリオ】次に、フロントエンドの URL にアクセスし、`遺失物の登録`をクリックして、遺失物の情報を登録します。
    - 2.1. トップページで、`遺失物の登録`をクリックします。
    ![image](https://github.com/user-attachments/assets/f9f39c90-7032-47da-ba14-fd8f601d3b16)
    - 2.2. 画像をアップロードをクリックして、任意の画像をアップロードします。
    - 2.3. スキャン画像をクリックして、画像をスキャンします。スキャンした画像に対して、登録したラベルがレコメンドされます。登録したラベルが正しいか確認し、必要に応じて修正してください。
    - 2.4. 他の情報を入力し、`登録`をクリックして、遺失物の情報を登録します(取得時間は必須項目のため、記入しないと登録ができません)。
    ![image](https://github.com/user-attachments/assets/0cae1e68-349f-42a2-bfe3-69507ed14f3a)

3. 【学習シナリオ】トップページに戻り、`ラベルチェック`をクリックして、ラベルの学習を行います。
    - 3.1. ラベルチェックがされていない遺失物の一覧が表示されます。この中から、ラベルチェックを行いたい遺失物を選択します。
    ![image](https://github.com/user-attachments/assets/cfa695fe-5264-45ee-9e2f-e9fb5c9f07ce)
    - 3.2. キーワードを編集したい場合はカンマ区切りでキーワードを入力し、`キーワードの更新`をクリックします。このままのラベルのままキーワードを登録したい場合は、`このままでOK`をクリックします。
    ![image](https://github.com/user-attachments/assets/b0c2c377-3ae7-4baf-aaf9-f6eb7e53a6d5)
    - 3.3. [Custom Vision ポータル](https://www.customvision.ai/projects) にアクセスし、プロジェクトに移動します。プロジェクトに登録された画像が表示され、画像に対してラベルが付与されていることを確認します。15枚以上の画像が登録されている場合、学習を開始することができます。
    ![image](https://github.com/user-attachments/assets/6a953f97-9a76-43e8-973e-2130d25d7776)
4. 【検索シナリオ】トップページに戻り、`遺失物の検索`をクリックして、遺失物の検索を行います。
    - 4.1. 学習シナリオにてキーワードの確認を行った遺失物の一覧が表示されていることを確認します。
    ![image](https://github.com/user-attachments/assets/bbd9bf61-6131-4308-8858-aee98e8c2f80)
    - 4.2. 登録したキーワードに対して検索を行いたい場合、検索窓からキーワードを入力し、`検索`をクリックします。登録したキーワードに近い用語が検索され、遺失物の一覧が表示されます。
    ![image](https://github.com/user-attachments/assets/49e71ae1-3609-44d5-ad59-fc0e6a81fe69)
