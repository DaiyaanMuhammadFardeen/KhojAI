package com.khojgroup.KhojAI.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.khojgroup.KhojAI.dto.AiRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.core.io.buffer.DefaultDataBufferFactory;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
public class AiService {

    private final WebClient aiWebClient;  // Injected from config

    // Streaming AI response functionality - new unified method
    public Flux<DataBuffer> streamAiResponse(String userPrompt) {
        AiRequest request = new AiRequest(userPrompt);

        return aiWebClient.post()
            .uri("/stream")
            .contentType(MediaType.APPLICATION_JSON)
            .accept(MediaType.TEXT_EVENT_STREAM)
            .bodyValue(request)
            .retrieve()
            .bodyToFlux(DataBuffer.class)
            .onErrorResume(throwable -> {
                System.err.println("Streaming error resume: " + throwable.getMessage());
                String json = "{\"type\":\"error\",\"message\":\"" + 
                              throwable.getMessage().replace("\"", "\\\"") + "\"}";
                byte[] bytes = ("data: " + json + "\n\n").getBytes(StandardCharsets.UTF_8);
                return Flux.just(DefaultDataBufferFactory.sharedInstance.wrap(bytes));
            });
    }
    
    // Synchronous method to generate response from stream - for use in MessageService
    public String generateResponseFromStream(String userPrompt) {
        StringBuilder responseBuilder = new StringBuilder();
        
        CompletableFuture<Void> future = streamAiResponse(userPrompt)
            .map(dataBuffer -> {
                byte[] bytes = new byte[dataBuffer.readableByteCount()];
                dataBuffer.read(bytes);
                // Note: In a production environment, you should properly release the DataBuffer
                return new String(bytes, StandardCharsets.UTF_8);
            })
            .filter(chunk -> chunk.startsWith("data: "))
            .map(chunk -> chunk.substring(6)) // Remove "data: " prefix
            .doOnNext(data -> {
                try {
                    ObjectMapper mapper = new ObjectMapper();
                    JsonNode jsonNode = mapper.readTree(data);
                    if ("response_token".equals(jsonNode.get("type").asText())) {
                        responseBuilder.append(jsonNode.get("data").asText());
                    }
                } catch (Exception e) {
                    // Ignore parsing errors
                }
            })
            .then().toFuture();
            
        try {
            // Wait for completion with a reasonable timeout
            future.get(30, TimeUnit.SECONDS);
        } catch (Exception e) {
            System.err.println("Error while waiting for AI response: " + e.getMessage());
        }
        
        return responseBuilder.toString();
    }
}