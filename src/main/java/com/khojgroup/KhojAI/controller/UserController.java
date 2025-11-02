package com.khojgroup.KhojAI.controller;

import com.khojgroup.KhojAI.dto.UserDTO;
import com.khojgroup.KhojAI.entity.User;
import com.khojgroup.KhojAI.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;
    private final PasswordEncoder passwordEncoder;

    @PostMapping
    public ResponseEntity<UserDTO> create(@RequestBody CreateUserRequest req) {
        User user = new User();
        user.setUsername(req.username());
        user.setEmail(req.email());
        user.setPassword(passwordEncoder.encode(req.password()));
        User saved = userService.save(user);
        return ResponseEntity.ok(toDTO(saved));
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserDTO> get(@PathVariable UUID id) {
        return ResponseEntity.ok(toDTO(userService.findById(id)));
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserDTO> update(@PathVariable UUID id, @RequestBody UpdateUserRequest req) {
        User user = userService.findById(id);
        user.setUsername(req.username());
        user.setEmail(req.email());
        if (req.password() != null && !req.password().isBlank()) {
            user.setPassword(passwordEncoder.encode(req.password()));
        }
        return ResponseEntity.ok(toDTO(userService.save(user)));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        userService.deleteById(id);
        return ResponseEntity.noContent().build();
    }

    private UserDTO toDTO(User user) {
        return new UserDTO(user.getId(), user.getUsername(), user.getEmail());
    }
}

// Request DTOs
record CreateUserRequest(String username, String email, String password) {}
record UpdateUserRequest(String username, String email, String password) {}