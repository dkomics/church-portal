// Church Membership Directory JavaScript

class MembershipDirectory {
    constructor() {
        this.members = [];
        this.filteredMembers = [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.searchTerm = '';
        this.filters = {
            gender: '',
            ageCategory: '',
            membershipType: '',
            baptized: ''
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadMembers();
        this.setupAccessibility();
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                this.searchTerm = searchInput.value.toLowerCase();
                this.filterAndDisplay();
            }, 300));
        }

        // Filter functionality
        document.querySelectorAll('.filter-select').forEach(select => {
            select.addEventListener('change', (e) => {
                this.filters[e.target.dataset.filter] = e.target.value;
                this.filterAndDisplay();
            });
        });

        // Export functionality
        const exportBtn = document.getElementById('exportBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportToCSV());
        }

        // Modal close functionality
        const modal = document.getElementById('memberModal');
        const closeBtn = document.querySelector('.close-btn');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeModal());
        }
        
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    setupAccessibility() {
        // Add ARIA labels and descriptions
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.setAttribute('aria-label', 'Tafuta washirika');
            searchInput.setAttribute('aria-describedby', 'search-help');
        }

        // Add role and aria-live for dynamic content
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            tableContainer.setAttribute('role', 'region');
            tableContainer.setAttribute('aria-label', 'Jedwali la washirika');
        }

        const paginationInfo = document.querySelector('.pagination-info');
        if (paginationInfo) {
            paginationInfo.setAttribute('aria-live', 'polite');
        }
    }

    async loadMembers() {
        this.showLoading();
        
        try {
            const response = await fetch('/api/members/');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.members = data;
            this.filteredMembers = [...this.members];
            
            this.hideLoading();
            this.updateStatistics();
            this.displayMembers();
            this.setupTableSorting();
            
        } catch (error) {
            console.error('Failed to load members:', error);
            this.showError('Imeshindwa kupakia orodha ya washirika. Tafadhali jaribu tena.');
        }
    }

    showLoading() {
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            tableContainer.innerHTML = `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <p>Inapakia orodha ya washirika...</p>
                </div>
            `;
        }
    }

    hideLoading() {
        // Loading will be replaced by table content
    }

    showError(message) {
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            tableContainer.innerHTML = `
                <div class="error-message" role="alert">
                    <strong>Hitilafu:</strong> ${message}
                </div>
            `;
        }
    }

    updateStatistics() {
        const stats = {
            total: this.members.length,
            male: this.members.filter(m => m.gender === 'Male').length,
            female: this.members.filter(m => m.gender === 'Female').length,
            baptized: this.members.filter(m => m.baptized === 'Yes').length
        };

        // Update stat cards
        const totalStat = document.getElementById('totalMembers');
        const maleStat = document.getElementById('maleMembers');
        const femaleStat = document.getElementById('femaleMembers');
        const baptizedStat = document.getElementById('baptizedMembers');

        if (totalStat) totalStat.textContent = stats.total;
        if (maleStat) maleStat.textContent = stats.male;
        if (femaleStat) femaleStat.textContent = stats.female;
        if (baptizedStat) baptizedStat.textContent = stats.baptized;
    }

    filterAndDisplay() {
        this.filteredMembers = this.members.filter(member => {
            // Search filter
            const matchesSearch = !this.searchTerm || 
                member.full_name.toLowerCase().includes(this.searchTerm) ||
                member.emergency_phone.includes(this.searchTerm) ||
                member.membership_id.toString().includes(this.searchTerm);

            // Other filters
            const matchesGender = !this.filters.gender || member.gender === this.filters.gender;
            const matchesAge = !this.filters.ageCategory || member.age_category === this.filters.ageCategory;
            const matchesMembership = !this.filters.membershipType || member.membership_type === this.filters.membershipType;
            const matchesBaptized = !this.filters.baptized || member.baptized === this.filters.baptized;

            return matchesSearch && matchesGender && matchesAge && matchesMembership && matchesBaptized;
        });

        this.currentPage = 1; // Reset to first page when filtering
        this.displayMembers();
    }

    sortMembers(column) {
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }

        this.filteredMembers.sort((a, b) => {
            let aVal = a[column] || '';
            let bVal = b[column] || '';

            // Handle different data types
            if (column === 'membership_id') {
                aVal = parseInt(aVal);
                bVal = parseInt(bVal);
            } else if (column === 'registration_date') {
                aVal = new Date(aVal);
                bVal = new Date(bVal);
            } else {
                aVal = aVal.toString().toLowerCase();
                bVal = bVal.toString().toLowerCase();
            }

            if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        this.displayMembers();
        this.updateSortIndicators();
    }

    updateSortIndicators() {
        // Remove all sort classes
        document.querySelectorAll('.member-table th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });

        // Add current sort class
        if (this.sortColumn) {
            const th = document.querySelector(`[data-sort="${this.sortColumn}"]`);
            if (th) {
                th.classList.add(this.sortDirection === 'asc' ? 'sort-asc' : 'sort-desc');
            }
        }
    }

    setupTableSorting() {
        document.querySelectorAll('[data-sort]').forEach(th => {
            th.addEventListener('click', () => {
                const column = th.dataset.sort;
                this.sortMembers(column);
            });
            
            // Add keyboard support
            th.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const column = th.dataset.sort;
                    this.sortMembers(column);
                }
            });
            
            th.setAttribute('tabindex', '0');
            th.setAttribute('role', 'button');
            th.setAttribute('aria-label', `Panga kwa ${th.textContent}`);
        });
    }

    displayMembers() {
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageMembers = this.filteredMembers.slice(startIndex, endIndex);

        const tableContainer = document.querySelector('.table-container');
        if (!tableContainer) return;

        const tableHTML = `
            <table class="member-table" role="table">
                <thead>
                    <tr role="row">
                        <th data-sort="membership_id" class="sortable" tabindex="0" role="columnheader">ID</th>
                        <th data-sort="full_name" class="sortable" tabindex="0" role="columnheader">Jina Kamili</th>
                        <th data-sort="gender" class="sortable" tabindex="0" role="columnheader">Jinsia</th>
                        <th data-sort="age_category" class="sortable" tabindex="0" role="columnheader">Umri</th>
                        <th data-sort="emergency_phone" class="sortable" tabindex="0" role="columnheader">Simu ya Dharura</th>
                        <th data-sort="membership_type" class="sortable" tabindex="0" role="columnheader">Aina ya Ushirika</th>
                        <th data-sort="registration_date" class="sortable" tabindex="0" role="columnheader">Tarehe ya Usajili</th>
                        <th role="columnheader">Vitendo</th>
                    </tr>
                </thead>
                <tbody>
                    ${pageMembers.map(member => `
                        <tr role="row" data-member-id="${member.membership_id}">
                            <td role="cell">${member.membership_id}</td>
                            <td role="cell">${this.escapeHtml(member.full_name)}</td>
                            <td role="cell">${this.translateGender(member.gender)}</td>
                            <td role="cell">${member.age_category || '-'}</td>
                            <td role="cell">${member.emergency_phone}</td>
                            <td role="cell">${this.translateMembershipType(member.membership_type)}</td>
                            <td role="cell">${this.formatDate(member.registration_date)}</td>
                            <td role="cell">
                                <div class="member-actions">
                                    <button class="action-btn view-btn" 
                                            onclick="memberDirectory.showMemberDetails(${member.membership_id})"
                                            aria-label="Ona maelezo ya ${member.full_name}">
                                        Ona
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        tableContainer.innerHTML = tableHTML;
        this.setupTableSorting();
        this.updateSortIndicators();
        this.updatePagination();
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredMembers.length / this.itemsPerPage);
        const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
        const endItem = Math.min(this.currentPage * this.itemsPerPage, this.filteredMembers.length);

        // Update pagination info
        const paginationInfo = document.querySelector('.pagination-info');
        if (paginationInfo) {
            paginationInfo.textContent = `Inaonyesha ${startItem}-${endItem} ya ${this.filteredMembers.length} washirika`;
        }

        // Update pagination buttons
        const pagination = document.querySelector('.pagination');
        if (!pagination) return;

        let paginationHTML = `
            <button class="page-btn" ${this.currentPage === 1 ? 'disabled' : ''} 
                    onclick="memberDirectory.goToPage(${this.currentPage - 1})"
                    aria-label="Ukurasa wa awali">
                ← Awali
            </button>
        `;

        // Page numbers
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <button class="page-btn ${i === this.currentPage ? 'active' : ''}"
                        onclick="memberDirectory.goToPage(${i})"
                        aria-label="Ukurasa ${i}"
                        ${i === this.currentPage ? 'aria-current="page"' : ''}>
                    ${i}
                </button>
            `;
        }

        paginationHTML += `
            <button class="page-btn" ${this.currentPage === totalPages ? 'disabled' : ''} 
                    onclick="memberDirectory.goToPage(${this.currentPage + 1})"
                    aria-label="Ukurasa wa mwisho">
                Mwisho →
            </button>
        `;

        pagination.innerHTML = paginationHTML;
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.filteredMembers.length / this.itemsPerPage);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.displayMembers();
        }
    }

    showMemberDetails(memberId) {
        const member = this.members.find(m => m.membership_id === memberId);
        if (!member) return;

        const modal = document.getElementById('memberModal');
        const modalContent = document.querySelector('.member-details');
        
        if (!modal || !modalContent) return;

        modalContent.innerHTML = `
            <div class="detail-section">
                <h4>Taarifa za Kibinafsi</h4>
                <div class="detail-item">
                    <span class="detail-label">Jina Kamili:</span>
                    <span class="detail-value">${this.escapeHtml(member.full_name)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Jinsia:</span>
                    <span class="detail-value">${this.translateGender(member.gender)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Kundi la Umri:</span>
                    <span class="detail-value">${member.age_category || '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Tarehe ya Kuzaliwa:</span>
                    <span class="detail-value">${member.dob ? this.formatDate(member.dob) : '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Hali ya Ndoa:</span>
                    <span class="detail-value">${this.translateMaritalStatus(member.marital_status)}</span>
                </div>
            </div>
            
            <div class="detail-section">
                <h4>Taarifa za Mawasiliano</h4>
                <div class="detail-item">
                    <span class="detail-label">Namba ya Simu:</span>
                    <span class="detail-value">${member.phone || '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Barua Pepe:</span>
                    <span class="detail-value">${member.email || '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Anuani:</span>
                    <span class="detail-value">${this.escapeHtml(member.address)}</span>
                </div>
            </div>
            
            <div class="detail-section">
                <h4>Taarifa za Kiroho</h4>
                <div class="detail-item">
                    <span class="detail-label">Tarehe ya Kuokoka:</span>
                    <span class="detail-value">${member.salvation_date ? this.formatDate(member.salvation_date) : '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Amebatizwa:</span>
                    <span class="detail-value">${member.baptized === 'Yes' ? 'Ndio' : 'Hapana'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Tarehe ya Ubatizo:</span>
                    <span class="detail-value">${member.baptism_date ? this.formatDate(member.baptism_date) : '-'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Darasa la Ushirika:</span>
                    <span class="detail-value">${this.translateMembershipClass(member.membership_class)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Kanisa la Awali:</span>
                    <span class="detail-value">${member.previous_church || '-'}</span>
                </div>
            </div>
            
            <div class="detail-section">
                <h4>Mtu wa Dharura na Ushirika</h4>
                <div class="detail-item">
                    <span class="detail-label">Jina la Mtu wa Dharura:</span>
                    <span class="detail-value">${this.escapeHtml(member.emergency_name)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Mahusiano:</span>
                    <span class="detail-value">${this.escapeHtml(member.emergency_relation)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Simu ya Dharura:</span>
                    <span class="detail-value">${member.emergency_phone}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Aina ya Ushirika:</span>
                    <span class="detail-value">${this.translateMembershipType(member.membership_type)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Tarehe ya Usajili:</span>
                    <span class="detail-value">${this.formatDate(member.registration_date)}</span>
                </div>
            </div>
        `;

        modal.classList.add('show');
        
        // Focus management for accessibility
        const closeBtn = modal.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.focus();
        }
    }

    closeModal() {
        const modal = document.getElementById('memberModal');
        if (modal) {
            modal.classList.remove('show');
        }
    }

    exportToCSV() {
        const headers = [
            'ID', 'Jina Kamili', 'Jinsia', 'Kundi la Umri', 'Tarehe ya Kuzaliwa',
            'Hali ya Ndoa', 'Simu', 'Barua Pepe', 'Anuani', 'Tarehe ya Kuokoka',
            'Amebatizwa', 'Tarehe ya Ubatizo', 'Darasa la Ushirika', 'Kanisa la Awali',
            'Jina la Mtu wa Dharura', 'Mahusiano', 'Simu ya Dharura',
            'Aina ya Ushirika', 'Tarehe ya Usajili'
        ];

        const csvContent = [
            headers.join(','),
            ...this.filteredMembers.map(member => [
                member.membership_id,
                `"${member.full_name}"`,
                this.translateGender(member.gender),
                member.age_category || '',
                member.dob || '',
                this.translateMaritalStatus(member.marital_status),
                member.phone || '',
                member.email || '',
                `"${member.address}"`,
                member.salvation_date || '',
                member.baptized === 'Yes' ? 'Ndio' : 'Hapana',
                member.baptism_date || '',
                this.translateMembershipClass(member.membership_class),
                member.previous_church || '',
                `"${member.emergency_name}"`,
                `"${member.emergency_relation}"`,
                member.emergency_phone,
                this.translateMembershipType(member.membership_type),
                member.registration_date
            ].join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `orodha_ya_washirika_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // Utility functions
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('sw-KE');
    }

    translateGender(gender) {
        const translations = {
            'Male': 'Mwanaume',
            'Female': 'Mwanamke',
            'Prefer not to say': 'Sipendi kusema'
        };
        return translations[gender] || gender;
    }

    translateMaritalStatus(status) {
        const translations = {
            'Single': 'Bila ndoa',
            'Married': 'Kwenye ndoa',
            'Divorced': 'Talaka',
            'Widowed': 'Mjane'
        };
        return translations[status] || status || '-';
    }

    translateMembershipType(type) {
        const translations = {
            'New': 'Mshirika Mpya',
            'Transfer': 'Aliyehamia',
            'Returning': 'Anayerudi'
        };
        return translations[type] || type;
    }

    translateMembershipClass(membershipClass) {
        const translations = {
            'Yes': 'Ndio',
            'No': 'Hapana',
            'Not Yet': 'Bado'
        };
        return translations[membershipClass] || membershipClass || '-';
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize the directory when DOM is loaded
let memberDirectory;
document.addEventListener('DOMContentLoaded', () => {
    memberDirectory = new MembershipDirectory();
});

// Handle page visibility changes for performance
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && memberDirectory) {
        // Refresh data when page becomes visible (optional)
        // memberDirectory.loadMembers();
    }
});
