package com.khojgroup.KhojAI.repository;

import com.khojgroup.KhojAI.entity.Message;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface MessageRepository extends JpaRepository<Message, UUID> {
}
