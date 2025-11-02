package com.khojgroup.KhojAI.service;

import com.khojgroup.KhojAI.dto.AiRequest;
import com.khojgroup.KhojAI.dto.AiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
@RequiredArgsConstructor
public class AiService {

    private final WebClient aiWebClient;  // Injected from config

    public String analyze(String userPrompt) {
        AiRequest request = new AiRequest(userPrompt);

        return aiWebClient.post()
                .uri("/analyze")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(request)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError, resp ->
                        resp.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new RuntimeException("AI Client Error: " + body))))
                .onStatus(HttpStatusCode::is5xxServerError, resp ->
                        resp.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new RuntimeException("AI Server Error: " + body))))
                .bodyToMono(AiResponse.class)
                .map(AiResponse::message)
                .block(); // sync for now
    }
}