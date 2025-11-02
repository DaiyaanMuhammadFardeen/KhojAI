package com.khojgroup.KhojAI.service;

import com.khojgroup.KhojAI.entity.Conversation;
import com.khojgroup.KhojAI.entity.Message;
import com.khojgroup.KhojAI.entity.User;
import com.khojgroup.KhojAI.repository.ConversationRepository;
import com.khojgroup.KhojAI.repository.MessageRepository;
import com.khojgroup.KhojAI.repository.UserRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ChatService {

    private final UserRepository userRepo;
    private final ConversationRepository convRepo;
    private final MessageRepository msgRepo;

    @Transactional
    public Conversation startConversation(UUID userId, String title) {
        User user = userRepo.findById(userId).orElseThrow();
        Conversation conv = new Conversation();
        conv.setTitle(title);
        user.addConversation(conv);
        return convRepo.save(conv);
    }
    @Transactional
    public Message sendMessage(UUID convId, String role, String content) {
        Conversation conv = convRepo.findById(convId).orElseThrow();
        // simple validation (optional but recommended)
        if (!Message.ROLE_USER.equals(role) && !Message.ROLE_AI.equals(role)) {
            throw new IllegalArgumentException("role must be USER or AI");
        }
        Message msg = new Message();
        msg.setRole(role);                 // <-- plain string
        msg.setContent(content);
        conv.addMessage(msg);
        return msgRepo.save(msg);    }
}