package com.example.demo.entity;

import jakarta.persistence.*;
import java.time.LocalDate;

@Entity
@Table(name = "recipe")
public class Recipe {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    
    @ManyToOne
    @JoinColumn(name = "bean_id", nullable = false)
    private Bean bean;
    
    @Column(nullable = false)
    private LocalDate date;
    
    @Column(nullable = false, length = 50)
    private String weather;
    
    private Float temperature;
    
    private Integer humidity;
    
    @Column(nullable = false)
    private Float gram;
    
    @Column(nullable = false)
    private Float mesh;
    
    @Column(nullable = false)
    private Float extraction_time;
    
    private Float days_passed;
    
    // Default constructor
    public Recipe() {}
    
    // Constructor with fields
    public Recipe(Bean bean, LocalDate date, String weather, Float temperature, 
                  Integer humidity, Float gram, Float mesh, Float extraction_time) {
        this.bean = bean;
        this.date = date;
        this.weather = weather;
        this.temperature = temperature;
        this.humidity = humidity;
        this.gram = gram;
        this.mesh = mesh;
        this.extraction_time = extraction_time;
        this.days_passed = 15.0f; // デフォルト値
    }
    
    // Constructor with days_passed
    public Recipe(Bean bean, LocalDate date, String weather, Float temperature, 
                  Integer humidity, Float gram, Float mesh, Float extraction_time, Float days_passed) {
        this.bean = bean;
        this.date = date;
        this.weather = weather;
        this.temperature = temperature;
        this.humidity = humidity;
        this.gram = gram;
        this.mesh = mesh;
        this.extraction_time = extraction_time;
        this.days_passed = days_passed;
    }
    
    // Getters and Setters
    public Integer getId() {
        return id;
    }
    
    public void setId(Integer id) {
        this.id = id;
    }
    
    public Bean getBean() {
        return bean;
    }
    
    public void setBean(Bean bean) {
        this.bean = bean;
    }
    
    public LocalDate getDate() {
        return date;
    }
    
    public void setDate(LocalDate date) {
        this.date = date;
    }
    
    public String getWeather() {
        return weather;
    }
    
    public void setWeather(String weather) {
        this.weather = weather;
    }
    
    public Float getTemperature() {
        return temperature;
    }
    
    public void setTemperature(Float temperature) {
        this.temperature = temperature;
    }
    
    public Integer getHumidity() {
        return humidity;
    }
    
    public void setHumidity(Integer humidity) {
        this.humidity = humidity;
    }
    
    public Float getGram() {
        return gram;
    }
    
    public void setGram(Float gram) {
        this.gram = gram;
    }
    
    public Float getMesh() {
        return mesh;
    }
    
    public void setMesh(Float mesh) {
        this.mesh = mesh;
    }
    
    public Float getExtraction_time() {
        return extraction_time;
    }
    
    public void setExtraction_time(Float extraction_time) {
        this.extraction_time = extraction_time;
    }
    
    public Float getDays_passed() {
        return days_passed;
    }
    
    public void setDays_passed(Float days_passed) {
        this.days_passed = days_passed;
    }
    
    @Override
    public String toString() {
        return "Recipe{" +
                "id=" + id +
                ", bean=" + bean +
                ", date=" + date +
                ", weather='" + weather + '\'' +
                ", temperature=" + temperature +
                ", humidity=" + humidity +
                ", gram=" + gram +
                ", mesh=" + mesh +
                ", extraction_time=" + extraction_time +
                ", days_passed=" + days_passed +
                '}';
    }
}
