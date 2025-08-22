package com.example.demo;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class WebController {
    
    @GetMapping("/")
    public String index() {
        return "index";
    }
    
    @GetMapping("/login")
    public String login() {
        return "login";
    }
    
    @GetMapping("/beans")
    public String beans() {
        return "beans";
    }
    
    @GetMapping("/recipes")
    public String recipes() {
        return "recipes";
    }
    
    @GetMapping("/predict")
    public String predict() {
        return "predict";
    }
}
