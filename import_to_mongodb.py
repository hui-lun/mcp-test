#!/usr/bin/env python3
import json
import pymongo
from pymongo import MongoClient
from typing import List, Dict, Any

def connect_to_mongodb(uri: str = "mongodb://192.168.1.221:27017/") -> MongoClient:
    """連接到 MongoDB"""
    try:
        client = MongoClient(uri)
        # 測試連接
        client.admin.command('ping')
        print(f"成功連接到 MongoDB: {uri}")
        return client
    except Exception as e:
        print(f"連接 MongoDB 失敗: {e}")
        raise

def load_json_data(file_path: str) -> List[Dict[Any, Any]]:
    """讀取 JSON 檔案"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"成功讀取 {file_path}，共 {len(data)} 筆資料")
            return data
    except Exception as e:
        print(f"讀取 JSON 檔案失敗: {e}")
        raise

def insert_data_to_mongodb(client: MongoClient, database_name: str, collection_name: str, data: List[Dict[Any, Any]]) -> None:
    """將資料插入到 MongoDB"""
    try:
        # 選擇資料庫和集合
        db = client[database_name]
        collection = db[collection_name]
        
        # 清空現有資料（可選）- 註解掉因為需要認證權限
        # print(f"清空集合 {collection_name} 中現有資料...")
        # collection.delete_many({})
        
        # 批次插入資料
        print(f"開始插入資料到 {database_name}.{collection_name}...")
        result = collection.insert_many(data)
        
        print(f"成功插入 {len(result.inserted_ids)} 筆資料")
        return result.inserted_ids
        
    except Exception as e:
        print(f"插入資料失敗: {e}")
        raise

def main():
    # 設定參數
    MONGODB_URI = "mongodb://admin:password@192.168.1.221:27017/"
    DATABASE_NAME = "spec"
    COLLECTION_NAME = "sepc-all"
    JSON_FILE_PATH = "/app/spec.json"
    
    try:
        # 1. 連接 MongoDB
        print("=== 開始連接 MongoDB ===")
        client = connect_to_mongodb(MONGODB_URI)
        
        # 2. 讀取 JSON 資料
        print("\n=== 讀取 JSON 檔案 ===")
        data = load_json_data(JSON_FILE_PATH)
        
        # 3. 插入資料到 MongoDB
        print("\n=== 插入資料到 MongoDB ===")
        inserted_ids = insert_data_to_mongodb(client, DATABASE_NAME, COLLECTION_NAME, data)
        
        # 4. 驗證插入結果
        print("\n=== 驗證插入結果 ===")
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        count = collection.count_documents({})
        print(f"資料庫中目前共有 {count} 筆資料")
        
        # 顯示第一筆資料作為範例
        first_doc = collection.find_one()
        if first_doc:
            print(f"第一筆資料的 ProjectModel: {first_doc.get('ProjectModel', 'N/A')}")
        
        print("\n=== 資料匯入完成 ===")
        
    except Exception as e:
        print(f"程式執行失敗: {e}")
    finally:
        if 'client' in locals():
            client.close()
            print("MongoDB 連接已關閉")

if __name__ == "__main__":
    main()