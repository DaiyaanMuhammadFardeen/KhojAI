package com.khojgroup.KhojAI.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

import java.util.List;

@Configuration
public class CorsConfig {

    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        
        // Allow requests from specific origins including Cloudflare tunnels
        config.setAllowedOriginPatterns(List.of(
            "http://localhost:*",
            "https://localhost:*",
            "https://*trycloudflare.com",
            "http://*trycloudflare.com"
        ));
        
        // Allow credentials
        config.setAllowCredentials(true);
        
        // Allow specific HTTP methods
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        
        // Allow specific headers
        config.setAllowedHeaders(List.of("*"));
        
        // Expose specific headers
        config.setExposedHeaders(List.of("Authorization", "Content-Type"));
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        
        return new CorsFilter(source);
    }
}