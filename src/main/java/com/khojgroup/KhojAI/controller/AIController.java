package com.khojgroup.KhojAI.controller;

import com.khojgroup.KhojAI.dto.AiRequest;
import com.khojgroup.KhojAI.dto.AiResponse;
import com.khojgroup.KhojAI.service.AiService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.MediaType;
import reactor.core.publisher.Flux;
import org.springframework.http.HttpStatus;
import java.util.concurrent.atomic.AtomicInteger;

@RestController
@RequestMapping("/api/v1/ai")
@CrossOrigin(origins = "http://localhost:3000") // Allow frontend to access
@RequiredArgsConstructor
public class AIController {

    private final AiService aiService;
    private final AtomicInteger requestCounter = new AtomicInteger(0);

    // Internal endpoint - removed @CrossOrigin to make it internal only
    @PostMapping("/analyze")
    public ResponseEntity<AiResponse> analyzePrompt(@RequestBody AiRequest request) {
        try {
            String result = aiService.analyzeInternal(request.prompt());
            return ResponseEntity.ok(new AiResponse(result));
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(new AiResponse("Error analyzing prompt: " + e.getMessage()));
        }
    }

    @PostMapping("/generate-response")
    public ResponseEntity<AiResponse> generateResponse(@RequestBody AiRequest request) {
        try {
            String result = aiService.generateResponse(request.prompt());
            return ResponseEntity.ok(new AiResponse(result));
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(new AiResponse("Error generating response: " + e.getMessage()));
        }
    }

    /**
     * CRITICAL FIX: Remove ServerSentEvent wrapper since Python AI already sends SSE format
     * Just pass through the raw SSE strings from the Python service
     */
    @PostMapping(value = "/stream-search", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> streamSearch(@RequestBody AiRequest request) {
        int reqNum = requestCounter.incrementAndGet();
        System.out.println("=== REQUEST #" + reqNum + " ===");
        System.out.println("=== CONTROLLER RECEIVED REQUEST ===");
        System.out.println("Prompt: " + request.prompt());
        System.out.println("Timestamp: " + System.currentTimeMillis());
        
        return aiService.streamSearch(request.prompt())
            .doOnNext(data -> {
                System.out.println("CONTROLLER EMITTING: [" + data + "]");
            })
            .doOnError(error -> {
                System.err.println("Controller stream error: " + error.getMessage());
                error.printStackTrace();
            })
            .doOnComplete(() -> {
                System.out.println("=== CONTROLLER COMPLETE ===");
            })
            .onErrorResume(throwable -> {
                System.err.println("Controller error resume: " + throwable.getMessage());
                // Send proper SSE error format
                String errorMessage = throwable.getMessage().replace("\"", "\\\"");
                return Flux.just("data: {\"type\":\"error\",\"message\":\"" + errorMessage + "\"}\n\n");
            });
    }
}