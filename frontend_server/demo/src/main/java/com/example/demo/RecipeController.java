package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/recipes")
@CrossOrigin(origins = "*")
public class RecipeController {
    
    @Autowired
    private RecipeRepository recipeRepository;
    
    @Autowired
    private BeanRepository beanRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    // Get all recipes for current user
    @GetMapping
    public ResponseEntity<List<Recipe>> getAllRecipes() {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        List<Recipe> recipes = recipeRepository.findByUserId(currentUser.get().getId());
        return ResponseEntity.ok(recipes);
    }
    
    // Get recipes by user ID (for admin purposes)
    @GetMapping("/user/{userId}")
    public ResponseEntity<List<Recipe>> getRecipesByUserId(@PathVariable Integer userId) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        // Only allow if requesting own data
        if (!currentUser.get().getId().equals(userId)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        
        List<Recipe> recipes = recipeRepository.findByUserId(userId);
        return ResponseEntity.ok(recipes);
    }
    
    // Get recipes by bean ID (only if bean belongs to current user)
    @GetMapping("/bean/{beanId}")
    public ResponseEntity<List<Recipe>> getRecipesByBeanId(@PathVariable Integer beanId) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        // Check if bean belongs to current user
        Optional<Bean> bean = beanRepository.findById(beanId);
        if (!bean.isPresent() || !bean.get().getUser().getId().equals(currentUser.get().getId())) {
            return ResponseEntity.notFound().build();
        }
        
        List<Recipe> recipes = recipeRepository.findByBeanId(beanId);
        return ResponseEntity.ok(recipes);
    }
    
    // Get recipe by ID (only if owned by current user)
    @GetMapping("/{id}")
    public ResponseEntity<Recipe> getRecipeById(@PathVariable Integer id) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        Optional<Recipe> recipe = recipeRepository.findById(id);
        if (recipe.isPresent() && recipe.get().getBean().getUser().getId().equals(currentUser.get().getId())) {
            return ResponseEntity.ok(recipe.get());
        }
        return ResponseEntity.notFound().build();
    }
    
    // Create new recipe for current user
    @PostMapping
    public ResponseEntity<Recipe> createRecipe(@RequestBody Recipe recipe) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        // Check if bean exists and belongs to current user
        Optional<Bean> bean = beanRepository.findById(recipe.getBean().getId());
        if (!bean.isPresent() || !bean.get().getUser().getId().equals(currentUser.get().getId())) {
            return ResponseEntity.badRequest().build();
        }
        
        recipe.setBean(bean.get());
        Recipe savedRecipe = recipeRepository.save(recipe);
        return ResponseEntity.ok(savedRecipe);
    }
    
    // Update recipe (only if owned by current user)
    @PutMapping("/{id}")
    public ResponseEntity<Recipe> updateRecipe(@PathVariable Integer id, @RequestBody Recipe recipeDetails) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        Optional<Recipe> recipe = recipeRepository.findById(id);
        if (recipe.isPresent() && recipe.get().getBean().getUser().getId().equals(currentUser.get().getId())) {
            Recipe existingRecipe = recipe.get();
            existingRecipe.setDate(recipeDetails.getDate());
            existingRecipe.setWeather(recipeDetails.getWeather());
            existingRecipe.setTemperature(recipeDetails.getTemperature());
            existingRecipe.setHumidity(recipeDetails.getHumidity());
            existingRecipe.setGram(recipeDetails.getGram());
            existingRecipe.setMesh(recipeDetails.getMesh());
            existingRecipe.setExtraction_time(recipeDetails.getExtraction_time());
            Recipe updatedRecipe = recipeRepository.save(existingRecipe);
            return ResponseEntity.ok(updatedRecipe);
        }
        return ResponseEntity.notFound().build();
    }
    
    // Delete recipe (only if owned by current user)
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteRecipe(@PathVariable Integer id) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        Optional<Recipe> recipe = recipeRepository.findById(id);
        if (recipe.isPresent() && recipe.get().getBean().getUser().getId().equals(currentUser.get().getId())) {
            recipeRepository.deleteById(id);
            return ResponseEntity.ok().build();
        }
        return ResponseEntity.notFound().build();
    }
    

    
    // Get recipes by date range (only for current user)
    @GetMapping("/date-range")
    public ResponseEntity<List<Recipe>> getRecipesByDateRange(
            @RequestParam String startDate,
            @RequestParam String endDate) {
        
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        LocalDate start = LocalDate.parse(startDate);
        LocalDate end = LocalDate.parse(endDate);
        
        List<Recipe> recipes = recipeRepository.findByUserIdAndDateBetween(
            currentUser.get().getId(), start, end);
        return ResponseEntity.ok(recipes);
    }
    
    // Get recipes by weather (only for current user)
    @GetMapping("/weather/{weather}")
    public ResponseEntity<List<Recipe>> getRecipesByWeather(@PathVariable String weather) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        List<Recipe> recipes = recipeRepository.findByUserIdAndWeather(
            currentUser.get().getId(), weather);
        return ResponseEntity.ok(recipes);
    }
}
