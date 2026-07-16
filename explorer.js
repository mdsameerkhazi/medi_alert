// explorer.js - Stitch Design Explorer Functionality

const screens = [
  { id: 'dashboard', name: 'Patient Dashboard', path: '/dashboard/code.html', img: '/dashboard/screen.png', category: 'Overview', icon: 'dashboard' },
  { id: 'caregiver_dashboard', name: 'Caregiver Dashboard', path: '/caregiver_dashboard/code.html', img: '/caregiver_dashboard/screen.png', category: 'Overview', icon: 'supervisor_account' },

  { id: 'login', name: 'Login Screen', path: '/login/code.html', img: '/login/screen.png', category: 'Authentication', icon: 'login' },
  { id: 'register', name: 'Registration Screen', path: '/register/code.html', img: '/register/screen.png', category: 'Authentication', icon: 'person_add' },
  { id: 'forgot_password', name: 'Forgot Password', path: '/forgot_password/code.html', img: '/forgot_password/screen.png', category: 'Authentication', icon: 'lock_reset' },
  { id: 'otp_verification', name: 'OTP Verification', path: '/otp_verification/code.html', img: '/otp_verification/screen.png', category: 'Authentication', icon: 'sms' },
  { id: 'auth_placeholder', name: 'Auth Placeholder', path: '/auth_placeholder/code.html', img: '/auth_placeholder/screen.png', category: 'Authentication', icon: 'security' },

  { id: 'settings', name: 'General Settings', path: '/settings/code.html', img: '/settings/screen.png', category: 'Settings & Management', icon: 'settings' },
  { id: 'theme_settings', name: 'Theme Settings', path: '/theme_settings/code.html', img: '/theme_settings/screen.png', category: 'Settings & Management', icon: 'palette' },
  { id: 'notification_settings', name: 'Notification Settings', path: '/notification_settings/code.html', img: '/notification_settings/screen.png', category: 'Settings & Management', icon: 'notifications_active' },
  { id: 'privacy_settings', name: 'Privacy Settings', path: '/privacy_settings/code.html', img: '/privacy_settings/screen.png', category: 'Settings & Management', icon: 'privacy_tip' },
  { id: 'user_profile', name: 'User Profile', path: '/user_profile/code.html', img: '/user_profile/screen.png', category: 'Settings & Management', icon: 'account_circle' },

  { id: 'medical_information', name: 'Medical Information', path: '/medical_information/code.html', img: '/medical_information/screen.png', category: 'Health Records & Info', icon: 'description' },
  { id: 'health_statistics', name: 'Health Statistics', path: '/health_statistics/code.html', img: '/health_statistics/screen.png', category: 'Health Records & Info', icon: 'bar_chart' },
  { id: 'medicine_details', name: 'Medicine Details', path: '/medicine_details/code.html', img: '/medicine_details/screen.png', category: 'Health Records & Info', icon: 'info', hidden: true },
  { id: 'medication_list', name: 'Medication List', path: '/medication_list/code.html', img: '/medication_list/screen.png', category: 'Health Records & Info', icon: 'list_alt' },
  { id: 'add_edit_medicine', name: 'Add/Edit Medicine', path: '/add_edit_medicine/code.html', img: '/add_edit_medicine/screen.png', category: 'Health Records & Info', icon: 'edit', hidden: true },
  { id: 'my_doctors', name: 'My Doctors', path: '/my_doctors/code.html', img: '/my_doctors/screen.png', category: 'Health Records & Info', icon: 'medical_services' },

  { id: 'emergency_contacts', name: 'Emergency Contacts', path: '/emergency_contacts/code.html', img: '/emergency_contacts/screen.png', category: 'Support & Actions', icon: 'contact_phone' },
  { id: 'emergency_sos', name: 'Emergency SOS', path: '/emergency_sos/code.html', img: '/emergency_sos/screen.png', category: 'Support & Actions', icon: 'emergency' },
  { id: 'notifications', name: 'Notification Center', path: '/notifications/code.html', img: '/notifications/screen.png', category: 'Support & Actions', icon: 'notifications' }
];

// State Management
let currentScreen = null;
let currentMode = 'live'; // 'live' | 'blueprint' | 'code'
let currentViewport = 'desktop'; // 'desktop' | 'tablet' | 'mobile'
let theme = localStorage.getItem('theme') || 'light';

// DOM Elements
const screenListContainer = document.getElementById('screen-list');
const searchInput = document.getElementById('search-input');
const totalScreensBadge = document.getElementById('total-screens');
const activeScreenTitle = document.getElementById('active-title');
const activeScreenPath = document.getElementById('active-path');
const newTabLink = document.getElementById('new-tab-link');

const btnLive = document.getElementById('btn-live');
const btnBlueprint = document.getElementById('btn-blueprint');
const btnCode = document.getElementById('btn-code');

const btnDesktop = document.getElementById('btn-desktop');
const btnTablet = document.getElementById('btn-tablet');
const btnMobile = document.getElementById('btn-mobile');
const viewportSelector = document.getElementById('viewport-selector');

const themeToggle = document.getElementById('theme-toggle');
const themeIcon = themeToggle.querySelector('.material-symbols-outlined');

const deviceWrapper = document.getElementById('device-wrapper');
const previewIframe = document.getElementById('preview-iframe');
const blueprintContainer = document.getElementById('blueprint-container');
const blueprintImage = document.getElementById('blueprint-image');
const codeContainer = document.getElementById('code-container');
const codeContent = document.getElementById('code-content');
const copyCodeBtn = document.getElementById('copy-code-btn');

// Initialize Theme
document.documentElement.setAttribute('data-theme', theme);
themeIcon.textContent = theme === 'dark' ? 'light_mode' : 'dark_mode';

themeToggle.addEventListener('click', () => {
  theme = theme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  themeIcon.textContent = theme === 'dark' ? 'light_mode' : 'dark_mode';
});

// Group Screens by Category
function getCategorizedScreens(filterText = '') {
  const groups = {};
  const query = filterText.toLowerCase().trim();

  screens.forEach(screen => {
    if (screen.hidden && !query) {
      return;
    }
    if (query && !screen.name.toLowerCase().includes(query) && !screen.category.toLowerCase().includes(query)) {
      return;
    }
    if (!groups[screen.category]) {
      groups[screen.category] = [];
    }
    groups[screen.category].push(screen);
  });

  return groups;
}

// Render Sidebar List
function renderSidebar(filterText = '') {
  screenListContainer.innerHTML = '';
  const categorized = getCategorizedScreens(filterText);
  let totalCount = 0;

  Object.keys(categorized).forEach(category => {
    const group = categorized[category];
    if (group.length === 0) return;

    totalCount += group.length;

    const groupDiv = document.createElement('div');
    groupDiv.className = 'category-group';

    const titleDiv = document.createElement('div');
    titleDiv.className = 'category-title';
    titleDiv.textContent = category;
    groupDiv.appendChild(titleDiv);

    group.forEach(screen => {
      const a = document.createElement('a');
      a.className = `screen-item ${currentScreen && currentScreen.id === screen.id ? 'active' : ''}`;
      a.href = `#${screen.id}`;
      a.innerHTML = `
        <span class="material-symbols-outlined item-icon">${screen.icon}</span>
        <span>${screen.name}</span>
        ${screen.name.includes('(Polished)') ? '<span class="badge-polished">pro</span>' : ''}
      `;
      a.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.hash = screen.id;
      });
      groupDiv.appendChild(a);
    });

    screenListContainer.appendChild(groupDiv);
  });

  totalScreensBadge.textContent = `${totalCount} screens`;
}

// Select Active Screen
function selectScreen(screenId) {
  const screen = screens.find(s => s.id === screenId) || screens[0];
  currentScreen = screen;
  
  // Highlight in sidebar
  const items = screenListContainer.querySelectorAll('.screen-item');
  items.forEach(item => {
    const isTarget = item.getAttribute('href') === `#${screen.id}`;
    item.classList.toggle('active', isTarget);
  });

  // Update Header UI
  activeScreenTitle.textContent = screen.name;
  activeScreenPath.textContent = screen.path;
  newTabLink.href = screen.path;

  // Load Iframe
  previewIframe.src = screen.path;

  // Load Blueprint
  if (screen.img) {
    blueprintImage.src = screen.img;
    blueprintImage.alt = `${screen.name} Blueprint Screenshot`;
    blueprintImage.style.display = 'block';
  } else {
    blueprintImage.style.display = 'none';
  }

  // Load Code Content
  loadCodeContent(screen.path);

  // Sync current mode visibility
  updateViewMode();
}

// Load Raw HTML for Code Viewer
async function loadCodeContent(path) {
  codeContent.textContent = 'Loading source code...';
  try {
    const response = await fetch(path);
    if (!response.ok) throw new Error('Failed to fetch code');
    const text = await response.text();
    codeContent.textContent = text;
  } catch (error) {
    codeContent.textContent = `Error loading source code: ${error.message}`;
  }
}

// Copy Code Button
copyCodeBtn.addEventListener('click', () => {
  navigator.clipboard.writeText(codeContent.textContent)
    .then(() => {
      const originalText = copyCodeBtn.innerHTML;
      copyCodeBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px;">check</span> Copied';
      setTimeout(() => {
        copyCodeBtn.innerHTML = originalText;
      }, 2000);
    })
    .catch(err => {
      alert('Failed to copy text: ' + err);
    });
});

// Update View Mode Visibility (Live vs Blueprint vs Code)
function updateViewMode() {
  // Reset
  deviceWrapper.style.display = 'none';
  blueprintContainer.style.display = 'none';
  codeContainer.style.display = 'none';
  viewportSelector.style.display = 'none';

  // Toggle active buttons
  btnLive.classList.toggle('active', currentMode === 'live');
  btnBlueprint.classList.toggle('active', currentMode === 'blueprint');
  btnCode.classList.toggle('active', currentMode === 'code');

  if (currentMode === 'live') {
    deviceWrapper.style.display = 'flex';
    viewportSelector.style.display = 'flex';
  } else if (currentMode === 'blueprint') {
    blueprintContainer.style.display = 'flex';
  } else if (currentMode === 'code') {
    codeContainer.style.display = 'block';
  }
}

// View Mode Buttons Listeners
btnLive.addEventListener('click', () => { currentMode = 'live'; updateViewMode(); });
btnBlueprint.addEventListener('click', () => { currentMode = 'blueprint'; updateViewMode(); });
btnCode.addEventListener('click', () => { currentMode = 'code'; updateViewMode(); });

// Viewport Switching (Desktop/Tablet/Mobile)
function setViewport(mode) {
  currentViewport = mode;
  
  btnDesktop.classList.toggle('active', mode === 'desktop');
  btnTablet.classList.toggle('active', mode === 'tablet');
  btnMobile.classList.toggle('active', mode === 'mobile');

  deviceWrapper.className = `device-wrapper mode-${mode}`;
}

btnDesktop.addEventListener('click', () => setViewport('desktop'));
btnTablet.addEventListener('click', () => setViewport('tablet'));
btnMobile.addEventListener('click', () => setViewport('mobile'));

// Handle Hash Routing
function handleRouting() {
  const hash = window.location.hash.substring(1);
  if (hash) {
    selectScreen(hash);
  } else {
    selectScreen('dashboard');
  }
}

// Search Functionality
searchInput.addEventListener('input', (e) => {
  renderSidebar(e.target.value);
});

// App Startup
window.addEventListener('hashchange', handleRouting);

// Start
renderSidebar();
handleRouting();
setViewport('desktop');
updateViewMode();
