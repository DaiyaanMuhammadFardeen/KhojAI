package com.khojgroup.KhojAI.controller;

import com.khojgroup.KhojAI.dto.AiRequest;
import com.khojgroup.KhojAI.service.AiService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.MediaType;
import reactor.core.publisher.Flux;
import java.util.concurrent.atomic.AtomicInteger;

@RestController
@RequestMapping("/api/v1/ai")
@CrossOrigin(origins = "http://localhost:3000") // Allow frontend to access
@RequiredArgsConstructor
public class AIController {

    private final AiService aiService;
    private final AtomicInteger requestCounter = new AtomicInteger(0);

    /**
     * Stream AI response from Python backend through Java service
     * This is the new unified endpoint that replaces all previous endpoints
     */
    @PostMapping(value = "/stream-ai-response", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public ResponseEntity<Flux<DataBuffer>> streamAiResponse(@RequestBody AiRequest request) {
        Flux<DataBuffer> stream = aiService.streamAiResponse(request.prompt());

        return ResponseEntity.ok()
            .header("Cache-Control", "no-cache")
            .header("Connection", "keep-alive")
            .header("X-Accel-Buffering", "no")
            .contentType(MediaType.TEXT_EVENT_STREAM)
            .body(stream);
    }
}