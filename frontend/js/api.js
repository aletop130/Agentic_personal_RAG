const API_BASE_URL = 'http://localhost:8000';

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
}

async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(error.detail || 'Failed to upload document');
    }

    return response.json();
}

async function listDocuments() {
    return apiRequest('/api/documents');
}

async function deleteDocument(docId) {
    return apiRequest(`/api/documents/${docId}`, {
        method: 'DELETE',
    });
}

async function deleteAllDocuments() {
    return apiRequest('/api/documents/all', {
        method: 'DELETE',
    });
}

async function chat(message, conversationHistory = [], topK = 5) {
    console.log('API: chat function called');
    console.log(`API: message='${message}' (length: ${message.length})`);
    console.log(`API: conversationHistory=`, conversationHistory);
    console.log(`API: topK=${topK}`);
    
    const body = JSON.stringify({
        message,
        conversation_history: conversationHistory,
        top_k: topK,
    });
    console.log(`API: request body='${body}'`);
    
    const result = await apiRequest('/api/rag/chat', {
        method: 'POST',
        body: body,
    });
    
    console.log('API: response=', result);
    return result;
}

async function healthCheck() {
    return apiRequest('/api/health');
}

async function searchDocuments(query, topK = 5) {
    return apiRequest('/api/rag/search', {
        method: 'POST',
        body: JSON.stringify({
            message: query,
            top_k: topK,
        }),
    });
}
