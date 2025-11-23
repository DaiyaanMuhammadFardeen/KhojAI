package com.khojgroup.KhojAI;

import com.khojgroup.KhojAI.dto.DocumentDTO;
import com.khojgroup.KhojAI.entity.Document;
import com.khojgroup.KhojAI.repository.DocumentRepository;
import com.khojgroup.KhojAI.service.DocumentService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.mock.web.MockMultipartFile;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class DocumentServiceTest {

    @Mock
    private DocumentRepository documentRepository;

    @InjectMocks
    private DocumentService documentService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testGetDocumentsByUser() {
        // Arrange
        String userId = "user123";
        Document document1 = new Document("doc1.pdf", "application/pdf", 1024L, LocalDateTime.now(), userId);
        document1.setId(1L);

        Document document2 = new Document("doc2.txt", "text/plain", 512L, LocalDateTime.now(), userId);
        document2.setId(2L);

        when(documentRepository.findByUserId(userId)).thenReturn(Arrays.asList(document1, document2));

        // Act
        List<DocumentDTO> result = documentService.getDocumentsByUser(userId);

        // Assert
        assertEquals(2, result.size());
        assertEquals("doc1.pdf", result.get(0).getName());
        assertEquals("doc2.txt", result.get(1).getName());
        verify(documentRepository, times(1)).findByUserId(userId);
    }

    @Test
    void testUploadDocument() throws Exception {
        // Arrange
        String userId = "user123";
        MockMultipartFile mockFile = new MockMultipartFile(
            "file",
            "test.pdf",
            "application/pdf",
            "PDF content".getBytes()
        );

        Document savedDocument = new Document("test.pdf", "application/pdf", 12L, LocalDateTime.now(), userId);
        savedDocument.setId(1L);

        when(documentRepository.save(any(Document.class))).thenReturn(savedDocument);

        // Act
        DocumentDTO result = documentService.uploadDocument(userId, mockFile);

        // Assert
        assertNotNull(result);
        assertEquals("test.pdf", result.getName());
        assertEquals("application/pdf", result.getType());
        assertEquals(12L, result.getSize());
        verify(documentRepository, times(1)).save(any(Document.class));
    }

    @Test
    void testDeleteDocument() {
        // Arrange
        Long documentId = 1L;
        Document document = new Document("test.pdf", "application/pdf", 12L, LocalDateTime.now(), "user123");
        document.setId(documentId);

        when(documentRepository.findById(documentId)).thenReturn(Optional.of(document));

        // Act
        documentService.deleteDocument(documentId);

        // Assert
        verify(documentRepository, times(1)).findById(documentId);
        verify(documentRepository, times(1)).deleteById(documentId);
    }

    @Test
    void testDeleteDocumentNotFound() {
        // Arrange
        Long documentId = 1L;
        when(documentRepository.findById(documentId)).thenReturn(Optional.empty());

        // Act & Assert
        RuntimeException exception = assertThrows(RuntimeException.class, () -> {
            documentService.deleteDocument(documentId);
        });

        assertEquals("Document not found with id: " + documentId, exception.getMessage());
        verify(documentRepository, times(1)).findById(documentId);
        verify(documentRepository, times(0)).deleteById(documentId);
    }
}