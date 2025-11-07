package com.khojgroup.KhojAI.controller;

import com.khojgroup.KhojAI.dto.AiRequest;
import com.khojgroup.KhojAI.dto.AiResponse;
import com.khojgroup.KhojAI.service.AiService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/ai")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:3000") // Allow frontend to access
public class AIController {

    private final AiService aiService;

    @PostMapping("/analyze")
    public ResponseEntity<AiResponse> analyzePrompt(@RequestBody AiRequest request) {
        try {
            String result = aiService.analyze(request.prompt());
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
}