package com.khojgroup.KhojAI.controller;

import com.khojgroup.KhojAI.config.JwtUtil;
import com.khojgroup.KhojAI.dto.JwtResponse;
import com.khojgroup.KhojAI.dto.LoginRequest;
import com.khojgroup.KhojAI.entity.User;
import com.khojgroup.KhojAI.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final JwtUtil jwtUtil;
    private final UserDetailsService userDetailsService;
    private final UserService userService;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest loginRequest) {
        try {
            // Authenticate user
            authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            loginRequest.username(), 
                            loginRequest.password())
            );
            
            // Generate JWT token
            final String token = jwtUtil.generateToken(loginRequest.username());
            
            // Get user details
            User user = userService.findByUsername(loginRequest.username());
            
            return ResponseEntity.ok(new JwtResponse(token, user.getUsername(), user.getId().toString()));
        } catch (Exception e) {
            return ResponseEntity.status(401).body("Invalid credentials");
        }
    }
}