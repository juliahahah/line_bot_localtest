# Chiikawa LINE 聊天機器人

這是一個由 AWS 支援的 LINE 聊天機器人應用程式，回應使用者訊息時會包含自定義格式，包括使用者名稱和使用者 ID。

## 設置與部署說明

### CloudFormation 部署指南

我們將使用 CloudFormation 來佈建本次工作坊所需的資源。

首先在 **Infrastructure Composer** 中建立模板，該模板將存儲在 S3 儲存桶中。然後，繼續前往 **Create stack** 部分完成剩餘步驟。

#### Infrastructure Composer 步驟

前往 "Infrastructure Composer" 頁面，然後：

1. 切換到 "Template" 視圖
2. 貼上 YAML 檔案的內容 (`template.yaml`)
3. 點擊 "Validate" 驗證一切正常
4. 然後，點擊 "Create Template"
5. 系統會自動生成 S3 儲存桶 URL，彈出窗口將幫助引導至 "Create Stack" 部分

#### Stacks 步驟

1. 建立堆疊：預設應選擇 "**Build from Infrastructure Composer**"，且 "**S3 URL**" 會自動填入
2. 指定堆疊詳細信息：提供堆疊名稱和模板中定義的參數
3. 配置堆疊選項：保持預設選項不變
4. 審核並建立：確認所有內容符合要求

審核後，點擊 "Submit" 並等待 3-5 分鐘完成資源建立。

### 準備部署套件

在將應用程式部署到 AWS Lambda 前，我們需要先準備好所有必要的檔案和依賴項。下面是準備部署套件的詳細步驟。

### 安裝相依套件

首先，我們需要安裝機器人運行所需的 Python 套件，並將它們打包成 Lambda 可以使用的格式。

#### 建立必要檔案的 ZIP 壓縮檔(這部分學員可以不用做 但是之後想學的話要下載座新的line_bot套件唷！)

1. 切換到應用程式目錄並安裝所需套件：

```bash
mkdir app
cd app
mkdir package
pip install line-bot-sdk python-dotenv --target ./package
```

2. 建立 ZIP 壓縮檔：

- **Mac/Linux 用戶**：
```bash
zip -r ./package.zip package
```

- **Windows 用戶**：
```bash

Compress-Archive -Path "package\*" -DestinationPath "package.zip"
```

3. 加入lamdbda_function.py的程式碼

添加你要寫的程式碼



### 部署到 AWS Lambda

有兩種方式可以上傳部署套件到 Lambda 函數：

#### 方法一：直接上傳 ZIP 檔案

1. 登入 AWS Console
2. 導航至 Lambda 服務
3. 找到名為 "auto-chiikawa-linebot" 的函數
4. 點擊函數開啟其設定頁面
5. 上傳 ZIP 套件：
   - 點擊 "Upload from" 下拉選單
   - 選擇 ".zip 檔案"
   - 上傳先前建立的 package.zip 檔案
   - 點擊 "Save" 儲存變更

#### 方法二：使用 S3 上傳（適合大於 50MB 的套件）

1. 登入 AWS Console
2. 導航至 S3 服務
3. 選擇或建立一個儲存桶
4. 上傳先前建立的 package.zip 檔案到該儲存桶
5. 記下檔案的 S3 URI
6. 導航至 Lambda 服務
7. 找到名為 "auto-chiikawa-linebot" 的函數
8. 點擊函數開啟其設定頁面
9. 點擊 "Upload from" 下拉選單
10. 選擇 "Amazon S3 location"
11. 輸入 package.zip 檔案的 S3 URI
12. 點擊 "Save" 儲存變更

### 設定 API Gateway

完成 Lambda 部署後，我們需要設定 API Gateway 以便 LINE 平台可以與我們的機器人通訊：

1. 在 AWS Console 中，導航至 API Gateway 服務
2. 找到名為 "auto-chiikawa-api" 的 API
3. 點擊該 API 開啟其設定
4. 前往 "Stages" 部分
5. 找到並複製 "Invoke URL" - 這是您的 webhook URL
6. 確保 API 的方法和整合已正確設置，指向您的 Lambda 函數

### 設定 LINE Developer Console

1. 登入 LINE Developer Console
2. 導航至您的機器人的提供者和頻道
3. 在頻道設定中，找到 Webhook URL 欄位
4. 貼上您剛才複製的 API Gateway Invoke URL
5. 儲存更改並點擊 "Verify" 按鈕測試 webhook 連接
6. 確保在 "Messaging API" 設定中啟用了 "Use webhook"

## 取得 LINE Channel Access Token 和 Channel Secret

1. 登入 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇您的 Provider，或建立一個新的 Provider
3. 建立一個新的 Channel (選擇 Messaging API)
4. 在 Channel 設定頁面中：
   - 在 "Basic settings" 選項卡下，可以找到 "Channel secret"
   - 在 "Messaging API" 選項卡下，點擊 "Issue" 按鈕來發行 "Channel access token"
5. 記下這兩個值，它們將用於設定 Lambda 函數的環境變數


## 機器人行為

機器人將以以下格式回應使用者訊息：
```
{使用者名稱}({使用者ID})呀哈~等等唷!我在幫你分析{使用者訊息}
```

## 問題排除

若機器人無法正常運作，請檢查：
1. Lambda 函數的日誌（CloudWatch Logs）
2. API Gateway 設定是否正確
3. LINE 開發者控制台中的 webhook URL 是否填寫正確
4. 環境變數是否已正確設定

## 聯絡與支援

如有任何問題，請聯繫工作坊講師或在 GitHub 專案中提出 Issue。

