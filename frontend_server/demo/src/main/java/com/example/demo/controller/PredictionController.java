package com.example.demo.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
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
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import com.fasterxml.jackson.databind.ObjectMapper;

@RestController
@RequestMapping("/api/predict")
public class PredictionController {

    @Autowired
    private RestTemplate restTemplate;

    private final String FASTAPI_URL = "http://fastapi:8081";
    
    @Value("${spring.datasource.url}")
    private String dbUrl;
    
    @Value("${spring.datasource.username}")
    private String dbUsername;
    
    @Value("${spring.datasource.password}")
    private String dbPassword;

    @PostMapping("/coffee")
    public ResponseEntity<?> predictCoffee(@RequestBody Map<String, Object> request) {
        try {
            // 動的モデル構築用のFastAPIエンドポイントを使用
            String fastApiUrl = FASTAPI_URL + "/predict-dynamic";
            
            // リクエストをFastAPIの形式に変換
            Map<String, Object> fastApiRequest = new HashMap<>();
            String beanName = (String) request.get("bean_name");
            fastApiRequest.put("bean_name", beanName);
            
            // beansテーブルから産地情報を取得
            String beanOrigin = getBeanOriginFromDatabase(beanName);
            fastApiRequest.put("bean_origin", beanOrigin);
            
            fastApiRequest.put("date", request.get("date"));
            fastApiRequest.put("weather", request.get("weather"));
            fastApiRequest.put("temperature", request.get("temperature"));
            fastApiRequest.put("humidity", request.get("humidity"));
            fastApiRequest.put("days_passed", request.get("days_passed"));

            // FastAPIにリクエストを送信
            ResponseEntity<Map> response = restTemplate.postForEntity(
                fastApiUrl, 
                fastApiRequest, 
                Map.class
            );

            return ResponseEntity.ok(response.getBody());

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            String errorMessage = e.getMessage();
            
            // FastAPIからのエラーメッセージを抽出
            if (errorMessage.contains("detail")) {
                // JSONレスポンスからエラーメッセージを抽出
                try {
                    int detailStart = errorMessage.indexOf("\"detail\":\"") + 10;
                    int detailEnd = errorMessage.indexOf("\"", detailStart);
                    if (detailStart > 9 && detailEnd > detailStart) {
                        errorMessage = errorMessage.substring(detailStart, detailEnd);
                    }
                } catch (Exception ex) {
                    // 抽出に失敗した場合は元のメッセージを使用
                }
            }
            
            error.put("error", errorMessage);
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

    @GetMapping("/bean-history")
    public ResponseEntity<?> getBeanHistory(@RequestParam String bean_name) {
        try {
            // 指定された豆の履歴データを取得
            List<Map<String, Object>> history = getBeanHistoryFromDatabase(bean_name);
            return ResponseEntity.ok(history);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "豆履歴取得エラー: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }
    
    private Integer getUserIdByUsername(String username) {
        try {
            // データベースからユーザーIDを取得
            try (Connection conn = DriverManager.getConnection(dbUrl, dbUsername, dbPassword);
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
            try (Connection conn = DriverManager.getConnection(dbUrl, dbUsername, dbPassword);
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
            try (Connection conn = DriverManager.getConnection(dbUrl, dbUsername, dbPassword);
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
            // OpenWeatherMap APIから京都の現在の気象データを取得（無料版）
            Map<String, Object> weatherData = getWeatherFromAPI();
            return ResponseEntity.ok(weatherData);

        } catch (Exception e) {
            // API取得に失敗した場合はデフォルト値を返す
            Map<String, Object> weatherData = new HashMap<>();
            weatherData.put("location", "京都府京都市左京区");
            weatherData.put("temperature", 20.0);
            weatherData.put("humidity", 60.0);
            weatherData.put("weather", "Clear");
            weatherData.put("description", "晴れ");
            weatherData.put("timestamp", java.time.LocalDateTime.now().toString());
            weatherData.put("note", "API取得に失敗したため、デフォルト値を使用しています");
            
            return ResponseEntity.ok(weatherData);
        }
    }
    
    private Map<String, Object> getWeatherFromAPI() throws Exception {
        // OpenWeatherMap APIの設定（無料版）
        String apiKey = System.getenv("OPENWEATHER_API_KEY"); // 環境変数から取得
        if (apiKey == null || apiKey.isEmpty()) {
            throw new Exception("OpenWeatherMap APIキーが設定されていません");
        }
        
        // 京都の座標（左京区付近）
        double lat = 35.0116;
        double lon = 135.7681;
        
        String url = String.format(
            "http://api.openweathermap.org/data/2.5/weather?lat=%.4f&lon=%.4f&appid=%s&units=metric&lang=ja",
            lat, lon, apiKey
        );
        
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .build();
        
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        
        if (response.statusCode() != 200) {
            throw new Exception("APIリクエストが失敗しました: " + response.statusCode());
        }
        
        // JSONレスポンスをパース
        ObjectMapper mapper = new ObjectMapper();
        Map<String, Object> jsonResponse = mapper.readValue(response.body(), Map.class);
        
        // 必要なデータを抽出
        Map<String, Object> main = (Map<String, Object>) jsonResponse.get("main");
        List<Map<String, Object>> weather = (List<Map<String, Object>>) jsonResponse.get("weather");
        Map<String, Object> weatherData = new HashMap<>();
        
        weatherData.put("location", "京都府京都市左京区");
        weatherData.put("temperature", main.get("temp"));
        weatherData.put("humidity", main.get("humidity"));
        weatherData.put("timestamp", java.time.LocalDateTime.now().toString());
        weatherData.put("note", "OpenWeatherMap API（無料版）から取得");
        
        // 天候情報を追加
        if (weather != null && !weather.isEmpty()) {
            Map<String, Object> weatherInfo = weather.get(0);
            weatherData.put("weather", weatherInfo.get("main"));
            weatherData.put("description", weatherInfo.get("description"));
        }
        
        return weatherData;
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
    
    private List<Map<String, Object>> getBeanHistoryFromDatabase(String beanName) {
        List<Map<String, Object>> history = new ArrayList<>();
        try {
            try (Connection conn = DriverManager.getConnection(dbUrl, dbUsername, dbPassword);
                 PreparedStatement stmt = conn.prepareStatement(
                     "SELECT r.date, r.weather, r.temperature, r.humidity, " +
                     "r.gram, r.mesh, r.extraction_time, r.days_passed " +
                     "FROM recipe r " +
                     "JOIN beans b ON r.bean_id = b.id " +
                     "WHERE b.name = ? " +
                     "AND r.date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) " +
                     "ORDER BY r.date ASC")) {
                
                stmt.setString(1, beanName);
                ResultSet rs = stmt.executeQuery();
                
                while (rs.next()) {
                    Map<String, Object> record = new HashMap<>();
                    record.put("date", rs.getDate("date").toString());
                    record.put("weather", rs.getString("weather"));
                    record.put("temperature", rs.getFloat("temperature"));
                    record.put("humidity", rs.getInt("humidity"));
                    record.put("gram", rs.getFloat("gram"));
                    record.put("mesh", rs.getFloat("mesh"));
                    record.put("extraction_time", rs.getFloat("extraction_time"));
                    record.put("days_passed", rs.getFloat("days_passed"));
                    history.add(record);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return history;
    }
    
    private String getBeanOriginFromDatabase(String beanName) {
        try {
            try (Connection conn = DriverManager.getConnection(dbUrl, dbUsername, dbPassword);
                 PreparedStatement stmt = conn.prepareStatement(
                     "SELECT from_location FROM beans WHERE name = ?")) {
                
                stmt.setString(1, beanName);
                ResultSet rs = stmt.executeQuery();
                
                if (rs.next()) {
                    return rs.getString("from_location");
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "その他"; // デフォルト値
    }
}
