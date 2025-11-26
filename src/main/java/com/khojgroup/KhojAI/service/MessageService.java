package com.khojgroup.KhojAI.service;

import com.khojgroup.KhojAI.entity.Conversation;
import com.khojgroup.KhojAI.entity.Message;
import com.khojgroup.KhojAI.repository.ConversationRepository;
import com.khojgroup.KhojAI.repository.MessageRepository;
import jakarta.persistence.EntityNotFoundException;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Set;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Transactional
public class MessageService {

    private final MessageRepository repo;
    private final ConversationRepository convRepo;
    private final AiService aiService;

    public Conversation create(UUID convId, String role, String content) {
        Conversation conv = convRepo.findById(convId)
                .orElseThrow(() -> new EntityNotFoundException("Conversation not found"));

        if (!Set.of("USER", "AI").contains(role)) {
            throw new IllegalArgumentException("Role must be USER or AI");
        }

        // Save USER message
        Message msg = new Message();
        msg.setRole(role);
        msg.setContent(content);
        conv.addMessage(msg);
        repo.save(msg);

        // AUTO AI REPLY
        if ("USER".equals(role)) {
            String aiReply = aiService.generateResponse(content);
            Message aiMsg = new Message();
            aiMsg.setRole("AI");
            aiMsg.setContent(aiReply);
            conv.addMessage(aiMsg);
            repo.save(aiMsg);
        }

        return conv; // Return full conversation
    }
    public Message updateContent(UUID id, String content) {
        Message msg = repo.findById(id).orElseThrow();
        msg.setContent(content);
        return msg;
    }

    public void deleteById(UUID id) {
        repo.deleteById(id);
    }
}