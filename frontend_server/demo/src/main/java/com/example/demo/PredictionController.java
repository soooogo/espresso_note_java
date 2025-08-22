package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/predict")
public class PredictionController {

    @Autowired
    private RestTemplate restTemplate;

    private final String FASTAPI_URL = "http://localhost:8081";

    @PostMapping("/coffee")
    public ResponseEntity<?> predictCoffee(@RequestBody Map<String, Object> request) {
        try {
            // FastAPIサーバーにリクエストを転送
            String fastApiUrl = FASTAPI_URL + "/predict";
            
            // リクエストをFastAPIの形式に変換
            Map<String, Object> fastApiRequest = new HashMap<>();
            fastApiRequest.put("bean_name", request.get("bean_name"));
            fastApiRequest.put("bean_origin", request.get("bean_origin"));
            fastApiRequest.put("date", request.get("date"));
            fastApiRequest.put("weather", request.get("weather"));
            fastApiRequest.put("temperature", request.get("temperature"));
            fastApiRequest.put("humidity", request.get("humidity"));

            // FastAPIにリクエストを送信
            ResponseEntity<Map> response = restTemplate.postForEntity(
                fastApiUrl, 
                fastApiRequest, 
                Map.class
            );

            return ResponseEntity.ok(response.getBody());

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "予測エラー: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/beans")
    public ResponseEntity<?> getBeans() {
        try {
            // Spring Bootで直接MySQLから豆情報を取得
            List<Map<String, Object>> beans = getAllBeansFromDatabase();
            return ResponseEntity.ok(beans);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "豆情報取得エラー: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/user-beans")
    public ResponseEntity<?> getUserBeans() {
        try {
            // 現在のユーザーIDを取得（認証情報から）
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            String username = auth.getName();
            
            // 認証されていない場合やデフォルトユーザーの場合
            if (username == null || username.equals("anonymousUser") || username.isEmpty()) {
                // 全ユーザーの豆情報を返す（デフォルト）
                List<Map<String, Object>> beans = getAllBeansFromDatabase();
                return ResponseEntity.ok(beans);
            }
            
            // ユーザーIDを取得
            Integer userId = getUserIdByUsername(username);
            
            if (userId == null) {
                // ユーザーが見つからない場合は全ユーザーの豆情報を返す
                List<Map<String, Object>> beans = getAllBeansFromDatabase();
                return ResponseEntity.ok(beans);
            }
            
            // Spring Bootで直接MySQLから豆情報を取得
            List<Map<String, Object>> beans = getUserBeansFromDatabase(userId);
            return ResponseEntity.ok(beans);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "ユーザー豆情報取得エラー: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }
    
    private Integer getUserIdByUsername(String username) {
        try {
            // データベースからユーザーIDを取得
            String url = "jdbc:mysql://localhost:3306/demo_db";
            String dbUsername = "root";
            String dbPassword = "password";
            
            try (Connection conn = DriverManager.getConnection(url, dbUsername, dbPassword);
                 PreparedStatement stmt = conn.prepareStatement("SELECT id FROM users WHERE email = ?")) {
                
                stmt.setString(1, username);
                ResultSet rs = stmt.executeQuery();
                
                if (rs.next()) {
                    return rs.getInt("id");
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    private List<Map<String, Object>> getUserBeansFromDatabase(Integer userId) {
        List<Map<String, Object>> beans = new ArrayList<>();
        try {
            String url = "jdbc:mysql://localhost:3306/demo_db";
            String dbUsername = "root";
            String dbPassword = "password";
            
            try (Connection conn = DriverManager.getConnection(url, dbUsername, dbPassword);
                 PreparedStatement stmt = conn.prepareStatement(
                     "SELECT b.id, b.name, b.from_location, u.name as user_name " +
                     "FROM beans b " +
                     "JOIN users u ON b.user_id = u.id " +
                     "WHERE b.user_id = ? " +
                     "ORDER BY b.name")) {
                
                stmt.setInt(1, userId);
                ResultSet rs = stmt.executeQuery();
                
                while (rs.next()) {
                    Map<String, Object> bean = new HashMap<>();
                    bean.put("id", rs.getInt("id"));
                    bean.put("name", rs.getString("name"));
                    bean.put("origin", rs.getString("from_location"));
                    bean.put("user_name", rs.getString("user_name"));
                    beans.add(bean);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return beans;
    }
    
    private List<Map<String, Object>> getAllBeansFromDatabase() {
        List<Map<String, Object>> beans = new ArrayList<>();
        try {
            String url = "jdbc:mysql://localhost:3306/demo_db";
            String dbUsername = "root";
            String dbPassword = "password";
            
            try (Connection conn = DriverManager.getConnection(url, dbUsername, dbPassword);
                 PreparedStatement stmt = conn.prepareStatement(
                     "SELECT b.id, b.name, b.from_location, u.name as user_name " +
                     "FROM beans b " +
                     "JOIN users u ON b.user_id = u.id " +
                     "ORDER BY b.name")) {
                
                ResultSet rs = stmt.executeQuery();
                
                while (rs.next()) {
                    Map<String, Object> bean = new HashMap<>();
                    bean.put("id", rs.getInt("id"));
                    bean.put("name", rs.getString("name"));
                    bean.put("origin", rs.getString("from_location"));
                    bean.put("user_name", rs.getString("user_name"));
                    beans.add(bean);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return beans;
    }

    @GetMapping("/weather")
    public ResponseEntity<?> getCurrentWeather() {
        try {
            // 現在の気象データを取得（簡易版）
            Map<String, Object> weatherData = new HashMap<>();
            weatherData.put("location", "京都府京都市左京区");
            weatherData.put("temperature", 20.0);  // デフォルト値
            weatherData.put("humidity", 60.0);     // デフォルト値
            weatherData.put("timestamp", java.time.LocalDateTime.now().toString());
            weatherData.put("note", "デフォルト値を使用しています");
            
            return ResponseEntity.ok(weatherData);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "気象データ取得エラー: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/health")
    public ResponseEntity<?> getHealth() {
        try {
            // Spring Bootアプリケーションのヘルスチェック
            Map<String, Object> healthData = new HashMap<>();
            healthData.put("status", "healthy");
            healthData.put("application", "Spring Boot Coffee Prediction");
            healthData.put("timestamp", java.time.LocalDateTime.now().toString());
            
            // FastAPIの接続確認
            try {
                String fastApiUrl = FASTAPI_URL + "/health";
                ResponseEntity<Map> response = restTemplate.getForEntity(
                    fastApiUrl, 
                    Map.class
                );
                healthData.put("fastapi_status", "connected");
                healthData.put("fastapi_data", response.getBody());
            } catch (Exception e) {
                healthData.put("fastapi_status", "disconnected");
                healthData.put("fastapi_error", e.getMessage());
            }
            
            return ResponseEntity.ok(healthData);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "ヘルスチェックエラー: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }
}
