package com.khojgroup.KhojAI.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.server.WebFilter;

@Configuration
public class NoBufferingWebFilter {

    @Bean
    public WebFilter noBufferingFilter() {
        return (exchange, chain) -> {
            var response = exchange.getResponse();
            response.getHeaders().add("Cache-Control", "no-cache, no-store, must-revalidate");
            response.getHeaders().add("Pragma", "no-cache");
            response.getHeaders().add("Expires", "0");
            response.getHeaders().add("X-Accel-Buffering", "no");
            return chain.filter(exchange);
        };
    }
}