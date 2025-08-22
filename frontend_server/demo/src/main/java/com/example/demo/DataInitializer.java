package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import org.springframework.security.crypto.password.PasswordEncoder;

@Component
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
        // Clear existing data
        recipeRepository.deleteAll();
        beanRepository.deleteAll();
        userRepository.deleteAll();
        
        // Create multiple users with encoded passwords and roles
        User user1 = userRepository.save(new User("コーヒー愛好家", "coffee.lover@example.com", passwordEncoder.encode("password"), "ROLE_USER"));
        User user2 = userRepository.save(new User("エスプレッソ職人", "espresso.pro@example.com", passwordEncoder.encode("password"), "ROLE_USER"));
        User user3 = userRepository.save(new User("ホームロースター", "home.roaster@example.com", passwordEncoder.encode("password"), "ROLE_ADMIN"));

        // Beans for user1
        Bean u1b1 = beanRepository.save(new Bean(user1, "エチオピア イルガチェフェ", "エチオピア"));
        Bean u1b2 = beanRepository.save(new Bean(user1, "グアテマラ アンティグア", "グアテマラ"));
        Bean u1b3 = beanRepository.save(new Bean(user2, "ブラジル サントス", "ブラジル"));

        // Recipes for user1 beans
        recipeRepository.save(new Recipe(u1b1, LocalDate.now().minusDays(1), "晴れ", 25.0f, 60, 18.0f, 2.5f, 30.0f));
        recipeRepository.save(new Recipe(u1b1, LocalDate.now().minusDays(2), "曇り", 22.5f, 65, 18.5f, 2.3f, 32.0f));
        recipeRepository.save(new Recipe(u1b2, LocalDate.now().minusDays(3), "雨", 20.0f, 80, 19.0f, 2.7f, 35.0f));
        recipeRepository.save(new Recipe(u1b2, LocalDate.now().minusDays(4), "晴れ", 28.0f, 55, 17.5f, 2.2f, 28.0f));
        recipeRepository.save(new Recipe(u1b3, LocalDate.now().minusDays(5), "曇り", 23.0f, 68, 18.0f, 2.4f, 31.0f));

        // Beans for user2
        Bean u2b1 = beanRepository.save(new Bean(user2, "コロンビア スプレモ", "コロンビア"));
        Bean u2b2 = beanRepository.save(new Bean(user2, "ケニア AA", "ケニア"));

        // Recipes for user2 beans
        recipeRepository.save(new Recipe(u2b1, LocalDate.now().minusDays(1), "晴れ", 24.0f, 58, 18.2f, 2.4f, 29.5f));
        recipeRepository.save(new Recipe(u2b1, LocalDate.now().minusDays(6), "雨", 19.0f, 85, 19.3f, 2.8f, 36.0f));
        recipeRepository.save(new Recipe(u2b2, LocalDate.now().minusDays(2), "曇り", 21.5f, 70, 18.8f, 2.6f, 33.0f));

        // Beans for user3
        Bean u3b1 = beanRepository.save(new Bean(user3, "インドネシア マンデリン", "インドネシア"));
        Bean u3b2 = beanRepository.save(new Bean(user3, "パナマ ゲイシャ", "パナマ"));
        Bean u3b3 = beanRepository.save(new Bean(user3, "タンザニア キリマンジャロ", "タンザニア"));

        // Recipes for user3 beans
        recipeRepository.save(new Recipe(u3b1, LocalDate.now().minusDays(7), "雨", 18.0f, 88, 19.5f, 2.9f, 38.0f));
        recipeRepository.save(new Recipe(u3b1, LocalDate.now().minusDays(8), "曇り", 20.5f, 72, 18.7f, 2.5f, 32.5f));
        recipeRepository.save(new Recipe(u3b2, LocalDate.now().minusDays(1), "晴れ", 26.0f, 52, 17.8f, 2.1f, 27.0f));
        recipeRepository.save(new Recipe(u3b3, LocalDate.now().minusDays(3), "雪", 2.0f, 40, 19.0f, 2.6f, 34.0f));

        System.out.println("エスプレッソアプリのサンプルデータが挿入されました！");
        System.out.println("ユーザー数: " + userRepository.count());
        System.out.println("コーヒー豆数: " + beanRepository.count());
        System.out.println("レシピ数: " + recipeRepository.count());
    }
}
