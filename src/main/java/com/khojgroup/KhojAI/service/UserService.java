package com.khojgroup.KhojAI.service;

import com.khojgroup.KhojAI.entity.User;
import com.khojgroup.KhojAI.repository.UserRepository;
import jakarta.persistence.EntityNotFoundException;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
@Transactional
public class UserService {
    private final UserRepository repo;
    public User save(User user) { return repo.save(user); }
    public User findById(UUID id) { return repo.findById(id).orElseThrow(() -> new EntityNotFoundException("User not found")); }
    public void deleteById(UUID id) { repo.deleteById(id); }
}