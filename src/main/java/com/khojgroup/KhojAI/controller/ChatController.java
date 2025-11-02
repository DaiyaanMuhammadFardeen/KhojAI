package com.khojgroup.KhojAI.controller;

import com.khojgroup.KhojAI.entity.Conversation;
import com.khojgroup.KhojAI.entity.Message;
import com.khojgroup.KhojAI.service.ChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    @PostMapping("/conversation")
    public Conversation create(@RequestBody Map<String, String> body) {
        return chatService.startConversation(
                UUID.fromString(body.get("userId")),
                body.get("title")
        );
    }
    public enum Role {
        USER, AI
    }
    @PostMapping("/message")
    public Message send(@RequestBody Map<String, String> body) {
        return chatService.sendMessage(
                UUID.fromString(body.get("convId")),
                body.get("role"),
                body.get("content")
        );
    }
}
