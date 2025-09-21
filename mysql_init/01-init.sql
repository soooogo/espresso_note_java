-- MySQL初期化スクリプト
-- データベースとユーザーの作成

-- データベースが存在しない場合は作成
CREATE DATABASE IF NOT EXISTS demo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ユーザーが存在しない場合は作成
CREATE USER IF NOT EXISTS 'demo_user'@'%' IDENTIFIED BY 'demo_password';

-- ユーザーに権限を付与
GRANT ALL PRIVILEGES ON demo_db.* TO 'demo_user'@'%';

-- 権限を反映
FLUSH PRIVILEGES;

-- demo_dbを使用
USE demo_db;

-- テーブルが存在しない場合は作成（Spring BootのJPAが自動生成するため、ここでは作成しない）
-- 必要に応じて初期データを挿入

