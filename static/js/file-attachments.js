
/**
 * File Attachment Handler for N1O1 Clinical Trials
 * Supports various file types including images, videos, documents, and spreadsheets
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize file attachment handler
    initFileAttachments();
});

function initFileAttachments() {
    // Get file input elements
    const fileAttachment = document.getElementById('file-attachment');
    const attachmentsList = document.getElementById('attachmentsList');
    
    if (!fileAttachment || !attachmentsList) return;
    
    // Handle file selection
    fileAttachment.addEventListener('change', function() {
        // Clear the list
        attachmentsList.innerHTML = '';
        
        // Display selected files
        if (this.files.length > 0) {
            const fileListHeader = document.createElement('h6');
            fileListHeader.className = 'mt-3 mb-2';
            fileListHeader.innerText = 'Selected Files:';
            attachmentsList.appendChild(fileListHeader);
            
            const fileList = document.createElement('ul');
            fileList.className = 'list-group';
            
            for (let i = 0; i < this.files.length; i++) {
                const file = this.files[i];
                const fileItem = document.createElement('li');
                fileItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                
                // File icon based on type
                let fileIcon = 'fa-file';
                if (file.type.startsWith('image/')) {
                    fileIcon = 'fa-file-image';
                } else if (file.type.startsWith('video/')) {
                    fileIcon = 'fa-file-video';
                } else if (file.type.startsWith('audio/')) {
                    fileIcon = 'fa-file-audio';
                } else if (file.type.includes('spreadsheet') || file.name.endsWith('.xlsx') || file.name.endsWith('.csv')) {
                    fileIcon = 'fa-file-excel';
                } else if (file.type.includes('pdf') || file.name.endsWith('.pdf')) {
                    fileIcon = 'fa-file-pdf';
                } else if (file.type.includes('word') || file.name.endsWith('.doc') || file.name.endsWith('.docx')) {
                    fileIcon = 'fa-file-word';
                }
                
                // Format file size
                const fileSize = formatFileSize(file.size);
                
                fileItem.innerHTML = `
                    <div>
                        <i class="fas ${fileIcon} me-2"></i>
                        <span>${file.name}</span>
                    </div>
                    <span class="badge bg-secondary rounded-pill">${fileSize}</span>
                `;
                
                fileList.appendChild(fileItem);
            }
            
            attachmentsList.appendChild(fileList);
            
            // Add remove button
            const removeButton = document.createElement('button');
            removeButton.type = 'button';
            removeButton.className = 'btn btn-sm btn-outline-danger mt-2';
            removeButton.innerHTML = '<i class="fas fa-times me-1"></i> Clear Files';
            removeButton.addEventListener('click', function() {
                fileAttachment.value = '';
                attachmentsList.innerHTML = '';
            });
            attachmentsList.appendChild(removeButton);
        }
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    
    return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + sizes[i];
}
