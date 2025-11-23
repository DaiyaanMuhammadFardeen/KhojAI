package com.khojgroup.KhojAI;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.khojgroup.KhojAI.controller.DocumentController;
import com.khojgroup.KhojAI.dto.DocumentDTO;
import com.khojgroup.KhojAI.service.DocumentService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(DocumentController.class)
class DocumentControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private DocumentService documentService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void testGetDocumentsByUser() throws Exception {
        // Arrange
        String userId = "user123";
        DocumentDTO document1 = new DocumentDTO(1L, "doc1.pdf", "application/pdf", 1024L, LocalDateTime.now(), userId, "vector1", true);
        DocumentDTO document2 = new DocumentDTO(2L, "doc2.txt", "text/plain", 512L, LocalDateTime.now(), userId, null, false);
        List<DocumentDTO> documents = Arrays.asList(document1, document2);

        when(documentService.getDocumentsByUser(userId)).thenReturn(documents);

        // Act & Assert
        mockMvc.perform(get("/api/v1/documents/user/{userId}", userId)
                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(content().json(objectMapper.writeValueAsString(documents)));

        verify(documentService, times(1)).getDocumentsByUser(userId);
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

        DocumentDTO document = new DocumentDTO(1L, "test.pdf", "application/pdf", 12L, LocalDateTime.now(), userId, "vector1", true);
        when(documentService.uploadDocument(userId, mockFile)).thenReturn(document);

        // Act & Assert
        mockMvc.perform(multipart("/api/v1/documents/upload")
                .file(mockFile)
                .param("userId", userId))
                .andExpect(status().isCreated())
                .andExpect(content().json(objectMapper.writeValueAsString(document)));

        verify(documentService, times(1)).uploadDocument(userId, mockFile);
    }

    @Test
    void testDeleteDocument() throws Exception {
        // Arrange
        Long documentId = 1L;
        doNothing().when(documentService).deleteDocument(documentId);

        // Act & Assert
        mockMvc.perform(delete("/api/v1/documents/{id}", documentId))
                .andExpect(status().isNoContent());

        verify(documentService, times(1)).deleteDocument(documentId);
    }

    @Test
    void testIsDocumentProcessed() throws Exception {
        // Arrange
        Long documentId = 1L;
        when(documentService.isDocumentProcessed(documentId)).thenReturn(true);

        // Act & Assert
        mockMvc.perform(get("/api/v1/documents/{id}/processed", documentId))
                .andExpect(status().isOk())
                .andExpect(content().string("true"));

        verify(documentService, times(1)).isDocumentProcessed(documentId);
    }

    @Test
    void testGetProcessedDocumentsByUser() throws Exception {
        // Arrange
        String userId = "user123";
        DocumentDTO document1 = new DocumentDTO(1L, "doc1.pdf", "application/pdf", 1024L, LocalDateTime.now(), userId, "vector1", true);
        DocumentDTO document2 = new DocumentDTO(2L, "doc2.pdf", "application/pdf", 2048L, LocalDateTime.now(), userId, "vector2", true);
        List<DocumentDTO> documents = Arrays.asList(document1, document2);

        when(documentService.getProcessedDocumentsByUser(userId)).thenReturn(documents);

        // Act & Assert
        mockMvc.perform(get("/api/v1/documents/user/{userId}/processed", userId)
                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(content().json(objectMapper.writeValueAsString(documents)));

        verify(documentService, times(1)).getProcessedDocumentsByUser(userId);
    }
}