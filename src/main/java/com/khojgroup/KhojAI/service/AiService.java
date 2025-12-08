package com.khojgroup.KhojAI.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.khojgroup.KhojAI.dto.AiRequest;
import com.khojgroup.KhojAI.dto.AiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.core.publisher.Flux;

@Service
@RequiredArgsConstructor
public class AiService {

    private final WebClient aiWebClient;  // Injected from config

    public String analyzeInternal(String userPrompt) {
        AiRequest request = new AiRequest(userPrompt);

        try {
            return aiWebClient.post()
                    .uri("/analyze")
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(request)
                    .retrieve()
                    .onStatus(HttpStatusCode::is4xxClientError, resp -> {
                        return resp.bodyToMono(String.class)
                                .flatMap(body -> {
                                    try {
                                        ObjectMapper mapper = new ObjectMapper();
                                        JsonNode json = mapper.readTree(body);
                                        return Mono.error(new RuntimeException("AI Client Error: " + json.get("detail").asText()));
                                    } catch (Exception e) {
                                        return Mono.error(new RuntimeException("AI Client Error: " + body));
                                    }
                                });
                    })
                    .onStatus(HttpStatusCode::is5xxServerError, resp -> {
                        return resp.bodyToMono(String.class)
                                .flatMap(body -> {
                                    try {
                                        ObjectMapper mapper = new ObjectMapper();
                                        JsonNode json = mapper.readTree(body);
                                        return Mono.error(new RuntimeException("AI Server Error: " + json.get("detail").asText()));
                                    } catch (Exception e) {
                                        return Mono.error(new RuntimeException("AI Server Error: " + body));
                                    }
                                });
                    })
                    .bodyToMono(AiResponse.class)
                    .map(AiResponse::message)
                    .block(); // sync for now
        } catch (WebClientResponseException e) {
            throw new RuntimeException("AI Service Unavailable: " + e.getMessage());
        } catch (Exception e) {
            throw new RuntimeException("Unexpected error when calling AI service: " + e.getMessage());
        }
    }

    // Generate response without exposing internal analysis
    public String generateResponse(String userPrompt) {
        AiRequest request = new AiRequest(userPrompt);

        try {
            return aiWebClient.post()
                    .uri("/generate-response")
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(request)
                    .retrieve()
                    .onStatus(HttpStatusCode::is4xxClientError, resp -> {
                        return resp.bodyToMono(String.class)
                                .flatMap(body -> {
                                    try {
                                        ObjectMapper mapper = new ObjectMapper();
                                        JsonNode json = mapper.readTree(body);
                                        return Mono.error(new RuntimeException("AI Client Error: " + json.get("detail").asText()));
                                    } catch (Exception e) {
                                        return Mono.error(new RuntimeException("AI Client Error: " + body));
                                    }
                                });
                    })
                    .onStatus(HttpStatusCode::is5xxServerError, resp -> {
                        return resp.bodyToMono(String.class)
                                .flatMap(body -> {
                                    try {
                                        ObjectMapper mapper = new ObjectMapper();
                                        JsonNode json = mapper.readTree(body);
                                        return Mono.error(new RuntimeException("AI Server Error: " + json.get("detail").asText()));
                                    } catch (Exception e) {
                                        return Mono.error(new RuntimeException("AI Server Error: " + body));
                                    }
                                });
                    })
                    .bodyToMono(AiResponse.class)
                    .map(AiResponse::message)
                    .block(); // sync for now
        } catch (WebClientResponseException e) {
            throw new RuntimeException("AI Service Unavailable: " + e.getMessage());
        } catch (Exception e) {
            throw new RuntimeException("Unexpected error when calling AI service: " + e.getMessage());
        }
    }

    // Streaming search functionality
    public Flux<String> streamSearch(String userPrompt) {
        AiRequest request = new AiRequest(userPrompt);
        
        System.out.println("=== AiService.streamSearch START ===");
        System.out.println("Prompt: " + userPrompt);
        
        return aiWebClient.post()
            .uri("/stream-search")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(request)
            .retrieve()
            .bodyToFlux(String.class)
            .doOnNext(chunk -> {
                System.out.println("RAW CHUNK FROM PYTHON: [" + chunk + "]");
                System.out.println("Chunk length: " + chunk.length());
                System.out.println("Starts with 'data:': " + chunk.startsWith("data:"));
            })
            .doOnError(throwable -> {
                System.err.println("Streaming error: " + throwable.getMessage());
                throwable.printStackTrace();
            })
            .doOnComplete(() -> {
                System.out.println("=== Python stream COMPLETE ===");
            })
            .onErrorResume(throwable -> {
                System.err.println("Streaming error resume: " + throwable.getMessage());
                return Flux.just("data: {\"type\": \"error\", \"message\": \"" + throwable.getMessage() + "\"}\n\n");
            });
    }
}