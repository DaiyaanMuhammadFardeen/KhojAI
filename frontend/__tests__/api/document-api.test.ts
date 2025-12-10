import { DocumentAPI } from '@/app/api/documents/route';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('DocumentAPI', () => {
  const userId = 'test-user-id';
  const documentId = 'test-document-id';
  const mockDocument = {
    id: documentId,
    name: 'test-document.pdf',
    type: 'pdf',
    size: 1024,
    uploadedAt: '2023-01-01T00:00:00Z'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getByUser', () => {
    it('should fetch documents for a user', async () => {
      const mockResponse = {
        data: [mockDocument],
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {}
      };
      
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const response = await DocumentAPI.getByUser(userId);
      
      expect(mockedAxios.get).toHaveBeenCalledWith(`/api/v1/documents/user/${userId}`);
      expect(response).toEqual(mockResponse);
    });

    it('should handle errors when fetching documents', async () => {
      const error = new Error('Network error');
      mockedAxios.get.mockRejectedValueOnce(error);

      await expect(DocumentAPI.getByUser(userId)).rejects.toThrow('Network error');
    });
  });

  describe('upload', () => {
    it('should upload a document', async () => {
      const mockFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
      const mockResponse = {
        data: mockDocument,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {}
      };
      
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const response = await DocumentAPI.upload(userId, mockFile);
      
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/v1/documents/upload',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      const formData = (mockedAxios.post.mock.calls[0][1] as FormData);
      expect(formData.get('file')).toBe(mockFile);
      expect(formData.get('userId')).toBe(userId);
      
      expect(response).toEqual(mockResponse);
    });

    it('should handle errors when uploading a document', async () => {
      const mockFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
      const error = new Error('Upload failed');
      mockedAxios.post.mockRejectedValueOnce(error);

      await expect(DocumentAPI.upload(userId, mockFile)).rejects.toThrow('Upload failed');
    });
  });

  describe('delete', () => {
    it('should delete a document', async () => {
      const mockResponse = {
        data: undefined,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {}
      };
      
      mockedAxios.delete.mockResolvedValueOnce(mockResponse);

      const response = await DocumentAPI.delete(documentId);
      
      expect(mockedAxios.delete).toHaveBeenCalledWith(`/api/v1/documents/${documentId}`);
      expect(response).toEqual(mockResponse);
    });

    it('should handle errors when deleting a document', async () => {
      const error = new Error('Document not found');
      mockedAxios.delete.mockRejectedValueOnce(error);

      await expect(DocumentAPI.delete(documentId)).rejects.toThrow('Document not found');
    });
  });
});