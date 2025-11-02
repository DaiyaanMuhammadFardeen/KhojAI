package com.khojgroup.KhojAI.service;

import com.khojgroup.KhojAI.entity.Conversation;
import com.khojgroup.KhojAI.entity.User;
import com.khojgroup.KhojAI.repository.ConversationRepository;
import com.khojgroup.KhojAI.repository.UserRepository;
import jakarta.persistence.EntityNotFoundException;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
@Transactional
public class ConversationService {
    private final ConversationRepository repo;
    private final UserRepository userRepo;

    public Conversation create(UUID userId, String title) {
        User user = userRepo.findById(userId).orElseThrow();
        Conversation conv = new Conversation();
        conv.setTitle(title);
        user.addConversation(conv);
        return repo.save(conv);
    }

    public Conversation findById(UUID id) {
        return repo.findById(id).orElseThrow(() -> new EntityNotFoundException("Conversation not found"));
    }

    public Conversation updateTitle(UUID id, String title) {
        Conversation conv = findById(id);
        conv.setTitle(title);
        return conv;
    }

    public void deleteById(UUID id) {
        repo.deleteById(id);
    }
}