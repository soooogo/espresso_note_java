#!/bin/bash

echo "=== データ永続化デバッグスクリプト ==="
echo "このスクリプトは、データベースの永続化と重複挿入防止機能をテストします。"
echo ""

# 色付きの出力用関数
print_success() {
    echo -e "\033[32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[31m❌ $1\033[0m"
}

print_info() {
    echo -e "\033[34mℹ️  $1\033[0m"
}

print_warning() {
    echo -e "\033[33m⚠️  $1\033[0m"
}

# データベースの状態を確認する関数
check_database_status() {
    echo "📊 データベースの現在の状態を確認中..."
    
    # Docker Composeでサービスが起動しているかチェック
    if ! docker-compose ps | grep -q "Up"; then
        print_warning "Docker Composeサービスが起動していません。起動しますか？ (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "Docker Composeサービスを起動中..."
            docker-compose up -d
            echo "サービス起動完了。30秒待機中..."
            sleep 30
        else
            print_error "サービスが起動していないため、テストを中止します。"
            exit 1
        fi
    fi
    
    # MySQLに接続してデータ数を確認
    echo "MySQLデータベースの状態を確認中..."
    docker-compose exec mysql mysql -u demo_user -pdemo_password demo_db -e "
        SELECT 
            'users' as table_name, COUNT(*) as count FROM users
        UNION ALL
        SELECT 
            'beans' as table_name, COUNT(*) as count FROM beans
        UNION ALL
        SELECT 
            'recipe' as table_name, COUNT(*) as count FROM recipe;
    " 2>/dev/null || {
        print_error "MySQLデータベースに接続できません。"
        return 1
    }
}

# 初回起動テスト
test_first_startup() {
    echo ""
    echo "=== テスト1: 初回起動（データベースが空の場合） ==="
    
    print_info "データベースをクリアして初回起動をシミュレート..."
    
    # データベースをクリア
    docker-compose exec mysql mysql -u demo_user -pdemo_password demo_db -e "
        DELETE FROM recipe;
        DELETE FROM beans;
        DELETE FROM users;
    " 2>/dev/null
    
    print_info "データベースをクリアしました。"
    
    # Spring Bootアプリケーションを再起動
    print_info "Spring Bootアプリケーションを再起動中..."
    docker-compose restart springboot
    
    # 起動完了を待機
    echo "起動完了を待機中..."
    sleep 60
    
    # データが挿入されたかチェック
    check_database_status
    
    print_success "初回起動テスト完了"
}

# 2回目起動テスト
test_second_startup() {
    echo ""
    echo "=== テスト2: 2回目起動（既存データがある場合） ==="
    
    print_info "既存データがある状態でSpring Bootアプリケーションを再起動..."
    
    # Spring Bootアプリケーションを再起動
    docker-compose restart springboot
    
    # 起動完了を待機
    echo "起動完了を待機中..."
    sleep 60
    
    # データが重複していないかチェック
    check_database_status
    
    print_success "2回目起動テスト完了"
}

# CSVデータ挿入テスト
test_csv_insertion() {
    echo ""
    echo "=== テスト3: CSVデータ挿入テスト ==="
    
    print_info "CSVデータ挿入スクリプトを実行..."
    
    # CSVデータ挿入スクリプトを実行
    docker-compose exec backend python3 insert_data.py
    
    print_success "CSVデータ挿入テスト完了"
}

# 重複挿入テスト
test_duplicate_prevention() {
    echo ""
    echo "=== テスト4: 重複挿入防止テスト ==="
    
    print_info "既存データがある状態でCSVデータ挿入スクリプトを再実行..."
    
    # CSVデータ挿入スクリプトを再実行
    docker-compose exec backend python3 insert_data.py
    
    print_success "重複挿入防止テスト完了"
}

# ログ確認
check_logs() {
    echo ""
    echo "=== ログ確認 ==="
    
    print_info "Spring Bootアプリケーションのログを確認..."
    echo "--- Spring Boot ログ (最新20行) ---"
    docker-compose logs --tail=20 springboot
    
    echo ""
    print_info "Backendサービスのログを確認..."
    echo "--- Backend ログ (最新20行) ---"
    docker-compose logs --tail=20 backend
}

# メイン実行
main() {
    echo "データ永続化デバッグを開始します。"
    echo "各テストは順次実行されます。"
    echo ""
    
    # 現在の状態を確認
    check_database_status
    
    # テストを実行
    test_first_startup
    test_second_startup
    test_csv_insertion
    test_duplicate_prevention
    
    # ログを確認
    check_logs
    
    echo ""
    print_success "すべてのデバッグテストが完了しました！"
    echo ""
    echo "=== デバッグ結果の確認方法 ==="
    echo "1. 上記のログ出力で各テストの結果を確認"
    echo "2. データベースの状態変化を確認"
    echo "3. 重複データが挿入されていないことを確認"
    echo ""
    echo "問題がある場合は、ログを詳しく確認してください。"
}

# スクリプト実行
main "$@"
