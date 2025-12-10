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
        
        // Allow requests from all origins (for demo)
        config.setAllowedOriginPatterns(List.of("*"));
        
        // Allow credentials
        config.setAllowCredentials(true);
        
        // Allow all HTTP methods
        config.setAllowedMethods(List.of("*"));
        
        // Allow all headers
        config.setAllowedHeaders(List.of("*"));
        
        // Expose specific headers
        config.setExposedHeaders(List.of("Authorization", "Content-Type"));
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        
        return new CorsFilter(source);
    }
}