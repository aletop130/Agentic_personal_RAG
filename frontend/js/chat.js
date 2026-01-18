let conversationHistory = [];
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const messagesContainer = document.getElementById('messages');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = chatInput.value.trim();
    if (!message) return;

    console.log('='*80);
    console.log('FRONTEND: Chat form submitted');
    console.log(`Message: '${message}'`);
    console.log(`Message length: ${message.length}`);
    console.log(`Message trimmed: '${message.trim()}'`);
    console.log(`Conversation history before:`, conversationHistory);

    chatInput.value = '';
    
    addMessage(message, 'user');
    conversationHistory.push({ role: 'user', content: message });
    
    console.log(`Conversation history after:`, conversationHistory);
    
    const loadingId = addLoadingMessage();
    
    try {
        console.log('FRONTEND: Calling chat API...');
        const response = await chat(message, conversationHistory);
        console.log('FRONTEND: Chat API response:', response);
        
        removeMessage(loadingId);
        
        addMessage(response.message, 'assistant');
        conversationHistory.push({ role: 'assistant', content: response.message });
        console.log(`Final conversation history:`, conversationHistory);
        
        if (response.sources && response.sources.length > 0) {
            addSources(response.sources);
        }
    } catch (error) {
        console.error('FRONTEND: Chat error:', error);
        console.error('Error details:', error.message);
        console.error('Error stack:', error.stack);
        removeMessage(loadingId);
        addMessage('Sorry, there was an error processing your request.', 'assistant', true);
    }
});

function addMessage(content, role, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = `max-w-[80%] rounded-lg p-4 ${
        role === 'user' 
            ? 'bg-blue-600 text-white' 
            : isError 
                ? 'bg-red-900 text-red-200' 
                : 'bg-gray-700 text-gray-100'
    }`;
    
    bubbleDiv.innerHTML = `
        <p class="text-sm whitespace-pre-wrap">${escapeHtml(content)}</p>
    `;
    
    messageDiv.appendChild(bubbleDiv);
    messagesContainer.appendChild(messageDiv);
    
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageDiv;
}

function addLoadingMessage() {
    const id = 'loading-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.id = id;
    messageDiv.className = 'flex justify-start';
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'bg-gray-700 text-gray-100 rounded-lg p-4';
    bubbleDiv.innerHTML = `
        <div class="flex items-center gap-2">
            <i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i>
            <span class="text-sm">Thinking...</span>
        </div>
    `;
    
    messageDiv.appendChild(bubbleDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    lucide.createIcons();
    
    return id;
}

function addSources(sources) {
    const sourcesDiv = document.createElement('div');
    sourcesDiv.className = 'mt-4 bg-gray-800 rounded-lg p-4';
    
    const sourcesTitle = document.createElement('div');
    sourcesTitle.className = 'flex items-center gap-2 mb-2 text-sm text-gray-400';
    sourcesTitle.innerHTML = `
        <i data-lucide="link" class="w-4 h-4"></i>
        <span>Sources</span>
    `;
    
    const sourcesList = document.createElement('div');
    sourcesList.className = 'space-y-2';
    
    sources.forEach(source => {
        const sourceItem = document.createElement('div');
        sourceItem.className = 'flex items-start gap-2 text-sm bg-gray-700 rounded p-2';
        sourceItem.innerHTML = `
            <i data-lucide="file-text" class="w-4 h-4 text-blue-400 mt-0.5"></i>
            <div>
                <p class="font-medium">${escapeHtml(source.filename)}</p>
                <p class="text-gray-400 text-xs">Page: ${source.page} • Score: ${source.score.toFixed(3)}</p>
            </div>
        `;
        sourcesList.appendChild(sourceItem);
    });
    
    sourcesDiv.appendChild(sourcesTitle);
    sourcesDiv.appendChild(sourcesList);
    messagesContainer.appendChild(sourcesDiv);
    
    lucide.createIcons();
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeMessage(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function clearConversation() {
    conversationHistory = [];
    messagesContainer.innerHTML = `
        <div class="text-center text-gray-500 py-8">
            <i data-lucide="sparkles" class="w-12 h-12 mx-auto mb-3 text-gray-600"></i>
            <p>Ask questions about your uploaded documents</p>
        </div>
    `;
    lucide.createIcons();
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('bg-blue-600', 'text-white');
        btn.classList.add('text-gray-400', 'hover:bg-gray-700');
    });
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    const activeTab = document.getElementById(`tab-${tabName}`);
    activeTab.classList.remove('text-gray-400', 'hover:bg-gray-700');
    activeTab.classList.add('bg-blue-600', 'text-white');
    
    document.getElementById(`section-${tabName}`).classList.remove('hidden');
    
    if (tabName === 'documents') {
        loadDocuments();
    }
}

function loadDocuments() {
    const documentsList = document.getElementById('documents-list');
    documentsList.innerHTML = '<div class="text-center py-4"><i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto"></i></div>';
    lucide.createIcons();
    
    listDocuments()
        .then(documents => {
            if (documents.length === 0) {
                documentsList.innerHTML = `
                    <div class="text-center text-gray-500 py-8">
                        <i data-lucide="files" class="w-12 h-12 mx-auto mb-3 text-gray-600"></i>
                        <p>No documents uploaded yet</p>
                    </div>
                `;
            } else {
                documentsList.innerHTML = documents.map(doc => `
                    <div class="bg-gray-700 rounded-lg p-4 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <i data-lucide="${getFileIcon(doc.file_type)}" class="w-8 h-8 text-blue-400"></i>
                            <div>
                                <p class="font-medium">${escapeHtml(doc.filename)}</p>
                                <p class="text-gray-400 text-sm">
                                    ${(doc.file_size / 1024).toFixed(1)} KB • 
                                    ${doc.chunk_count} chunks • 
                                    ${new Date(doc.uploaded_at).toLocaleDateString()}
                                </p>
                            </div>
                        </div>
                        <button onclick="deleteDocumentById('${doc.id}')" class="text-red-400 hover:text-red-300 p-2 hover:bg-red-500/20 rounded-lg transition-colors">
                            <i data-lucide="trash-2" class="w-5 h-5"></i>
                        </button>
                    </div>
                `).join('');
            }
            lucide.createIcons();
        })
        .catch(error => {
            documentsList.innerHTML = `
                <div class="text-center text-red-400 py-8">
                    <i data-lucide="alert-circle" class="w-12 h-12 mx-auto mb-3"></i>
                    <p>Failed to load documents: ${error.message}</p>
                </div>
            `;
            lucide.createIcons();
        });
}

function getFileIcon(fileType) {
    const icons = {
        pdf: 'file-type-2',
        docx: 'file-text',
        txt: 'file-code'
    };
    return icons[fileType] || 'file';
}

async function deleteDocumentById(docId) {
    if (!confirm('Are you sure you want to delete this document?')) return;
    
    try {
        await deleteDocument(docId);
        showToast('Document deleted successfully', 'success');
        loadDocuments();
    } catch (error) {
        console.error('Delete error:', error);
        showToast(`Failed to delete document: ${error.message}`, 'error');
    }
}

async function deleteAllDocuments() {
    if (!confirm('Are you sure you want to delete ALL documents? This cannot be undone.')) return;
    
    try {
        await deleteAllDocuments();
        showToast('All documents deleted successfully', 'success');
        loadDocuments();
        clearConversation();
    } catch (error) {
        console.error('Delete all error:', error);
        showToast(`Failed to delete documents: ${error.message}`, 'error');
    }
}
