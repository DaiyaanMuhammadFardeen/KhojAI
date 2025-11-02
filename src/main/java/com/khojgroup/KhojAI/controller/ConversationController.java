package com.khojgroup.KhojAI.controller;

import com.khojgroup.KhojAI.dto.ConversationDTO;
import com.khojgroup.KhojAI.dto.MessageDTO;
import com.khojgroup.KhojAI.entity.Conversation;
import com.khojgroup.KhojAI.service.ConversationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/conversations")
@RequiredArgsConstructor
public class ConversationController {

    private final ConversationService convService;

    @PostMapping
    public ResponseEntity<ConversationDTO> create(@RequestBody CreateConvRequest req) {
        Conversation conv = convService.create(req.userId(), req.title());
        return ResponseEntity.ok(toDTO(conv));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ConversationDTO> get(@PathVariable UUID id) {
        return ResponseEntity.ok(toDTO(convService.findById(id)));
    }

    @PutMapping("/{id}/title")
    public ResponseEntity<ConversationDTO> updateTitle(@PathVariable UUID id, @RequestBody Map<String, String> body) {
        Conversation conv = convService.updateTitle(id, body.get("title"));
        return ResponseEntity.ok(toDTO(conv));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        convService.deleteById(id);
        return ResponseEntity.noContent().build();
    }

    private ConversationDTO toDTO(Conversation conv) {
        List<MessageDTO> msgs = conv.getMessages().stream()
                .map(m -> new MessageDTO(m.getId(), m.getRole(), m.getContent(), m.getSentAt()))
                .toList();
        return new ConversationDTO(conv.getId(), conv.getTitle(), conv.getCreatedAt(), msgs);
    }
}

record CreateConvRequest(UUID userId, String title) {}