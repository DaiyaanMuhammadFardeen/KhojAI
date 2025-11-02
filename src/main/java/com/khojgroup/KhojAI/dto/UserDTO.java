package com.khojgroup.KhojAI.dto;

import java.util.UUID;

public record UserDTO(
        UUID id,
        String username,
        String email
) {}