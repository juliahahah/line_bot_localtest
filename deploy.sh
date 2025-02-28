#!/bin/bash

# Line Bot Lambda 部署腳本

echo "===== 開始部署 Line Bot Lambda 函數 ====="

# 創建臨時目錄
echo "創建部署包目錄..."
mkdir -p deployment/package

# 安裝依賴包
echo "安裝 Line Bot SDK..."
pip install --target ./deployment/package line-bot-sdk

# 複製 Lambda 函數到部署包
echo "複製 Lambda 函數代碼..."
cp lambda_function.py deployment/package/

# 創建 ZIP 部署包
echo "創建部署包..."
cd deployment/package
zip -r ../deployment_package.zip .
cd ../..

echo "部署包已創建: deployment/deployment_package.zip"

# 檢查是否提供 Lambda 函數名稱
if [ -z "$1" ]; then
  echo "使用說明: ./deploy.sh <lambda-function-name>"
  echo "未指定 Lambda 函數名稱，部署結束。"
  exit 1
fi

# 使用 AWS CLI 更新 Lambda 函數
echo "上傳部署包到 Lambda 函數: $1..."
aws lambda update-function-code \
  --function-name $1 \
  --zip-file fileb://deployment/deployment_package.zip

echo "===== 部署完成 ====="
echo "請確保在 Lambda 環境變量中設置了以下內容:"
echo "  - CHANNEL_ACCESS_TOKEN: Line Channel Access Token"
echo "  - CHANNEL_SECRET: Line Channel Secret"
