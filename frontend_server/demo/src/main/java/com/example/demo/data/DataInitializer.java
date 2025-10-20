package com.example.demo.data;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import org.springframework.context.annotation.Profile;

import java.time.LocalDate;
import org.springframework.security.crypto.password.PasswordEncoder;

import com.example.demo.entity.User;
import com.example.demo.entity.Bean;
import com.example.demo.entity.Recipe;
import com.example.demo.repository.UserRepository;
import com.example.demo.repository.BeanRepository;
import com.example.demo.repository.RecipeRepository;

@Component
@Profile("seed")
public class DataInitializer implements CommandLineRunner {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private BeanRepository beanRepository;
    
    @Autowired
    private RecipeRepository recipeRepository;
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    @Override
    public void run(String... args) throws Exception {
        System.out.println("=== DataInitializer デバッグ開始 ===");
        
        // Check if data already exists
        long userCount = userRepository.count();
        long beanCount = beanRepository.count();
        long recipeCount = recipeRepository.count();
        
        System.out.println("現在のデータベース状態:");
        System.out.println("  ユーザー数: " + userCount);
        System.out.println("  コーヒー豆数: " + beanCount);
        System.out.println("  レシピ数: " + recipeCount);
        
        if (userCount > 0 || beanCount > 0 || recipeCount > 0) {
            System.out.println("✅ 既存のデータが検出されました。データの初期化をスキップします。");
            System.out.println("=== DataInitializer デバッグ終了（スキップ） ===");
            return;
        }
        
        System.out.println("データベースが空のため、サンプルデータを初期化します...");
        
        // Create multiple users with encoded passwords and roles
        User user1 = userRepository.save(new User("コーヒー愛好家", "coffee.lover@example.com", passwordEncoder.encode("password"), "ROLE_USER"));
        User user2 = userRepository.save(new User("エスプレッソ職人", "espresso.pro@example.com", passwordEncoder.encode("password"), "ROLE_USER"));
        User user3 = userRepository.save(new User("ホームロースター", "home.roaster@example.com", passwordEncoder.encode("password"), "ROLE_ADMIN"));

        // Beans for user1
        Bean u1b1 = beanRepository.save(new Bean(user1, "エチオピア イルガチェフェ", "エチオピア"));
        Bean u1b2 = beanRepository.save(new Bean(user1, "グアテマラ アンティグア", "グアテマラ"));
        Bean u1b3 = beanRepository.save(new Bean(user2, "ブラジル サントス", "ブラジル"));

        
        // グアテマラ アンティグアのレシピ（20件）
        for (int i = 1; i <= 20; i++) {
            LocalDate date = LocalDate.now().minusDays(i + 20); // 重複を避けるため20日ずらす
            String weather = i % 4 == 0 ? "晴れ" : i % 4 == 1 ? "曇り" : i % 4 == 2 ? "雨" : "雪";
            float temperature = 16.0f + (i % 14); // 16-30度の範囲
            int humidity = 45 + (i % 35); // 45-80%の範囲
            float mesh = 16.5f + (i % 4) * 0.5f; // 16.5-18.5の範囲
            float gram = 2.1f + (i % 5) * 0.1f; // 2.1-2.5の範囲
            float extractionTime = 26.0f + (i % 9); // 26-35秒の範囲
            float daysPassed = 12.0f + (i % 8); // 12-20日の範囲
            
            recipeRepository.save(new Recipe(u1b2, date, weather, temperature, humidity, mesh, gram, extractionTime, daysPassed));
        }
        
        // ブラジル サントスのレシピ（20件）
        for (int i = 1; i <= 20; i++) {
            LocalDate date = LocalDate.now().minusDays(i + 40); // 重複を避けるため40日ずらす
            String weather = i % 4 == 0 ? "晴れ" : i % 4 == 1 ? "曇り" : i % 4 == 2 ? "雨" : "雪";
            float temperature = 17.0f + (i % 13); // 17-30度の範囲
            int humidity = 48 + (i % 32); // 48-80%の範囲
            float mesh = 17.5f + (i % 3) * 0.5f; // 17.5-19の範囲
            float gram = 2.2f + (i % 4) * 0.1f; // 2.2-2.5の範囲
            float extractionTime = 27.0f + (i % 8); // 27-35秒の範囲
            float daysPassed = 15.0f + (i % 5); // 15-20日の範囲
            
            recipeRepository.save(new Recipe(u1b3, date, weather, temperature, humidity, mesh, gram, extractionTime, daysPassed));
        }

        // Beans for user2
        Bean u2b1 = beanRepository.save(new Bean(user2, "コロンビア スプレモ", "コロンビア"));
        Bean u2b2 = beanRepository.save(new Bean(user2, "ケニア AA", "ケニア"));

        // Recipes for user2 beans
        recipeRepository.save(new Recipe(u2b1, LocalDate.now().minusDays(1), "晴れ", 24.0f, 58, 18.2f, 2.4f, 29.5f, 15.0f));
        recipeRepository.save(new Recipe(u2b1, LocalDate.now().minusDays(6), "雨", 19.0f, 85, 19.3f, 2.8f, 36.0f, 12.0f));
        recipeRepository.save(new Recipe(u2b2, LocalDate.now().minusDays(2), "曇り", 21.5f, 70, 18.8f, 2.6f, 33.0f, 18.0f));

        // Beans for user3
        Bean u3b1 = beanRepository.save(new Bean(user3, "インドネシア マンデリン", "インドネシア"));
        Bean u3b2 = beanRepository.save(new Bean(user3, "パナマ ゲイシャ", "パナマ"));
        Bean u3b3 = beanRepository.save(new Bean(user3, "タンザニア キリマンジャロ", "タンザニア"));

        // Recipes for user3 beans
        recipeRepository.save(new Recipe(u3b1, LocalDate.now().minusDays(7), "雨", 18.0f, 88, 19.5f, 2.9f, 38.0f, 10.0f));
        recipeRepository.save(new Recipe(u3b1, LocalDate.now().minusDays(8), "曇り", 20.5f, 72, 18.7f, 2.5f, 32.5f, 16.0f));
        recipeRepository.save(new Recipe(u3b2, LocalDate.now().minusDays(1), "晴れ", 26.0f, 52, 17.8f, 2.1f, 27.0f, 14.0f));
        recipeRepository.save(new Recipe(u3b3, LocalDate.now().minusDays(3), "雪", 2.0f, 40, 19.0f, 2.6f, 34.0f, 20.0f));

        System.out.println("✅ エスプレッソアプリのサンプルデータが挿入されました！");
        System.out.println("最終データベース状態:");
        System.out.println("  ユーザー数: " + userRepository.count());
        System.out.println("  コーヒー豆数: " + beanRepository.count());
        System.out.println("  レシピ数: " + recipeRepository.count());
        System.out.println("=== DataInitializer デバッグ終了（初期化完了） ===");
    }
}
