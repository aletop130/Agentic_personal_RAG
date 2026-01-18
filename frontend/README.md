# Agentic RAG - Frontend

## Overview

Single-page HTML frontend for the Agentic RAG system with document upload, chat interface, and document management.

## Features

- **Document Upload**: Drag & drop interface for PDF, DOCX, and TXT files
- **Chat Interface**: Interactive chat with streaming responses and source citations
- **Document Management**: View, delete, and manage uploaded documents
- **Modern UI**: Built with Tailwind CSS and Lucide icons
- **Responsive**: Mobile-friendly design

## Setup

1. Open `index.html` in your browser
2. Or serve it with a simple HTTP server:

```bash
cd frontend
python -m http.server 8000
# or
npx serve .
```

## API Integration

The frontend communicates with the backend API running on `http://localhost:8000`.

To change the API URL, edit `js/api.js`:

```javascript
const API_BASE_URL = 'http://your-api-url:8000';
```

## File Structure

```
frontend/
├── index.html          # Main HTML file
├── css/
│   └── custom.css      # Custom styles
└── js/
    ├── api.js          # API client functions
    ├── upload.js       # File upload handling
    └── chat.js        # Chat functionality
```

## Usage

### Upload Documents
1. Click on the "Upload" tab
2. Drag & drop files or click "Select Files"
3. Supported formats: PDF, DOCX, TXT (max 10MB)

### Chat
1. Click on the "Chat" tab
2. Type your question about uploaded documents
3. View AI responses with source citations

### Manage Documents
1. Click on the "Documents" tab
2. View all uploaded documents
3. Delete individual documents or delete all

## Customization

### Change Colors
Edit `css/custom.css` to modify the color scheme.

### Add More File Types
Update the `validTypes` array in `js/upload.js`.

### Modify Chat Behavior
Edit `js/chat.js` to change conversation handling or UI elements.

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari

## Troubleshooting

**CORS Errors**: Ensure the backend CORS settings allow your frontend URL.

**Upload Fails**: Check file size (max 10MB) and format (PDF, DOCX, TXT).

**Chat Not Working**: Verify backend is running and health check passes.

## License

MIT
