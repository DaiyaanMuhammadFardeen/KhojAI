package com.khojgroup.KhojAI.dto;

import java.time.LocalDateTime;

public class DocumentDTO {
    private Long id;
    private String name;
    private String type;
    private Long size;
    private LocalDateTime uploadedAt;
    private String userId;

    // Constructors
    public DocumentDTO() {}

    public DocumentDTO(Long id, String name, String type, Long size, LocalDateTime uploadedAt, String userId) {
        this.id = id;
        this.name = name;
        this.type = type;
        this.size = size;
        this.uploadedAt = uploadedAt;
        this.userId = userId;
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public Long getSize() {
        return size;
    }

    public void setSize(Long size) {
        this.size = size;
    }

    public LocalDateTime getUploadedAt() {
        return uploadedAt;
    }

    public void setUploadedAt(LocalDateTime uploadedAt) {
        this.uploadedAt = uploadedAt;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }
}