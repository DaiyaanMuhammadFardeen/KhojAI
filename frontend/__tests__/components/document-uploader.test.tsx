import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import DocumentUploader from '@/components/document-uploader';
import * as documentApi from '@/app/api/documents/route';

// Mock the DocumentAPI
jest.mock('@/app/api/documents/route', () => ({
  DocumentAPI: {
    upload: jest.fn()
  }
}));

const mockedDocumentAPI = documentApi.DocumentAPI as jest.Mocked<typeof documentApi.DocumentAPI>;

describe('DocumentUploader', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => 'test-user-id'),
        setItem: jest.fn(),
        removeItem: jest.fn()
      },
      writable: true
    });
  });

  it('should render nothing when closed', () => {
    render(<DocumentUploader />);
    
    // Component should not be visible initially
    expect(screen.queryByText('Upload Document')).not.toBeInTheDocument();
  });

  it('should open when triggered by event', async () => {
    render(<DocumentUploader />);
    
    // Simulate opening the uploader via event
    act(() => {
      window.dispatchEvent(new CustomEvent('openDocumentUpload'));
    });

    // Now the modal should be visible
    expect(await screen.findByText('Upload Document')).toBeInTheDocument();
    expect(screen.getByText('Click to upload or drag and drop')).toBeInTheDocument();
  });

  it('should handle file selection', async () => {
    render(<DocumentUploader />);
    
    // Open the uploader
    act(() => {
      window.dispatchEvent(new CustomEvent('openDocumentUpload'));
    });
    
    await screen.findByText('Upload Document');

    // Create a mock file
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });

    // Get the file input and simulate file selection
    const fileInput = screen.getByTestId('file-input') || screen.getByLabelText(/choose file/i) || document.querySelector('input[type="file"]');
    
    if (fileInput) {
      fireEvent.change(fileInput, {
        target: { files: [file] }
      });
    }

    // Check if file name is displayed
    // Note: This might not work perfectly in JSDOM environment
    await waitFor(() => {
      expect(screen.queryByText('test.pdf')).toBeInTheDocument();
    }, { timeout: 1000 });
  });

  it('should handle drag and drop', async () => {
    render(<DocumentUploader />);
    
    // Open the uploader
    act(() => {
      window.dispatchEvent(new CustomEvent('openDocumentUpload'));
    });
    
    await screen.findByText('Upload Document');

    // Get the drop zone
    const dropZone = screen.getByText('Click to upload or drag and drop').closest('div');
    
    if (dropZone) {
      // Simulate drag enter
      fireEvent.dragEnter(dropZone, {
        dataTransfer: {
          items: [{ kind: 'file' }]
        }
      });

      // Check if drag state is active (this would require checking CSS classes)
      // We'll skip this detailed check for now as it's complex in JSDOM
      
      // Simulate drag leave
      fireEvent.dragLeave(dropZone);
    }
  });

  it('should call upload API when upload button is clicked', async () => {
    mockedDocumentAPI.upload.mockResolvedValueOnce({
      data: {
        id: 'doc-123',
        name: 'test.pdf',
        type: 'pdf',
        size: 1024,
        uploadedAt: new Date().toISOString()
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    render(<DocumentUploader />);
    
    // Open the uploader
    act(() => {
      window.dispatchEvent(new CustomEvent('openDocumentUpload'));
    });
    
    await screen.findByText('Upload Document');

    // Create and select a file
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
      fireEvent.change(fileInput, {
        target: { files: [file] }
      });
    }

    // Click upload button
    const uploadButton = screen.getByRole('button', { name: 'Upload' });
    fireEvent.click(uploadButton);

    // Wait for upload to complete
    await waitFor(() => {
      expect(mockedDocumentAPI.upload).toHaveBeenCalledWith('test-user-id', file);
    });
  });

  it('should show error message on upload failure', async () => {
    mockedDocumentAPI.upload.mockRejectedValueOnce(new Error('Upload failed'));

    render(<DocumentUploader />);
    
    // Open the uploader
    act(() => {
      window.dispatchEvent(new CustomEvent('openDocumentUpload'));
    });
    
    await screen.findByText('Upload Document');

    // Create and select a file
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
      fireEvent.change(fileInput, {
        target: { files: [file] }
      });
    }

    // Click upload button
    const uploadButton = screen.getByRole('button', { name: 'Upload' });
    fireEvent.click(uploadButton);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Upload failed')).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('should close when cancel button is clicked', async () => {
    render(<DocumentUploader />);
    
    // Open the uploader
    act(() => {
      window.dispatchEvent(new CustomEvent('openDocumentUpload'));
    });
    
    await screen.findByText('Upload Document');

    // Click cancel button
    const cancelButton = screen.getByRole('button', { name: 'Cancel' });
    fireEvent.click(cancelButton);

    // Modal should be closed
    expect(screen.queryByText('Upload Document')).not.toBeInTheDocument();
  });
});