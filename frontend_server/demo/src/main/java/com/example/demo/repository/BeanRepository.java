package com.example.demo.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

import com.example.demo.entity.Bean;
import com.example.demo.entity.User;
import java.util.Optional;

@Repository
public interface BeanRepository extends JpaRepository<Bean, Integer> {
    
    // Find beans by user
    List<Bean> findByUser(User user);
    
    // Find beans by user ID
    List<Bean> findByUserId(Integer userId);
    
    // Find bean by name and user
    Optional<Bean> findByNameAndUser(String name, User user);
    
    // Check if bean exists by name and user
    boolean existsByNameAndUser(String name, User user);
}
