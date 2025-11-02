package com.khojgroup.KhojAI.dto;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

public record ConversationDTO(
        UUID id,
        String title,
        LocalDateTime createdAt,
        List<MessageDTO> messages
) {}