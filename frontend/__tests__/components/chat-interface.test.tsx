import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatInterface from '@/components/chat-interface';
import * as chatApi from '@/app/api/chat/route';

// Mock the APIs
jest.mock('@/app/api/chat/route', () => ({
  ConversationAPI: {
    get: jest.fn()
  },
  MessageAPI: {
    create: jest.fn()
  },
  AIApi: {
    generateResponse: jest.fn()
  }
}));

const mockedConversationAPI = chatApi.ConversationAPI as jest.Mocked<typeof chatApi.ConversationAPI>;
const mockedMessageAPI = chatApi.MessageAPI as jest.Mocked<typeof chatApi.MessageAPI>;
const mockedAIApi = chatApi.AIApi as jest.Mocked<typeof chatApi.AIApi>;

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

// Mock the ChatMessage component
jest.mock('@/components/chat-message', () => {
  return function MockChatMessage({ role, content }: { role: string; content: string }) {
    return (
      <div data-testid="chat-message" data-role={role}>
        {content}
      </div>
    );
  };
});

describe('ChatInterface', () => {
  const mockProps = {
    onMenuClick: jest.fn(),
    chatId: 'test-chat-id'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render empty state when no chat is selected', () => {
    render(<ChatInterface onMenuClick={jest.fn()} chatId={null} />);
    
    expect(screen.getByText('No Chat Selected')).toBeInTheDocument();
    expect(screen.getByText('Select an existing chat from the sidebar or create a new one to get started.')).toBeInTheDocument();
  });

  it('should render chat interface when chat is selected', async () => {
    mockedConversationAPI.get.mockResolvedValueOnce({
      data: {
        id: 'test-chat-id',
        title: 'Test Chat',
        createdAt: new Date().toISOString(),
        messages: []
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    render(<ChatInterface {...mockProps} />);

    expect(await screen.findByText('KhojAI Chat')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
  });

  it('should show drag and drop hint', async () => {
    mockedConversationAPI.get.mockResolvedValueOnce({
      data: {
        id: 'test-chat-id',
        title: 'Test Chat',
        createdAt: new Date().toISOString(),
        messages: []
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    render(<ChatInterface {...mockProps} />);

    expect(await screen.findByText('Drag & drop documents here or select from sidebar')).toBeInTheDocument();
  });

  it('should handle drag events', async () => {
    mockedConversationAPI.get.mockResolvedValueOnce({
      data: {
        id: 'test-chat-id',
        title: 'Test Chat',
        createdAt: new Date().toISOString(),
        messages: []
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    render(<ChatInterface {...mockProps} />);

    await screen.findByText('KhojAI Chat');

    const container = screen.getByText('KhojAI Chat').closest('div');
    
    if (container) {
      // Simulate drag enter
      fireEvent.dragEnter(container, {
        dataTransfer: {
          types: ['Files']
        }
      });

      // Simulate drag leave
      fireEvent.dragLeave(container);
    }
  });

  it('should show attached document', async () => {
    mockedConversationAPI.get.mockResolvedValueOnce({
      data: {
        id: 'test-chat-id',
        title: 'Test Chat',
        createdAt: new Date().toISOString(),
        messages: []
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    render(<ChatInterface {...mockProps} />);

    await screen.findByText('KhojAI Chat');

    // Simulate document attachment via event
    const mockDocument = {
      id: 'doc-1',
      name: 'Test Document.pdf',
      type: 'pdf',
      size: 1024,
      uploadedAt: new Date().toISOString()
    };

    fireEvent(
      window,
      new CustomEvent('documentSelected', { detail: mockDocument })
    );

    // Wait for document to appear
    await waitFor(() => {
      expect(screen.getByText('Test Document.pdf')).toBeInTheDocument();
    });
  });

  it('should remove attached document', async () => {
    mockedConversationAPI.get.mockResolvedValueOnce({
      data: {
        id: 'test-chat-id',
        title: 'Test Chat',
        createdAt: new Date().toISOString(),
        messages: []
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {}
    } as any);

    render(<ChatInterface {...mockProps} />);

    await screen.findByText('KhojAI Chat');

    // Simulate document attachment via event
    const mockDocument = {
      id: 'doc-1',
      name: 'Test Document.pdf',
      type: 'pdf',
      size: 1024,
      uploadedAt: new Date().toISOString()
    };

    fireEvent(
      window,
      new CustomEvent('documentSelected', { detail: mockDocument })
    );

    // Wait for document to appear
    await waitFor(() => {
      expect(screen.getByText('Test Document.pdf')).toBeInTheDocument();
    });

    // Click remove button
    const removeButton = screen.getByRole('button', { name: '×' });
    fireEvent.click(removeButton);

    // Document should be removed
    expect(screen.queryByText('Test Document.pdf')).not.toBeInTheDocument();
  });
});