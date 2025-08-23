package com.example.demo.service;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.util.Optional;

import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;

@Component
public class SecurityUtils {
    
    /**
     * 現在ログインしているユーザーのメールアドレスを取得
     */
    public static Optional<String> getCurrentUserEmail() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.isAuthenticated() && 
            !"anonymousUser".equals(authentication.getName())) {
            return Optional.of(authentication.getName());
        }
        return Optional.empty();
    }
    
    /**
     * 現在ログインしているユーザーを取得
     */
    public static Optional<User> getCurrentUser(UserRepository userRepository) {
        return getCurrentUserEmail()
                .flatMap(userRepository::findByEmail);
    }
}
