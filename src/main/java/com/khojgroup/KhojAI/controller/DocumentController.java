package com.khojgroup.KhojAI.controller;

import com.khojgroup.KhojAI.dto.DocumentDTO;
import com.khojgroup.KhojAI.service.DocumentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/v1/documents")
@CrossOrigin(origins = "http://localhost:3000") // Allow frontend to access
public class DocumentController {

    @Autowired
    private DocumentService documentService;

    @GetMapping("/user/{userId}")
    public ResponseEntity<List<DocumentDTO>> getDocumentsByUser(@PathVariable String userId) {
        List<DocumentDTO> documents = documentService.getDocumentsByUser(userId);
        return new ResponseEntity<>(documents, HttpStatus.OK);
    }

    @PostMapping("/upload")
    public ResponseEntity<DocumentDTO> uploadDocument(
            @RequestParam("file") MultipartFile file,
            @RequestParam("userId") String userId) {
        try {
            DocumentDTO document = documentService.uploadDocument(userId, file);
            return new ResponseEntity<>(document, HttpStatus.CREATED);
        } catch (IOException e) {
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDocument(@PathVariable Long id) {
        try {
            documentService.deleteDocument(id);
            return new ResponseEntity<>(HttpStatus.NO_CONTENT);
        } catch (RuntimeException e) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }
}