package com.example.demo;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface RecipeRepository extends JpaRepository<Recipe, Integer> {
    
    // Find recipes by bean
    List<Recipe> findByBean(Bean bean);
    
    // Find recipes by bean ID
    List<Recipe> findByBeanId(Integer beanId);
    
    // Find recipes by date range
    List<Recipe> findByDateBetween(LocalDate startDate, LocalDate endDate);
    
    // Find recipes by weather
    List<Recipe> findByWeather(String weather);
    
    // Find recipes by temperature range
    List<Recipe> findByTemperatureBetween(Float minTemp, Float maxTemp);
    
    // Find recipes by humidity range
    List<Recipe> findByHumidityBetween(Integer minHumidity, Integer maxHumidity);
    
    // Custom query for recipe prediction based on weather and temperature
    @Query("SELECT r FROM Recipe r WHERE r.weather = :weather AND r.temperature BETWEEN :minTemp AND :maxTemp ORDER BY r.date DESC")
    List<Recipe> findRecipesForPrediction(@Param("weather") String weather, 
                                         @Param("minTemp") Float minTemp, 
                                         @Param("maxTemp") Float maxTemp);
    
    // Find recipes by user (through bean)
    @Query("SELECT r FROM Recipe r JOIN r.bean b WHERE b.user.id = :userId ORDER BY r.date DESC")
    List<Recipe> findByUserId(@Param("userId") Integer userId);
    
    // Find recipes by user and date range
    @Query("SELECT r FROM Recipe r JOIN r.bean b WHERE b.user.id = :userId AND r.date BETWEEN :startDate AND :endDate ORDER BY r.date DESC")
    List<Recipe> findByUserIdAndDateBetween(@Param("userId") Integer userId, 
                                           @Param("startDate") LocalDate startDate, 
                                           @Param("endDate") LocalDate endDate);
    
    // Find recipes by user and weather
    @Query("SELECT r FROM Recipe r JOIN r.bean b WHERE b.user.id = :userId AND r.weather = :weather ORDER BY r.date DESC")
    List<Recipe> findByUserIdAndWeather(@Param("userId") Integer userId, 
                                       @Param("weather") String weather);
}
