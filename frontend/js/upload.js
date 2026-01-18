const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadProgress = document.getElementById('upload-progress');
const uploadStatus = document.getElementById('upload-status');

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-blue-500', 'bg-blue-500/10');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-blue-500', 'bg-blue-500/10');
});

dropZone.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-blue-500', 'bg-blue-500/10');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        await handleFiles(files);
    }
});

fileInput.addEventListener('change', async (e) => {
    const files = e.target.files;
    if (files.length > 0) {
        await handleFiles(files);
    }
});

async function handleFiles(files) {
    const validTypes = ['pdf', 'docx', 'txt'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    for (const file of files) {
        const fileType = file.name.split('.').pop().toLowerCase();
        
        if (!validTypes.includes(fileType)) {
            showToast(`Invalid file type: ${file.name}`, 'error');
            continue;
        }

        if (file.size > maxSize) {
            showToast(`File too large: ${file.name}`, 'error');
            continue;
        }

        uploadProgress.classList.remove('hidden');
        uploadStatus.textContent = `Uploading ${file.name}...`;

        try {
            await uploadDocument(file);
            showToast(`Document uploaded: ${file.name}`, 'success');
            loadDocuments();
        } catch (error) {
            console.error('Upload error:', error);
            showToast(`Failed to upload ${file.name}: ${error.message}`, 'error');
        }

        uploadProgress.classList.add('hidden');
    }

    fileInput.value = '';
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');

    toastMessage.textContent = message;
    
    if (type === 'success') {
        toastIcon.setAttribute('data-lucide', 'check-circle');
        toastIcon.classList.remove('text-red-400');
        toastIcon.classList.add('text-green-400');
    } else {
        toastIcon.setAttribute('data-lucide', 'x-circle');
        toastIcon.classList.remove('text-green-400');
        toastIcon.classList.add('text-red-400');
    }

    lucide.createIcons();
    
    toast.classList.remove('translate-y-20', 'opacity-0');
    
    setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
    }, 3000);
}
