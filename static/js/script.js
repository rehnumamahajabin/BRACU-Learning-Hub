// BRACU Learning Hub - Main JavaScript File

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('BRACU Learning Hub loaded successfully');
  
  // Initialize tooltips
  initializeTooltips();
  
  // Initialize file upload previews
  initializeFileUploads();
  
  // Initialize material interactions
  initializeMaterialInteractions();
  
  // Initialize comment system
  initializeCommentSystem();
  
  // Initialize search functionality
  initializeSearch();
  
  // Initialize admin features
  initializeAdminFeatures();
  
  // Initialize responsive behaviors
  initializeResponsiveBehaviors();
});

// Tooltip Initialization
function initializeTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

// File Upload with Preview
function initializeFileUploads() {
  const fileInputs = document.querySelectorAll('input[type="file"]');
  
  fileInputs.forEach(input => {
    input.addEventListener('change', function(e) {
      const file = e.target.files[0];
      const previewId = this.getAttribute('data-preview');
      
      if (previewId && file) {
        const previewElement = document.getElementById(previewId);
        if (previewElement) {
          updateFilePreview(previewElement, file);
        }
      }
      
      // Update file size validation
      validateFileSize(this);
    });
  });
  
  // Drag and drop functionality
  const dropZones = document.querySelectorAll('.file-upload-area');
  dropZones.forEach(zone => {
    zone.addEventListener('dragover', function(e) {
      e.preventDefault();
      this.classList.add('dragover');
    });
    
    zone.addEventListener('dragleave', function(e) {
      e.preventDefault();
      this.classList.remove('dragover');
    });
    
    zone.addEventListener('drop', function(e) {
      e.preventDefault();
      this.classList.remove('dragover');
      
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        const fileInput = this.querySelector('input[type="file"]');
        if (fileInput) {
          fileInput.files = files;
          fileInput.dispatchEvent(new Event('change'));
        }
      }
    });
  });
}

function updateFilePreview(element, file) {
  const reader = new FileReader();
  
  reader.onload = function(e) {
    if (file.type.startsWith('image/')) {
      element.innerHTML = `<img src="${e.target.result}" class="img-fluid" alt="Preview">`;
    } else {
      const icon = getFileIcon(file.name);
      element.innerHTML = `
        <div class="text-center">
          <i class="${icon}" style="font-size: 3rem;"></i>
          <p class="mt-2 mb-0">${file.name}</p>
          <small class="text-muted">${formatFileSize(file.size)}</small>
        </div>
      `;
    }
  };
  
  reader.readAsDataURL(file);
}

function getFileIcon(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  const icons = {
    'pdf': 'bi bi-file-earmark-pdf text-danger',
    'doc': 'bi bi-file-earmark-word text-primary',
    'docx': 'bi bi-file-earmark-word text-primary',
    'ppt': 'bi bi-file-earmark-ppt text-danger',
    'pptx': 'bi bi-file-earmark-ppt text-danger',
    'txt': 'bi bi-file-earmark-text text-secondary',
    'jpg': 'bi bi-file-earmark-image text-success',
    'jpeg': 'bi bi-file-earmark-image text-success',
    'png': 'bi bi-file-earmark-image text-success',
    'zip': 'bi bi-file-earmark-zip text-warning',
    'rar': 'bi bi-file-earmark-zip text-warning'
  };
  
  return icons[ext] || 'bi bi-file-earmark text-secondary';
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function validateFileSize(input) {
  const maxSize = 50 * 1024 * 1024; // 50MB
  const file = input.files[0];
  
  if (file && file.size > maxSize) {
    alert('File size exceeds 50MB limit. Please choose a smaller file.');
    input.value = '';
  }
}

// Material Interactions
function initializeMaterialInteractions() {
  // Save/Unsave material
  const saveButtons = document.querySelectorAll('[data-action="save-material"]');
  saveButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const materialId = this.getAttribute('data-material-id');
      toggleMaterialSave(materialId, this);
    });
  });
  
  // Rate material
  const ratingButtons = document.querySelectorAll('[data-action="rate-material"]');
  ratingButtons.forEach(button => {
    button.addEventListener('click', function() {
      const materialId = this.getAttribute('data-material-id');
      const rating = this.getAttribute('data-rating');
      submitRating(materialId, rating, this);
    });
  });
  
  // Download counter
  const downloadLinks = document.querySelectorAll('a[download]');
  downloadLinks.forEach(link => {
    link.addEventListener('click', function() {
      const materialId = this.getAttribute('data-material-id');
      if (materialId) {
        incrementDownloadCount(materialId);
      }
    });
  });
}

function toggleMaterialSave(materialId, button) {
  const isSaved = button.classList.contains('active');
  const url = `/api/materials/${materialId}/save/`;
  const method = isSaved ? 'DELETE' : 'POST';
  
  fetch(url, {
    method: method,
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/json',
    },
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      if (isSaved) {
        button.classList.remove('active', 'btn-warning');
        button.classList.add('btn-outline-warning');
        button.innerHTML = '<i class="bi bi-bookmark"></i> Save';
        showToast('Material removed from saved items', 'info');
      } else {
        button.classList.remove('btn-outline-warning');
        button.classList.add('active', 'btn-warning');
        button.innerHTML = '<i class="bi bi-bookmark-check"></i> Saved';
        showToast('Material saved successfully', 'success');
      }
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showToast('Error saving material', 'error');
  });
}

function submitRating(materialId, rating, button) {
  fetch(`/api/materials/${materialId}/rate/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ rating: rating }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Update all rating buttons
      const ratingButtons = document.querySelectorAll(`[data-material-id="${materialId}"][data-action="rate-material"]`);
      ratingButtons.forEach(btn => {
        btn.classList.remove('active', 'btn-warning');
        btn.classList.add('btn-outline-warning');
      });
      
      // Activate selected button
      button.classList.remove('btn-outline-warning');
      button.classList.add('active', 'btn-warning');
      
      // Update average rating display
      const avgRatingElement = document.querySelector(`[data-material-id="${materialId}"] .average-rating`);
      if (avgRatingElement && data.average_rating) {
        avgRatingElement.textContent = data.average_rating.toFixed(1);
      }
      
      showToast('Rating submitted successfully', 'success');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showToast('Error submitting rating', 'error');
  });
}

function incrementDownloadCount(materialId) {
  fetch(`/api/materials/${materialId}/download/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
    },
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const downloadCountElement = document.querySelector(`[data-material-id="${materialId}"] .download-count`);
      if (downloadCountElement) {
        const currentCount = parseInt(downloadCountElement.textContent) || 0;
        downloadCountElement.textContent = currentCount + 1;
      }
    }
  })
  .catch(error => console.error('Error:', error));
}

// Comment System
function initializeCommentSystem() {
  // Comment form submission
  const commentForms = document.querySelectorAll('.comment-form');
  commentForms.forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      submitComment(this);
    });
  });
  
  // Comment voting
  const voteButtons = document.querySelectorAll('[data-action="vote-comment"]');
  voteButtons.forEach(button => {
    button.addEventListener('click', function() {
      const commentId = this.getAttribute('data-comment-id');
      const voteType = this.getAttribute('data-vote-type');
      voteComment(commentId, voteType, this);
    });
  });
  
  // Comment reporting
  const reportButtons = document.querySelectorAll('[data-action="report-comment"]');
  reportButtons.forEach(button => {
    button.addEventListener('click', function() {
      const commentId = this.getAttribute('data-comment-id');
      reportComment(commentId, this);
    });
  });
}

function submitComment(form) {
  const formData = new FormData(form);
  const url = form.getAttribute('action');
  
  fetch(url, {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': getCSRFToken(),
    },
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Add new comment to list
      const commentsList = form.closest('.card-body').querySelector('.comments-section');
      if (commentsList) {
        const newComment = createCommentElement(data.comment);
        commentsList.appendChild(newComment);
        
        // Clear form
        form.reset();
        
        // Show success message
        showToast('Comment posted successfully', 'success');
        
        // Scroll to new comment
        newComment.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showToast('Error posting comment', 'error');
  });
}

function createCommentElement(commentData) {
  const div = document.createElement('div');
  div.className = 'card mb-3 comment-card fade-in';
  div.setAttribute('data-comment-id', commentData.id);
  
  div.innerHTML = `
    <div class="card-body">
      <div class="d-flex justify-content-between">
        <div>
          <strong>${commentData.user}</strong>
          <small class="text-muted">just now</small>
        </div>
        <div class="dropdown">
          <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="dropdown">
            <i class="bi bi-three-dots"></i>
          </button>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item text-danger" href="#" data-action="report-comment" data-comment-id="${commentData.id}">
              <i class="bi bi-flag"></i> Report
            </a></li>
          </ul>
        </div>
      </div>
      <p class="mt-2 mb-2">${commentData.content}</p>
      <div class="d-flex align-items-center">
        <button class="btn btn-sm btn-outline-success" data-action="vote-comment" data-comment-id="${commentData.id}" data-vote-type="upvote">
          <i class="bi bi-hand-thumbs-up"></i> 0
        </button>
        <button class="btn btn-sm btn-outline-danger ms-2" data-action="vote-comment" data-comment-id="${commentData.id}" data-vote-type="downvote">
          <i class="bi bi-hand-thumbs-down"></i> 0
        </button>
      </div>
    </div>
  `;
  
  // Re-initialize event listeners for new elements
  setTimeout(() => {
    const voteBtns = div.querySelectorAll('[data-action="vote-comment"]');
    voteBtns.forEach(btn => {
      btn.addEventListener('click', function() {
        const commentId = this.getAttribute('data-comment-id');
        const voteType = this.getAttribute('data-vote-type');
        voteComment(commentId, voteType, this);
      });
    });
    
    const reportBtn = div.querySelector('[data-action="report-comment"]');
    if (reportBtn) {
      reportBtn.addEventListener('click', function(e) {
        e.preventDefault();
        const commentId = this.getAttribute('data-comment-id');
        reportComment(commentId, this);
      });
    }
  }, 100);
  
  return div;
}

function voteComment(commentId, voteType, button) {
  fetch(`/api/comments/${commentId}/vote/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ vote_type: voteType }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Update vote counts
      const upvoteBtn = document.querySelector(`[data-comment-id="${commentId}"][data-vote-type="upvote"]`);
      const downvoteBtn = document.querySelector(`[data-comment-id="${commentId}"][data-vote-type="downvote"]`);
      
      if (upvoteBtn) {
        upvoteBtn.innerHTML = `<i class="bi bi-hand-thumbs-up"></i> ${data.upvotes}`;
        if (voteType === 'upvote') {
          upvoteBtn.classList.remove('btn-outline-success');
          upvoteBtn.classList.add('btn-success');
          if (downvoteBtn) {
            downvoteBtn.classList.remove('btn-danger');
            downvoteBtn.classList.add('btn-outline-danger');
          }
        }
      }
      
      if (downvoteBtn) {
        downvoteBtn.innerHTML = `<i class="bi bi-hand-thumbs-down"></i> ${data.downvotes}`;
        if (voteType === 'downvote') {
          downvoteBtn.classList.remove('btn-outline-danger');
          downvoteBtn.classList.add('btn-danger');
          if (upvoteBtn) {
            upvoteBtn.classList.remove('btn-success');
            upvoteBtn.classList.add('btn-outline-success');
          }
        }
      }
    }
  })
  .catch(error => console.error('Error:', error));
}

function reportComment(commentId, button) {
  if (confirm('Report this comment as inappropriate?')) {
    fetch(`/api/comments/${commentId}/report/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        const commentCard = button.closest('.comment-card');
        if (commentCard) {
          commentCard.classList.add('reported');
          commentCard.innerHTML += '<span class="badge bg-danger ms-2">Reported</span>';
        }
        showToast('Comment reported successfully', 'success');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showToast('Error reporting comment', 'error');
    });
  }
}

// Search Functionality
function initializeSearch() {
  const searchInput = document.querySelector('#global-search');
  const searchForm = document.querySelector('#search-form');
  
  if (searchInput) {
    // Debounced search
    let debounceTimer;
    searchInput.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        performSearch(this.value);
      }, 300);
    });
    
    // Clear search
    const clearBtn = searchInput.parentElement.querySelector('.search-clear');
    if (clearBtn) {
      clearBtn.addEventListener('click', function() {
        searchInput.value = '';
        searchInput.focus();
        clearSearchResults();
      });
    }
  }
  
  if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const query = this.querySelector('input[name="q"]').value;
      if (query.trim()) {
        window.location.href = `/search/?q=${encodeURIComponent(query)}`;
      }
    });
  }
}

function performSearch(query) {
  if (query.length < 2) {
    clearSearchResults();
    return;
  }
  
  fetch(`/api/search/suggestions/?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
      displaySearchSuggestions(data.suggestions, query);
    })
    .catch(error => console.error('Search error:', error));
}

function displaySearchSuggestions(suggestions, query) {
  const suggestionsContainer = document.querySelector('.search-suggestions');
  if (!suggestionsContainer) return;
  
  if (suggestions.length === 0) {
    suggestionsContainer.innerHTML = `
      <div class="dropdown-item text-muted">
        No results found for "${query}"
      </div>
    `;
    suggestionsContainer.classList.add('show');
    return;
  }
  
  let html = '';
  suggestions.forEach(suggestion => {
    html += `
      <a class="dropdown-item" href="${suggestion.url}">
        <div class="d-flex align-items-center">
          <i class="${getSuggestionIcon(suggestion.type)} me-2"></i>
          <div>
            <div>${highlightText(suggestion.title, query)}</div>
            <small class="text-muted">${suggestion.subtitle}</small>
          </div>
        </div>
      </a>
    `;
  });
  
  html += `
    <div class="dropdown-divider"></div>
    <a class="dropdown-item text-primary" href="/search/?q=${encodeURIComponent(query)}">
      <i class="bi bi-search me-2"></i>
      See all results for "${query}"
    </a>
  `;
  
  suggestionsContainer.innerHTML = html;
  suggestionsContainer.classList.add('show');
}

function clearSearchResults() {
  const suggestionsContainer = document.querySelector('.search-suggestions');
  if (suggestionsContainer) {
    suggestionsContainer.innerHTML = '';
    suggestionsContainer.classList.remove('show');
  }
}

function getSuggestionIcon(type) {
  const icons = {
    'material': 'bi bi-file-earmark-text',
    'post': 'bi bi-chat-text',
    'user': 'bi bi-person',
    'subject': 'bi bi-journal-text',
    'group': 'bi bi-people'
  };
  return icons[type] || 'bi bi-search';
}

function highlightText(text, query) {
  if (!query) return text;
  const regex = new RegExp(`(${query})`, 'gi');
  return text.replace(regex, '<span class="text-primary fw-bold">$1</span>');
}

// Admin Features
function initializeAdminFeatures() {
  // Bulk actions
  const bulkCheckboxes = document.querySelectorAll('.bulk-select');
  const bulkActionSelect = document.querySelector('#bulk-action-select');
  const bulkActionBtn = document.querySelector('#bulk-action-btn');
  
  if (bulkCheckboxes.length > 0) {
    // Select all checkbox
    const selectAll = document.querySelector('#select-all');
    if (selectAll) {
      selectAll.addEventListener('change', function() {
        bulkCheckboxes.forEach(cb => {
          cb.checked = this.checked;
        });
        updateBulkActionState();
      });
    }
    
    // Individual checkbox change
    bulkCheckboxes.forEach(cb => {
      cb.addEventListener('change', updateBulkActionState);
    });
    
    // Bulk action button
    if (bulkActionSelect && bulkActionBtn) {
      bulkActionBtn.addEventListener('click', function() {
        const action = bulkActionSelect.value;
        const selectedIds = getSelectedIds();
        
        if (selectedIds.length === 0) {
          showToast('Please select items to perform action', 'warning');
          return;
        }
        
        if (action && confirm(`Perform ${action} on ${selectedIds.length} selected items?`)) {
          performBulkAction(action, selectedIds);
        }
      });
    }
  }
  
  // Quick approve/reject buttons
  const quickActionBtns = document.querySelectorAll('[data-action="quick-action"]');
  quickActionBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const action = this.getAttribute('data-action-type');
      const itemId = this.getAttribute('data-item-id');
      const itemType = this.getAttribute('data-item-type');
      
      if (action && itemId && itemType) {
        performQuickAction(action, itemType, itemId, this);
      }
    });
  });
}

function updateBulkActionState() {
  const selectedCount = document.querySelectorAll('.bulk-select:checked').length;
  const bulkActionBtn = document.querySelector('#bulk-action-btn');
  const selectAll = document.querySelector('#select-all');
  
  if (selectAll) {
    const totalCheckboxes = document.querySelectorAll('.bulk-select').length;
    const checkedCheckboxes = document.querySelectorAll('.bulk-select:checked').length;
    selectAll.checked = totalCheckboxes > 0 && checkedCheckboxes === totalCheckboxes;
    selectAll.indeterminate = checkedCheckboxes > 0 && checkedCheckboxes < totalCheckboxes;
  }
  
  if (bulkActionBtn) {
    if (selectedCount > 0) {
      bulkActionBtn.disabled = false;
      bulkActionBtn.textContent = `Apply to ${selectedCount} items`;
    } else {
      bulkActionBtn.disabled = true;
      bulkActionBtn.textContent = 'Apply';
    }
  }
}

function getSelectedIds() {
  const ids = [];
  document.querySelectorAll('.bulk-select:checked').forEach(cb => {
    ids.push(cb.value);
  });
  return ids;
}

function performBulkAction(action, ids) {
  fetch('/api/admin/bulk-action/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      action: action,
      ids: ids
    }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      showToast(`${action} completed for ${ids.length} items`, 'success');
      setTimeout(() => location.reload(), 1000);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showToast('Error performing bulk action', 'error');
  });
}

function performQuickAction(action, itemType, itemId, button) {
  fetch(`/api/admin/${itemType}/${itemId}/${action}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
    },
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const card = button.closest('.card');
      if (card) {
        card.classList.add('fade-out');
        setTimeout(() => card.remove(), 300);
      }
      showToast(`${itemType} ${action}d successfully`, 'success');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showToast(`Error ${action}ing ${itemType}`, 'error');
  });
}

// Responsive Behaviors
function initializeResponsiveBehaviors() {
  // Mobile menu enhancements
  const navbarToggler = document.querySelector('.navbar-toggler');
  if (navbarToggler) {
    navbarToggler.addEventListener('click', function() {
      document.body.classList.toggle('mobile-menu-open');
    });
  }
  
  // Sidebar collapse for small screens
  const sidebarToggles = document.querySelectorAll('[data-bs-toggle="collapse"]');
  sidebarToggles.forEach(toggle => {
    toggle.addEventListener('click', function() {
      const target = document.querySelector(this.getAttribute('data-bs-target'));
      if (target && window.innerWidth < 992) {
        target.classList.toggle('show');
      }
    });
  });
  
  // Lazy loading images
  if ('IntersectionObserver' in window) {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.getAttribute('data-src');
          img.removeAttribute('data-src');
          observer.unobserve(img);
        }
      });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
  }
  
  // Infinite scroll for materials and posts
  let isLoading = false;
  let currentPage = 1;
  
  window.addEventListener('scroll', function() {
    if (isLoading || !document.querySelector('.infinite-scroll-trigger')) return;
    
    const trigger = document.querySelector('.infinite-scroll-trigger');
    const triggerPosition = trigger.getBoundingClientRect().top;
    const screenPosition = window.innerHeight;
    
    if (triggerPosition < screenPosition) {
      loadMoreContent();
    }
  });
}

function loadMoreContent() {
  isLoading = true;
  currentPage++;
  
  const url = window.location.pathname + `?page=${currentPage}` + window.location.search.replace(/\?page=\d+/, '');
  
  fetch(url)
    .then(response => response.text())
    .then(html => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const newItems = doc.querySelector('#content-container').innerHTML;
      
      const container = document.querySelector('#content-container');
      if (container) {
        container.innerHTML += newItems;
        
        // Re-initialize event listeners for new items
        setTimeout(() => {
          initializeMaterialInteractions();
          initializeCommentSystem();
          isLoading = false;
        }, 100);
      }
    })
    .catch(error => {
      console.error('Error loading more content:', error);
      isLoading = false;
    });
}

// Utility Functions
function getCSRFToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  return cookieValue;
}

function showToast(message, type = 'info') {
  // Create toast container if it doesn't exist
  let toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(toastContainer);
  }
  
  // Create toast element
  const toastId = 'toast-' + Date.now();
  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('id', toastId);
  
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">
        ${message}
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;
  
  toastContainer.appendChild(toast);
  
  // Initialize and show toast
  const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
  bsToast.show();
  
  // Remove toast after hiding
  toast.addEventListener('hidden.bs.toast', function () {
    toast.remove();
  });
}

// Export functions for use in other scripts
window.BRACULearningHub = {
  showToast,
  formatFileSize,
  getFileIcon,
  initializeTooltips,
  initializeFileUploads
};

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
  // Ctrl/Cmd + K for search
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    const searchInput = document.querySelector('#global-search');
    if (searchInput) {
      searchInput.focus();
    }
  }
  
  // Escape to clear search
  if (e.key === 'Escape') {
    const searchInput = document.querySelector('#global-search');
    if (searchInput && document.activeElement === searchInput) {
      searchInput.value = '';
      clearSearchResults();
    }
  }
});