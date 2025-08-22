package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/beans")
@CrossOrigin(origins = "*")
public class BeanController {
    
    @Autowired
    private BeanRepository beanRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    // Get all beans for current user
    @GetMapping
    public ResponseEntity<List<Bean>> getAllBeans() {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        List<Bean> beans = beanRepository.findByUserId(currentUser.get().getId());
        return ResponseEntity.ok(beans);
    }
    
    // Get beans by user ID (for admin purposes)
    @GetMapping("/user/{userId}")
    public ResponseEntity<List<Bean>> getBeansByUserId(@PathVariable Integer userId) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        // Only allow if requesting own data
        if (!currentUser.get().getId().equals(userId)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        
        List<Bean> beans = beanRepository.findByUserId(userId);
        return ResponseEntity.ok(beans);
    }
    
    // Get bean by ID (only if owned by current user)
    @GetMapping("/{id}")
    public ResponseEntity<Bean> getBeanById(@PathVariable Integer id) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        Optional<Bean> bean = beanRepository.findById(id);
        if (bean.isPresent() && bean.get().getUser().getId().equals(currentUser.get().getId())) {
            return ResponseEntity.ok(bean.get());
        }
        return ResponseEntity.notFound().build();
    }
    
    // Create new bean for current user
    @PostMapping
    public ResponseEntity<Bean> createBean(@RequestBody Bean bean) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        // バリデーション
        if (bean.getName() == null || bean.getName().trim().isEmpty()) {
            return ResponseEntity.badRequest().build();
        }
        if (bean.getName().length() > 50) {
            return ResponseEntity.badRequest().build();
        }
        if (bean.getFromLocation() == null || bean.getFromLocation().trim().isEmpty()) {
            return ResponseEntity.badRequest().build();
        }
        if (bean.getFromLocation().length() > 50) {
            return ResponseEntity.badRequest().build();
        }
        
        // Set the current user as the owner
        bean.setUser(currentUser.get());
        
        // Check if bean name already exists for this user
        if (beanRepository.existsByNameAndUser(bean.getName(), currentUser.get())) {
            return ResponseEntity.badRequest().build();
        }
        
        Bean savedBean = beanRepository.save(bean);
        return ResponseEntity.ok(savedBean);
    }
    
    // Update bean (only if owned by current user)
    @PutMapping("/{id}")
    public ResponseEntity<Bean> updateBean(@PathVariable Integer id, @RequestBody Bean beanDetails) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        Optional<Bean> bean = beanRepository.findById(id);
        if (bean.isPresent() && bean.get().getUser().getId().equals(currentUser.get().getId())) {
            Bean existingBean = bean.get();
            
            // バリデーション
            if (beanDetails.getName() == null || beanDetails.getName().trim().isEmpty()) {
                return ResponseEntity.badRequest().build();
            }
            if (beanDetails.getName().length() > 50) {
                return ResponseEntity.badRequest().build();
            }
            if (beanDetails.getFromLocation() == null || beanDetails.getFromLocation().trim().isEmpty()) {
                return ResponseEntity.badRequest().build();
            }
            if (beanDetails.getFromLocation().length() > 50) {
                return ResponseEntity.badRequest().build();
            }
            
            existingBean.setName(beanDetails.getName());
            existingBean.setFromLocation(beanDetails.getFromLocation());
            Bean updatedBean = beanRepository.save(existingBean);
            return ResponseEntity.ok(updatedBean);
        }
        return ResponseEntity.notFound().build();
    }
    
    // Delete bean (only if owned by current user)
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteBean(@PathVariable Integer id) {
        Optional<User> currentUser = SecurityUtils.getCurrentUser(userRepository);
        if (!currentUser.isPresent()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        Optional<Bean> bean = beanRepository.findById(id);
        if (bean.isPresent() && bean.get().getUser().getId().equals(currentUser.get().getId())) {
            beanRepository.deleteById(id);
            return ResponseEntity.ok().build();
        }
        return ResponseEntity.notFound().build();
    }
}
