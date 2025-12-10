import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Sidebar from '@/components/sidebar';
import * as conversationApi from '@/app/api/chat/route';
import * as documentApi from '@/app/api/documents/route';

// Mock the APIs
jest.mock('@/app/api/chat/route', () => ({
  ConversationAPI: {
    getByUser: jest.fn(),
    create: jest.fn(),
    delete: jest.fn(),
    updateTitle: jest.fn()
  },
  MessageAPI: {
    create: jest.fn()
  },
  AIApi: {
    generateResponse: jest.fn()
  }
}));

jest.mock('@/app/api/documents/route', () => ({
  DocumentAPI: {
    getByUser: jest.fn()
  }
}));

const mockedConversationAPI = conversationApi.ConversationAPI as jest.Mocked<typeof conversationApi.ConversationAPI>;
const mockedDocumentAPI = documentApi.DocumentAPI as jest.Mocked<typeof documentApi.DocumentAPI>;

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn((key) => {
      if (key === 'userId') return 'test-user-id';
      return null;
    }),
    setItem: jest.fn(),
    removeItem: jest.fn()
  },
  writable: true
});

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn()
  })
}));

const mockProps = {
  isOpen: true,
  onToggle: jest.fn(),
  onChatSelect: jest.fn(),
  onSettingsClick: jest.fn(),
  selectedChatId: 'chat-1'
};

describe('Sidebar', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render conversations and documents sections', async () => {
    // Mock API responses
    mockedConversationAPI.getByUser.mockResolvedValueOnce({
      data: [{
        id: 'chat-1',
        title: 'Test Chat',
        createdAt: new Date().toISOString(),
        messages: []
      }],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    mockedDocumentAPI.getByUser.mockResolvedValueOnce({
      data: [{
        id: 'doc-1',
        name: 'Test Document.pdf',
        type: 'pdf',
        size: 1024,
        uploadedAt: new Date().toISOString()
      }],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    render(<Sidebar {...mockProps} />);

    // Check if conversations section is rendered
    expect(await screen.findByText('Conversations')).toBeInTheDocument();
    expect(screen.getByText('Test Chat')).toBeInTheDocument();

    // Check if documents section is rendered
    expect(screen.getByText('Documents')).toBeInTheDocument();
    expect(screen.getByText('Test Document.pdf')).toBeInTheDocument();
  });

  it('should show loading state for documents', async () => {
    // Mock conversations loaded immediately
    mockedConversationAPI.getByUser.mockResolvedValueOnce({
      data: [],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    // Don't resolve documents promise to simulate loading state
    mockedDocumentAPI.getByUser.mockImplementation(() => new Promise(() => {}));

    render(<Sidebar {...mockProps} />);

    // Should show loading text for documents
    expect(await screen.findByText('Loading documents...')).toBeInTheDocument();
  });

  it('should show empty state for documents', async () => {
    mockedConversationAPI.getByUser.mockResolvedValueOnce({
      data: [],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    mockedDocumentAPI.getByUser.mockResolvedValueOnce({
      data: [],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    render(<Sidebar {...mockProps} />);

    // Should show empty state for documents
    expect(await screen.findByText('No documents uploaded')).toBeInTheDocument();
  });

  it('should dispatch event when document is selected', async () => {
    mockedConversationAPI.getByUser.mockResolvedValueOnce({
      data: [],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    mockedDocumentAPI.getByUser.mockResolvedValueOnce({
      data: [{
        id: 'doc-1',
        name: 'Test Document.pdf',
        type: 'pdf',
        size: 1024,
        uploadedAt: new Date().toISOString()
      }],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    render(<Sidebar {...mockProps} />);

    // Wait for document to appear
    const documentItem = await screen.findByText('Test Document.pdf');
    
    // Spy on event dispatch
    const eventSpy = jest.spyOn(window, 'dispatchEvent');

    // Click on document
    fireEvent.click(documentItem);

    // Check if event was dispatched
    expect(eventSpy).toHaveBeenCalledWith(expect.objectContaining({
      type: 'documentSelected'
    }));
  });

  it('should dispatch event when upload button is clicked', async () => {
    mockedConversationAPI.getByUser.mockResolvedValueOnce({
      data: [],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    mockedDocumentAPI.getByUser.mockResolvedValueOnce({
      data: [],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    render(<Sidebar {...mockProps} />);

    await screen.findByText('No documents uploaded');

    // Find the upload button (it's the one with the Upload icon)
    const uploadButtons = screen.getAllByRole('button');
    const uploadButton = uploadButtons.find(button => 
      button.querySelector('svg')
    );

    // Spy on event dispatch
    const eventSpy = jest.spyOn(window, 'dispatchEvent');

    if (uploadButton) {
      fireEvent.click(uploadButton);
    }

    // Check if event was dispatched
    expect(eventSpy).toHaveBeenCalledWith(expect.objectContaining({
      type: 'openDocumentUpload'
    }));
  });
});