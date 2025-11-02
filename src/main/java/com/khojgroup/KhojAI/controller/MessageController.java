package com.khojgroup.KhojAI.controller;

import com.khojgroup.KhojAI.dto.ConversationDTO;
import com.khojgroup.KhojAI.dto.MessageDTO;
import com.khojgroup.KhojAI.entity.Conversation;
import com.khojgroup.KhojAI.entity.Message;
import com.khojgroup.KhojAI.service.MessageService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/messages")
@RequiredArgsConstructor
public class MessageController {

    private final MessageService msgService;

    @PostMapping
    public ResponseEntity<ConversationDTO> create(@RequestBody CreateMessageRequest req) {

        // 1. Let service save USER + AI messages and return full conversation
        Conversation conv = msgService.create(req.convId(), req.role(), req.content());

        // 2. Build ConversationDTO manually (no external toDTO!)
        List<MessageDTO> messageDTOs = conv.getMessages().stream()
                .map(m -> new MessageDTO(
                        m.getId(),
                        m.getRole(),
                        m.getContent(),
                        m.getSentAt()
                ))
                .toList();

        ConversationDTO dto = new ConversationDTO(
                conv.getId(),
                conv.getTitle(),
                conv.getCreatedAt(),
                messageDTOs
        );

        return ResponseEntity.ok(dto);
    }
    @PutMapping("/{id}")
    public ResponseEntity<MessageDTO> update(@PathVariable UUID id, @RequestBody Map<String, String> body) {
        Message msg = msgService.updateContent(id, body.get("content"));
        return ResponseEntity.ok(toDTO(msg));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        msgService.deleteById(id);
        return ResponseEntity.noContent().build();
    }

    private MessageDTO toDTO(Message m) {
        return new MessageDTO(m.getId(), m.getRole(), m.getContent(), m.getSentAt());
    }
}

record CreateMessageRequest(UUID convId, String role, String content) {}