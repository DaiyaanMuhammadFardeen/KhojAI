package com.khojgroup.KhojAI.service;

import com.khojgroup.KhojAI.dto.DocumentDTO;
import com.khojgroup.KhojAI.entity.Document;
import com.khojgroup.KhojAI.repository.DocumentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class DocumentService {

    @Autowired
    private DocumentRepository documentRepository;

    public List<DocumentDTO> getDocumentsByUser(String userId) {
        List<Document> documents = documentRepository.findByUserId(userId);
        return documents.stream().map(this::convertToDTO).collect(Collectors.toList());
    }

    public DocumentDTO uploadDocument(String userId, MultipartFile file) throws IOException {
        // Save document metadata to relational database
        Document document =new Document();
        document.setName(file.getOriginalFilename());
        document.setType(file.getContentType());
        document.setSize(file.getSize());
        document.setUserId(userId);
        document.setUploadedAt(LocalDateTime.now());
        
        Document savedDocument = documentRepository.save(document);
        
        return convertToDTO(savedDocument);
    }

    public void deleteDocument(Long documentId) {
        Document document = documentRepository.findById(documentId)
            .orElseThrow(() -> new RuntimeException("Document not found with id: " + documentId));
        
        // Remove from relational database
        documentRepository.deleteById(documentId);
    }

private DocumentDTO convertToDTO(Document document) {
        return new DocumentDTO(
            document.getId(),
            document.getName(),
            document.getType(),
            document.getSize(),
            document.getUploadedAt(),
            document.getUserId()
        );
    }
}