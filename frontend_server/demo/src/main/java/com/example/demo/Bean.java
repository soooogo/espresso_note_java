package com.example.demo;

import jakarta.persistence.*;
import java.util.List;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonIgnore;

@Entity
@Table(name = "beans")
public class Bean {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    
    @ManyToOne
    @JoinColumn(name = "user_id", nullable = false)
    @JsonBackReference(value = "user-beans")
    private User user;
    
    @Column(nullable = false, length = 50)
    private String name;
    
    @Column(name = "from_location", nullable = false, length = 50)
    private String fromLocation;
    
    @OneToMany(mappedBy = "bean", cascade = CascadeType.ALL)
    @JsonIgnore
    private List<Recipe> recipes;
    
    // Default constructor
    public Bean() {}
    
    // Constructor with fields
    public Bean(User user, String name, String fromLocation) {
        this.user = user;
        this.name = name;
        this.fromLocation = fromLocation;
    }
    
    // Getters and Setters
    public Integer getId() {
        return id;
    }
    
    public void setId(Integer id) {
        this.id = id;
    }
    
    public User getUser() {
        return user;
    }
    
    public void setUser(User user) {
        this.user = user;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getFromLocation() {
        return fromLocation;
    }
    
    public void setFromLocation(String fromLocation) {
        this.fromLocation = fromLocation;
    }
    
    public List<Recipe> getRecipes() {
        return recipes;
    }
    
    public void setRecipes(List<Recipe> recipes) {
        this.recipes = recipes;
    }
    
    @Override
    public String toString() {
        return "Bean{" +
                "id=" + id +
                ", user=" + user +
                ", name='" + name + '\'' +
                ", fromLocation='" + fromLocation + '\'' +
                '}';
    }
}
