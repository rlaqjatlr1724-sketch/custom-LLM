// 상태 관리
const state = {
    files: [],
    selectedFiles: new Set(),
    currentTab: 'upload'
};

// DOM 요소
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadProgress = document.getElementById('uploadProgress');
const uploadStatus = document.getElementById('uploadStatus');
const filesList = document.getElementById('filesList');
const fileCheckboxList = document.getElementById('fileCheckboxList');
const searchQuery = document.getElementById('searchQuery');
const searchBtn = document.getElementById('searchBtn');
const searchResult = document.getElementById('searchResult');
const resultContent = document.getElementById('resultContent');
const searchLoading = document.getElementById('searchLoading');
const toast = document.getElementById('toast');
const refreshFilesBtn = document.getElementById('refreshFilesBtn');
const selectAllBtn = document.getElementById('selectAllBtn');
const closeResultBtn = document.getElementById('closeResultBtn');

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadFiles();
    loadStores();
});

// 이벤트 리스너 설정
function setupEventListeners() {
    // 탭 네비게이션
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', handleTabChange);
    });

    // 파일 업로드
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);

    // 파일 목록
    refreshFilesBtn.addEventListener('click', loadFiles);

    // 검색
    searchBtn.addEventListener('click', performSearch);
    selectAllBtn.addEventListener('click', toggleSelectAll);
    closeResultBtn.addEventListener('click', () => {
        searchResult.style.display = 'none';
    });

    // Enter 키로 검색
    searchQuery.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            performSearch();
        }
    });
}

// 탭 변경
function handleTabChange(e) {
    const tabName = e.currentTarget.getAttribute('data-tab');

    // 네비게이션 업데이트
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    e.currentTarget.classList.add('active');

    // 탭 컨텐츠 업데이트
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');

    state.currentTab = tabName;

    // 탭별 초기화
    if (tabName === 'files') {
        loadFiles();
    } else if (tabName === 'stores') {
        loadStores();
    } else if (tabName === 'search') {
        loadFilesForSearch();
    }
}

// 파일 드래그 오버
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

// 파일 드래그 떠남
function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

// 파일 드롭
function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    handleFiles(files);
}

// 파일 선택
function handleFileSelect(e) {
    const files = e.target.files;
    handleFiles(files);
}

// 파일 처리
function handleFiles(files) {
    const fileArray = Array.from(files);

    uploadProgress.style.display = 'block';
    uploadStatus.innerHTML = '';

    fileArray.forEach((file, index) => {
        uploadFile(file, index, fileArray.length);
    });
}

// 파일 업로드
async function uploadFile(file, index, total) {
    const formData = new FormData();
    formData.append('file', file);

    const fileName = file.name;
    const statusItem = document.createElement('div');
    statusItem.className = 'status-item';
    statusItem.id = `status-${index}`;
    statusItem.innerHTML = `
        <div class="status-icon">⏳</div>
        <div class="status-content">
            <div class="status-title">${fileName}</div>
            <div class="status-message">업로드 중...</div>
        </div>
    `;
    uploadStatus.appendChild(statusItem);

    try {
        const response = await fetch('/api/files/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            statusItem.classList.add('success');
            statusItem.innerHTML = `
                <div class="status-icon">✓</div>
                <div class="status-content">
                    <div class="status-title">${fileName}</div>
                    <div class="status-message">업로드 완료</div>
                </div>
            `;
            showToast(`${fileName} 업로드 완료`, 'success');
        } else {
            throw new Error(data.error || '업로드 실패');
        }

        // 모든 파일이 업로드되면 파일 목록 새로고침
        if (document.querySelectorAll('.status-item.success').length === total) {
            setTimeout(() => {
                loadFiles();
                uploadProgress.style.display = 'none';
            }, 1000);
        }
    } catch (error) {
        statusItem.classList.add('error');
        statusItem.innerHTML = `
            <div class="status-icon">✗</div>
            <div class="status-content">
                <div class="status-title">${fileName}</div>
                <div class="status-message">${error.message}</div>
            </div>
        `;
        showToast(`${fileName} 업로드 실패: ${error.message}`, 'error');
    }
}

// 파일 목록 로드
async function loadFiles() {
    try {
        const response = await fetch('/api/files/list');
        const data = await response.json();

        if (data.success) {
            state.files = data.files;
            renderFiles();
            loadFilesForSearch();
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error loading files:', error);
        filesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">❌</div>
                <p>파일 로드 실패</p>
            </div>
        `;
    }
}

// 파일 렌더링
function renderFiles() {
    if (state.files.length === 0) {
        filesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <p>업로드된 파일이 없습니다</p>
            </div>
        `;
        return;
    }

    filesList.innerHTML = state.files.map(file => {
        const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
        const fileType = file.mime_type.split('/')[1].toUpperCase();
        const date = new Date(file.created_time).toLocaleDateString('ko-KR');

        return `
            <div class="file-card">
                <div class="file-card-header">
                    <div class="file-icon">${getFileIcon(file.mime_type)}</div>
                    <div class="file-card-actions">
                        <button title="삭제" onclick="deleteFile('${file.file_id}', '${file.file_name}')">🗑️</button>
                    </div>
                </div>
                <div class="file-name" title="${file.file_name}">${file.file_name}</div>
                <div class="file-type">${fileType}</div>
                <div class="file-info">
                    <span>${sizeInMB} MB</span>
                    <span class="file-date">${date}</span>
                </div>
            </div>
        `;
    }).join('');
}

// 파일 아이콘 가져오기
function getFileIcon(mimeType) {
    const iconMap = {
        'application/pdf': '📄',
        'text/plain': '📝',
        'application/msword': '📘',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '📘',
        'application/vnd.ms-excel': '📊',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '📊',
        'application/vnd.ms-powerpoint': '🎨',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '🎨',
        'text/csv': '📋',
        'application/json': '{}',
        'application/xml': '<>',
        'text/html': '🌐'
    };
    return iconMap[mimeType] || '📎';
}

// 파일 삭제
async function deleteFile(fileId, fileName) {
    if (!confirm(`"${fileName}"을(를) 정말 삭제하시겠습니까?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/files/${fileId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast(`${fileName} 삭제 완료`, 'success');
            loadFiles();
        } else {
            const data = await response.json();
            throw new Error(data.error);
        }
    } catch (error) {
        showToast(`삭제 실패: ${error.message}`, 'error');
    }
}

// FileStore 로드
async function loadStores() {
    try {
        const response = await fetch('/api/stores');
        const data = await response.json();

        if (data.success) {
            const storesContainer = document.getElementById('storesList');
            storesContainer.innerHTML = `
                <div class="store-info">
                    <p>✓ FileStore가 정상적으로 구성되었습니다</p>
                </div>
            `;

            // 통계 업데이트
            document.getElementById('totalFiles').textContent = state.files.length;
            const totalSize = (state.files.reduce((sum, f) => sum + f.size, 0) / (1024 * 1024)).toFixed(2);
            document.getElementById('totalSize').textContent = totalSize + ' MB';
        }
    } catch (error) {
        console.error('Error loading stores:', error);
    }
}

// 검색용 파일 로드
function loadFilesForSearch() {
    if (state.files.length === 0) {
        fileCheckboxList.innerHTML = `
            <div class="empty-state">
                <p>업로드된 파일이 없습니다</p>
            </div>
        `;
        return;
    }

    fileCheckboxList.innerHTML = state.files.map(file => {
        const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
        const fileId = file.file_id.replace('files/', '');

        return `
            <label class="checkbox-item">
                <input type="checkbox" value="${fileId}" class="file-checkbox" data-name="${file.file_name}">
                <span class="checkbox-label">${file.file_name}</span>
                <span class="checkbox-size">${sizeInMB} MB</span>
            </label>
        `;
    }).join('');
}

// 전체 선택
function toggleSelectAll() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);

    checkboxes.forEach(cb => {
        cb.checked = !allChecked;
    });

    selectAllBtn.textContent = allChecked ? '전체 선택' : '전체 해제';
}

// 검색 수행
async function performSearch() {
    const selectedCheckboxes = document.querySelectorAll('.file-checkbox:checked');

    if (selectedCheckboxes.length === 0) {
        showToast('검색할 파일을 선택하세요', 'warning');
        return;
    }

    const query = searchQuery.value.trim();
    if (!query) {
        showToast('검색 질문을 입력하세요', 'warning');
        return;
    }

    const fileIds = Array.from(selectedCheckboxes).map(cb => cb.value);

    searchLoading.style.display = 'flex';
    searchResult.style.display = 'none';

    try {
        const response = await fetch('/api/chat/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                file_ids: fileIds
            })
        });

        const data = await response.json();

        if (data.success) {
            resultContent.textContent = data.result;
            searchResult.style.display = 'block';
            showToast('검색 완료', 'success');
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        showToast(`검색 실패: ${error.message}`, 'error');
    } finally {
        searchLoading.style.display = 'none';
    }
}

// 토스트 메시지
function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
