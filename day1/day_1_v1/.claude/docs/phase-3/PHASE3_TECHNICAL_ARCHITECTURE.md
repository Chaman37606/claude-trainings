# Phase 3 Technical Architecture

**Document:** Phase 3 Technical Architecture & Implementation Guide  
**Date:** 2026-08-29  
**Version:** 1.0

---

## 1. Overall Architecture

### Single-File Constraint Strategy

Phase 3 will remain a single HTML file (~6000-7000 lines) by:
- Adding 5 new manager objects
- Extending existing CSS (not modifying)
- Keeping all logic in JavaScript
- Using localStorage for all data persistence
- Maintaining modular code organization

### Code Organization

```
alcoa-plus-tool.html (6000-7000 lines)
├── HTML (20%)
│   ├── Existing 8 tabs (unchanged)
│   ├── New auth UI (login/register modal)
│   ├── New admin panels (user mgmt, API config, branding)
│   └── New elements (language switcher, branding preview)
├── CSS (15%)
│   ├── Existing styles (unchanged)
│   ├── New auth styling (~200 lines)
│   ├── New admin panel styling (~300 lines)
│   └── Responsive adjustments (~100 lines)
└── JavaScript (65%)
    ├── Existing Phase 1-2 code (~2000 lines, unchanged)
    ├── Phase 3 Managers (~3500 lines)
    │   ├── authManager (~400 lines)
    │   ├── userManager (~600 lines)
    │   ├── rbacManager (~500 lines)
    │   ├── languageManager (~700 lines)
    │   ├── brandingManager (~400 lines)
    │   └── apiManager (~500 lines)
    └── Integration & Utilities (~300 lines)
```

### Manager Objects Pattern

```javascript
// Consistent pattern across all managers
const [feature]Manager = {
  // Configuration/state
  config: { /* settings */ },
  data: { /* runtime data */ },
  
  // Initialization
  init: function() { /* setup */ },
  
  // Core functions
  create: function() { /* ... */ },
  read: function() { /* ... */ },
  update: function() { /* ... */ },
  delete: function() { /* ... */ },
  
  // Persistence
  save: function() { /* localStorage */ },
  load: function() { /* localStorage */ },
  
  // UI
  render: function() { /* DOM updates */ },
  
  // Error handling
  handleError: function(err) { /* ... */ }
}
```

---

## 2. Feature 1: User Account System

### Architecture

```
Authentication Flow:
┌─────────────┐
│   Login UI  │
└──────┬──────┘
       │ Submit credentials
       ▼
┌──────────────────────────┐
│  userManager.login()     │
│  - Validate input        │
│  - Find user in storage  │
│  - Verify password hash  │
└──────┬───────────────────┘
       │
       ├─ Success: Create session token
       │            Store session
       │            Update currentUser
       │            Redirect to dashboard
       │
       └─ Failure: Show error
                   Increment failed attempts
                   Check rate limit
```

### Implementation

**userManager Object (~600 lines):**

```javascript
const userManager = {
  config: {
    passwordMinLength: 8,
    sessionTimeout: 86400000,  // 24 hours
    lockoutThreshold: 5,
    lockoutDuration: 900000    // 15 minutes
  },
  
  users: [],  // Loaded from localStorage on init
  failedAttempts: {},  // Track failed login attempts
  
  init: function() {
    this.users = storageManager.load('users') || [];
    this.validateSessions();
  },
  
  register: function(email, password, name, org) {
    // Validation
    if (!this.validateEmail(email)) throw new Error('Invalid email');
    if (!this.validatePassword(password)) throw new Error('Password too weak');
    if (this.findByEmail(email)) throw new Error('Email exists');
    
    // Create user
    const user = {
      id: this.generateUserId(),
      email: email,
      passwordHash: this.hashPassword(password),
      name: name,
      organization: org,
      role: 'viewer',  // Default role
      createdAt: Date.now(),
      lastLogin: null,
      preferences: {
        language: 'en',
        timezone: 'UTC'
      }
    };
    
    this.users.push(user);
    this.save();
    return user;
  },
  
  login: function(email, password) {
    // Rate limiting
    if (this.isLockedOut(email)) {
      throw new Error('Account locked. Try again later.');
    }
    
    // Find user
    const user = this.findByEmail(email);
    if (!user) {
      this.recordFailedAttempt(email);
      throw new Error('Invalid credentials');
    }
    
    // Verify password
    if (!this.verifyPassword(password, user.passwordHash)) {
      this.recordFailedAttempt(email);
      throw new Error('Invalid credentials');
    }
    
    // Reset failed attempts
    this.failedAttempts[email] = 0;
    
    // Create session
    const session = {
      userId: user.id,
      token: this.generateToken(),
      createdAt: Date.now(),
      expiresAt: Date.now() + this.config.sessionTimeout,
      lastActivity: Date.now()
    };
    
    // Store session
    authManager.setSession(session);
    user.lastLogin = Date.now();
    this.save();
    
    // Record in audit log
    auditManager.log({
      userId: user.id,
      action: 'LOGIN',
      resource: 'auth',
      timestamp: Date.now(),
      success: true
    });
    
    return { user, session };
  },
  
  logout: function() {
    const currentUser = authManager.getCurrentUser();
    if (!currentUser) return;
    
    auditManager.log({
      userId: currentUser.id,
      action: 'LOGOUT',
      resource: 'auth',
      timestamp: Date.now()
    });
    
    authManager.clearSession();
  },
  
  // Password operations
  hashPassword: function(password) {
    // Simple hash for Phase 3 (Phase 4: use bcrypt)
    // This is a placeholder - would use proper hashing in production
    return 'hashed_' + btoa(password + 'salt_' + password.length);
  },
  
  verifyPassword: function(password, hash) {
    return this.hashPassword(password) === hash;
  },
  
  validatePassword: function(password) {
    // 8+ chars, mixed case, at least one number
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    return regex.test(password);
  },
  
  validateEmail: function(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  },
  
  // Helper functions
  findByEmail: function(email) {
    return this.users.find(u => u.email.toLowerCase() === email.toLowerCase());
  },
  
  findById: function(userId) {
    return this.users.find(u => u.id === userId);
  },
  
  generateUserId: function() {
    return 'user-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
  },
  
  generateToken: function() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let token = '';
    for (let i = 0; i < 32; i++) {
      token += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return token;
  },
  
  // Rate limiting
  recordFailedAttempt: function(email) {
    this.failedAttempts[email] = (this.failedAttempts[email] || 0) + 1;
  },
  
  isLockedOut: function(email) {
    const attempts = this.failedAttempts[email] || 0;
    return attempts >= this.config.lockoutThreshold;
  },
  
  // Persistence
  save: function() {
    storageManager.save('users', this.users);
  },
  
  load: function() {
    this.users = storageManager.load('users') || [];
  }
};
```

**authManager Object (~400 lines):**

```javascript
const authManager = {
  currentSession: null,
  currentUser: null,
  
  init: function() {
    // Restore session from localStorage
    const session = storageManager.load('session');
    const user = storageManager.load('currentUser');
    
    if (session && this.isSessionValid(session)) {
      this.currentSession = session;
      this.currentUser = user;
    } else {
      this.clearSession();
    }
  },
  
  setSession: function(session) {
    this.currentSession = session;
    this.currentUser = userManager.findById(session.userId);
    storageManager.save('session', session);
    storageManager.save('currentUser', this.currentUser);
  },
  
  clearSession: function() {
    this.currentSession = null;
    this.currentUser = null;
    storageManager.clear('session');
    storageManager.clear('currentUser');
  },
  
  getCurrentUser: function() {
    return this.currentUser;
  },
  
  isAuthenticated: function() {
    return this.currentSession && this.isSessionValid(this.currentSession);
  },
  
  isSessionValid: function(session) {
    if (!session || !session.expiresAt) return false;
    return Date.now() < session.expiresAt;
  },
  
  validateToken: function(token) {
    if (!this.currentSession) return false;
    return this.currentSession.token === token;
  },
  
  checkAuthentication: function() {
    if (!this.isAuthenticated()) {
      window.location.hash = '#auth';
      throw new Error('Not authenticated');
    }
  },
  
  logout: function() {
    userManager.logout();
    this.clearSession();
    window.location.hash = '#auth';
  }
};
```

### UI Components

**Login/Registration Modal:**
- Overlay modal on page load if not authenticated
- Two tabs: Login and Register
- Email/password fields with validation
- Show password toggle
- Forgot password link
- Error messages
- Loading states

**Session Timeout:**
- Warn user at 5-minute mark
- Auto-logout at 24 hours
- Allow session extension on activity
- Show countdown on warning

---

## 3. Feature 2: Role-Based Access Control

### Architecture

```
Permission Check Flow:
┌────────────────────────────────┐
│ Feature Needs Permission Check │
└────────────┬───────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ rbacManager.isAuthorized(action)     │
│ - Get current user role              │
│ - Load role permissions              │
│ - Check if permission granted        │
└────────┬─────────────────────────────┘
         │
         ├─ Granted: Continue
         │
         └─ Denied: Audit log + Error
```

### Implementation

**rbacManager Object (~500 lines):**

```javascript
const rbacManager = {
  roles: {
    administrator: {
      name: 'Administrator',
      permissions: ['*'],
      color: '#dc3545'
    },
    manager: {
      name: 'Manager',
      permissions: [
        'dashboard:view', 'dashboard:filter',
        'export:csv', 'export:json', 'export:html', 'export:pdf',
        'report:view', 'report:export',
        'quiz:take', 'quiz:view-results',
        'principles:view', 'resources:view',
        'progress:view'
      ],
      color: '#667eea'
    },
    auditor: {
      name: 'Auditor',
      permissions: [
        'audit:view', 'audit:read',
        'compliance:view', 'compliance:read',
        'dashboard:view', 'dashboard:filter'
      ],
      color: '#28a745'
    },
    trainer: {
      name: 'Trainer',
      permissions: [
        'quiz:view', 'quiz:create', 'quiz:edit', 'quiz:manage',
        'training:view', 'training:manage',
        'assessment:view', 'assessment:administer',
        'quiz:take'
      ],
      color: '#ffc107'
    },
    viewer: {
      name: 'Viewer',
      permissions: [
        'principles:view', 'resources:view',
        'overview:view', 'quiz:take',
        'profile:view-own'
      ],
      color: '#999999'
    }
  },
  
  init: function() {
    // Load role permissions from storage or defaults
    this.roles = storageManager.load('roles') || this.roles;
  },
  
  isAuthorized: function(resource, action) {
    const user = authManager.getCurrentUser();
    if (!user) return false;
    
    const role = this.roles[user.role];
    if (!role) return false;
    
    // Admin has all permissions
    if (role.permissions.includes('*')) return true;
    
    // Check specific permission
    const permission = resource + ':' + action;
    return role.permissions.includes(permission) ||
           role.permissions.includes(resource + ':*');
  },
  
  canViewDashboard: function() {
    return this.isAuthorized('dashboard', 'view');
  },
  
  canExport: function(format) {
    return this.isAuthorized('export', format || '*');
  },
  
  canManageUsers: function() {
    return this.isAuthorized('users', 'manage');
  },
  
  canConfigureAPI: function() {
    return this.isAuthorized('api', 'configure');
  },
  
  canCustomizeBranding: function() {
    return this.isAuthorized('branding', 'customize');
  },
  
  canManageQuiz: function() {
    return this.isAuthorized('quiz', 'manage');
  },
  
  canViewAuditLog: function() {
    return this.isAuthorized('audit', 'view');
  },
  
  // Enforce access (throw error if unauthorized)
  enforceAccess: function(resource, action) {
    if (!this.isAuthorized(resource, action)) {
      const user = authManager.getCurrentUser();
      auditManager.log({
        userId: user?.id,
        action: 'ACCESS_DENIED',
        resource: resource,
        details: action,
        timestamp: Date.now()
      });
      throw new Error('Access denied: ' + resource + ':' + action);
    }
  },
  
  // Restrict UI element
  enforceUIElement: function(element, resource, action) {
    if (!this.isAuthorized(resource, action)) {
      element.style.display = 'none';
      element.disabled = true;
    }
  },
  
  // Get all permissions for current user
  getCurrentUserPermissions: function() {
    const user = authManager.getCurrentUser();
    if (!user) return [];
    return this.roles[user.role]?.permissions || [];
  },
  
  // Assign role to user
  assignRole: function(userId, roleName) {
    this.enforceAccess('users', 'manage');
    
    if (!this.roles[roleName]) {
      throw new Error('Invalid role: ' + roleName);
    }
    
    const user = userManager.findById(userId);
    if (!user) throw new Error('User not found');
    
    user.role = roleName;
    userManager.save();
    
    auditManager.log({
      userId: authManager.getCurrentUser().id,
      action: 'ASSIGN_ROLE',
      resource: 'user',
      details: { userId, roleName },
      timestamp: Date.now()
    });
  }
};
```

### UI Integration

**Admin Panel - User Management:**
- List all users with current roles
- Assign/change roles via dropdown
- Delete users (admin only)
- Reset passwords (admin only)
- View user creation date
- View last login
- Filter by role

---

## 4. Feature 3: Multi-Language Support

### Implementation

**languageManager Object (~700 lines):**

```javascript
const languageManager = {
  currentLanguage: 'en',
  
  translations: {
    en: {
      common: {
        yes: 'Yes',
        no: 'No',
        save: 'Save',
        cancel: 'Cancel',
        close: 'Close',
        loading: 'Loading...',
        error: 'Error',
        success: 'Success'
      },
      auth: {
        login: 'Login',
        register: 'Register',
        email: 'Email Address',
        password: 'Password',
        name: 'Full Name',
        organization: 'Organization',
        forgotPassword: 'Forgot Password?',
        createAccount: 'Create New Account',
        loginError: 'Invalid email or password',
        registerError: 'Registration failed',
        passwordWeak: 'Password must be at least 8 characters with uppercase, lowercase, and numbers'
      },
      dashboard: {
        title: 'Dashboard',
        overallCompliance: 'Overall Compliance',
        systemsAudited: 'Systems Audited',
        criticalFindings: 'Critical Findings',
        personnelTrained: 'Personnel Trained',
        selectScenario: 'Select Test Scenario',
        selectPrinciple: 'Select Principle Focus',
        principleCompliance: 'ALCOA+ Principle Compliance'
      },
      // ... 100+ translation keys for all content
    },
    es: {
      // Spanish translations
    },
    de: {
      // German translations
    },
    fr: {
      // French translations
    },
    zh: {
      // Chinese translations
    },
    ja: {
      // Japanese translations
    }
  },
  
  init: function() {
    this.currentLanguage = storageManager.load('language') || 'en';
    this.applyLanguage();
  },
  
  t: function(key, params) {
    // Usage: languageManager.t('auth.login')
    // Usage with params: languageManager.t('greeting', {name: 'John'})
    
    const keys = key.split('.');
    let value = this.translations[this.currentLanguage];
    
    for (const k of keys) {
      value = value[k];
      if (!value) return key; // Return key if translation not found
    }
    
    // Replace parameters
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        value = value.replace('{{' + k + '}}', v);
      }
    }
    
    return value;
  },
  
  setLanguage: function(code) {
    if (!this.translations[code]) {
      console.warn('Language not supported:', code);
      return false;
    }
    
    this.currentLanguage = code;
    storageManager.save('language', code);
    this.applyLanguage();
    
    // Trigger re-render
    this.updateDOM();
    
    return true;
  },
  
  getLanguages: function() {
    return Object.keys(this.translations).map(code => ({
      code: code,
      name: this.t('language.name', { code }),
      flag: this.getFlagEmoji(code)
    }));
  },
  
  getFlagEmoji: function(code) {
    const flags = {
      en: '🇺🇸',
      es: '🇪🇸',
      de: '🇩🇪',
      fr: '🇫🇷',
      zh: '🇨🇳',
      ja: '🇯🇵'
    };
    return flags[code] || '';
  },
  
  formatDate: function(date) {
    const formats = {
      en: new Intl.DateTimeFormat('en-US', { 
        year: 'numeric', month: '2-digit', day: '2-digit' 
      }),
      es: new Intl.DateTimeFormat('es-ES', { 
        year: 'numeric', month: '2-digit', day: '2-digit' 
      }),
      de: new Intl.DateTimeFormat('de-DE', { 
        year: 'numeric', month: '2-digit', day: '2-digit' 
      }),
      // ... other locales
    };
    
    return formats[this.currentLanguage]?.format(date) || 
           new Date(date).toLocaleDateString();
  },
  
  formatNumber: function(num) {
    const formats = {
      en: new Intl.NumberFormat('en-US'),
      es: new Intl.NumberFormat('es-ES'),
      de: new Intl.NumberFormat('de-DE'),
      // ... other locales
    };
    
    return formats[this.currentLanguage]?.format(num) || num.toString();
  },
  
  formatCurrency: function(num, currency = 'USD') {
    const formats = {
      en: new Intl.NumberFormat('en-US', { 
        style: 'currency', currency 
      }),
      es: new Intl.NumberFormat('es-ES', { 
        style: 'currency', currency 
      }),
      // ... other locales
    };
    
    return formats[this.currentLanguage]?.format(num) || '$' + num;
  },
  
  // Update all UI strings
  updateDOM: function() {
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (el.tagName === 'INPUT' && el.type === 'placeholder') {
        el.placeholder = this.t(key);
      } else {
        el.textContent = this.t(key);
      }
    });
    
    // Update dynamic content
    this.updateDashboard();
    this.updatePrinciples();
    this.updateQuiz();
  },
  
  updateDashboard: function() {
    // Update dashboard strings
    document.querySelectorAll('.kpi-label').forEach((el, idx) => {
      const labels = ['common.overallCompliance', 'common.systemsAudited', 
                     'common.criticalFindings', 'common.personnelTrained'];
      el.textContent = this.t(labels[idx] || labels[0]);
    });
  },
  
  updatePrinciples: function() {
    // Update principle names and descriptions
    // Iterate through principle cards and update text
  },
  
  updateQuiz: function() {
    // Update quiz questions and options
  },
  
  applyLanguage: function() {
    // Set HTML lang attribute
    document.documentElement.lang = this.currentLanguage;
    
    // Update DOM
    this.updateDOM();
  }
};
```

### HTML Integration

Mark all user-facing strings with `data-i18n` attribute:

```html
<h1 data-i18n="header.title">ALCOA+ Data Integrity Framework</h1>
<input type="text" data-i18n="auth.email" placeholder="Email Address">
<button data-i18n="auth.login">Login</button>
```

---

## 5. Feature 4: Custom Branding

### Implementation

**brandingManager Object (~400 lines):**

```javascript
const brandingManager = {
  config: {
    organizationName: 'Eli Lilly',
    logoUrl: null,
    colors: {
      primary: '#667eea',
      secondary: '#764ba2',
      success: '#28a745',
      warning: '#ffc107',
      danger: '#dc3545'
    },
    fonts: {
      heading: "'Segoe UI', Arial, sans-serif",
      body: "'Segoe UI', Arial, sans-serif"
    },
    customText: {
      organizationName: 'Eli Lilly',
      headerTitle: 'ALCOA+ Data Integrity Framework',
      headerSubtitle: 'Eli Lilly Operations - Ensuring Quality & Compliance',
      footerText: 'For questions, contact your Quality Assurance department'
    }
  },
  
  init: function() {
    this.config = storageManager.load('brandingConfig') || this.config;
    this.applyBranding();
  },
  
  uploadLogo: function(file) {
    if (file.size > 500000) { // 500KB
      throw new Error('Logo file too large (max 500KB)');
    }
    
    if (!file.type.startsWith('image/')) {
      throw new Error('File must be an image');
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
      this.config.logoUrl = e.target.result;
      this.applyBranding();
      this.save();
    };
    reader.readAsDataURL(file);
  },
  
  setColors: function(colorObj) {
    this.config.colors = { ...this.config.colors, ...colorObj };
    this.applyBranding();
    this.save();
  },
  
  setFonts: function(fontObj) {
    this.config.fonts = { ...this.config.fonts, ...fontObj };
    this.applyBranding();
    this.save();
  },
  
  setCustomText: function(textObj) {
    this.config.customText = { ...this.config.customText, ...textObj };
    this.updateText();
    this.save();
  },
  
  applyBranding: function() {
    // Apply colors via CSS variables
    const root = document.documentElement;
    root.style.setProperty('--primary-color', this.config.colors.primary);
    root.style.setProperty('--secondary-color', this.config.colors.secondary);
    root.style.setProperty('--success-color', this.config.colors.success);
    root.style.setProperty('--warning-color', this.config.colors.warning);
    root.style.setProperty('--danger-color', this.config.colors.danger);
    
    // Apply fonts
    root.style.setProperty('--font-heading', this.config.fonts.heading);
    root.style.setProperty('--font-body', this.config.fonts.body);
    
    // Apply logo
    this.updateLogo();
    
    // Apply text
    this.updateText();
  },
  
  updateLogo: function() {
    if (this.config.logoUrl) {
      const logo = document.querySelector('.header-logo');
      if (logo) {
        logo.src = this.config.logoUrl;
        logo.style.display = 'block';
      }
    }
  },
  
  updateText: function() {
    // Update header title
    document.querySelector('h1').textContent = 
      this.config.customText.headerTitle;
    
    // Update header subtitle
    document.querySelector('.subtitle').textContent = 
      this.config.customText.headerSubtitle;
    
    // Update footer
    document.querySelector('.footer p').textContent = 
      this.config.customText.footerText;
  },
  
  exportBranding: function() {
    const json = JSON.stringify(this.config, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'branding-config.json';
    a.click();
  },
  
  importBranding: function(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const config = JSON.parse(e.target.result);
        this.config = config;
        this.applyBranding();
        this.save();
        alert('Branding imported successfully');
      } catch (err) {
        alert('Error importing branding: ' + err.message);
      }
    };
    reader.readAsText(file);
  },
  
  save: function() {
    storageManager.save('brandingConfig', this.config);
  }
};
```

---

## 6. Feature 5: API Integration

### Implementation

**apiManager Object (~500 lines):**

```javascript
const apiManager = {
  endpoints: [],
  syncStatus: {},
  cache: {},
  
  init: function() {
    this.endpoints = storageManager.load('apiEndpoints') || [];
    this.syncStatus = storageManager.load('syncStatus') || {};
    this.setupAutoSync();
  },
  
  configureEndpoint: function(config) {
    // Validate configuration
    if (!config.name || !config.baseUrl || !config.endpoint) {
      throw new Error('Missing required fields');
    }
    
    // Encrypt credentials
    const encrypted = {
      ...config,
      token: this.encryptToken(config.token),
      credentials: this.encryptCredentials(config.credentials)
    };
    
    // Check if updating existing
    const existing = this.endpoints.find(e => e.id === config.id);
    if (existing) {
      Object.assign(existing, encrypted);
    } else {
      encrypted.id = this.generateEndpointId();
      this.endpoints.push(encrypted);
    }
    
    this.save();
    
    auditManager.log({
      userId: authManager.getCurrentUser().id,
      action: 'CONFIGURE_API',
      resource: 'api',
      details: config.name,
      timestamp: Date.now()
    });
    
    return encrypted;
  },
  
  testConnection: function(endpointId) {
    return new Promise((resolve, reject) => {
      const endpoint = this.endpoints.find(e => e.id === endpointId);
      if (!endpoint) reject(new Error('Endpoint not found'));
      
      const headers = {
        'Content-Type': 'application/json',
        ...endpoint.headers
      };
      
      if (endpoint.authentication === 'bearer') {
        headers['Authorization'] = 'Bearer ' + this.decryptToken(endpoint.token);
      }
      
      fetch(endpoint.baseUrl + endpoint.endpoint, {
        method: endpoint.method || 'GET',
        headers,
        timeout: endpoint.timeout || 5000
      })
      .then(response => {
        if (response.ok) {
          resolve({ success: true, status: response.status });
        } else {
          reject(new Error('HTTP ' + response.status));
        }
      })
      .catch(err => reject(err));
    });
  },
  
  syncData: function(endpointId) {
    const endpoint = this.endpoints.find(e => e.id === endpointId);
    if (!endpoint) throw new Error('Endpoint not found');
    
    // Mark as syncing
    this.syncStatus[endpointId] = { 
      syncing: true, 
      startTime: Date.now() 
    };
    
    return this.fetchData(endpoint)
      .then(data => {
        // Validate and transform data
        const transformed = this.transformData(endpoint, data);
        
        // Cache the data
        this.cache[endpointId] = {
          data: transformed,
          timestamp: Date.now(),
          ttl: endpoint.cacheTTL || 3600000
        };
        
        // Update status
        this.syncStatus[endpointId] = {
          syncing: false,
          success: true,
          lastSync: Date.now(),
          rowCount: Array.isArray(transformed) ? transformed.length : 1
        };
        
        this.save();
        
        auditManager.log({
          userId: authManager.getCurrentUser().id,
          action: 'API_SYNC',
          resource: 'api',
          details: endpoint.name,
          timestamp: Date.now(),
          success: true
        });
        
        return transformed;
      })
      .catch(err => {
        this.syncStatus[endpointId] = {
          syncing: false,
          success: false,
          error: err.message,
          lastSync: Date.now()
        };
        
        auditManager.log({
          userId: authManager.getCurrentUser().id,
          action: 'API_SYNC_FAILED',
          resource: 'api',
          details: endpoint.name,
          error: err.message,
          timestamp: Date.now()
        });
        
        throw err;
      });
  },
  
  fetchData: function(endpoint) {
    const headers = { ...endpoint.headers };
    if (endpoint.authentication === 'bearer') {
      headers['Authorization'] = 'Bearer ' + this.decryptToken(endpoint.token);
    }
    
    return fetch(endpoint.baseUrl + endpoint.endpoint, {
      method: endpoint.method || 'GET',
      headers
    })
    .then(response => {
      if (!response.ok) throw new Error('API error: ' + response.status);
      return response.json();
    });
  },
  
  transformData: function(endpoint, data) {
    // Map API response to internal format based on system type
    switch (endpoint.system) {
      case 'lims':
        return this.transformLIMSData(data);
      case 'erp':
        return this.transformERPData(data);
      case 'audit':
        return this.transformAuditData(data);
      default:
        return data;
    }
  },
  
  transformLIMSData: function(data) {
    // Transform LIMS data to internal format
    return data;  // Placeholder
  },
  
  transformERPData: function(data) {
    // Transform ERP data to internal format
    return data;  // Placeholder
  },
  
  transformAuditData: function(data) {
    // Transform audit data to internal format
    return data;  // Placeholder
  },
  
  getCachedData: function(endpointId) {
    const cached = this.cache[endpointId];
    if (!cached) return null;
    
    // Check if cache is still valid
    if (Date.now() - cached.timestamp > cached.ttl) {
      delete this.cache[endpointId];
      return null;
    }
    
    return cached.data;
  },
  
  getStatus: function(endpointId) {
    return this.syncStatus[endpointId] || {};
  },
  
  setupAutoSync: function() {
    setInterval(() => {
      this.endpoints.forEach(endpoint => {
        if (endpoint.enabled && endpoint.syncFrequency === 'hourly') {
          const status = this.syncStatus[endpoint.id];
          if (!status || Date.now() - status.lastSync > 3600000) {
            this.syncData(endpoint.id).catch(err => {
              console.error('Auto-sync failed:', err);
            });
          }
        }
      });
    }, 60000); // Check every minute
  },
  
  // Encryption helpers
  encryptToken: function(token) {
    // Simple encryption (Phase 4: use crypto)
    return 'encrypted_' + btoa(token);
  },
  
  decryptToken: function(encrypted) {
    return atob(encrypted.replace('encrypted_', ''));
  },
  
  encryptCredentials: function(creds) {
    return JSON.stringify(creds);  // Placeholder
  },
  
  generateEndpointId: function() {
    return 'endpoint-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
  },
  
  save: function() {
    storageManager.save('apiEndpoints', this.endpoints);
    storageManager.save('syncStatus', this.syncStatus);
  }
};
```

---

## 7. Integration Points

### Initialization Order

```javascript
// On page load
window.addEventListener('load', function() {
  // 1. Initialize storage
  storageManager.init?.();
  
  // 2. Initialize auth
  authManager.init();
  
  // 3. Check authentication
  if (!authManager.isAuthenticated()) {
    showAuthUI();
    return;
  }
  
  // 4. Initialize Phase 1-2 systems
  searchManager.buildIndex();
  progressTracker.init();
  metricsEngine.checkCompliance();
  
  // 5. Initialize Phase 3 systems
  userManager.init();
  rbacManager.init();
  languageManager.init();
  brandingManager.init();
  apiManager.init();
  auditManager.init();
  
  // 6. Apply access control
  applyAccessControl();
  
  // 7. Show main UI
  showMainUI();
});
```

### Audit Manager

```javascript
const auditManager = {
  logs: [],
  
  init: function() {
    this.logs = storageManager.load('auditLog') || [];
  },
  
  log: function(entry) {
    const log = {
      id: 'log-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
      timestamp: entry.timestamp || Date.now(),
      userId: entry.userId,
      action: entry.action,
      resource: entry.resource,
      details: entry.details || null,
      success: entry.success !== false,
      error: entry.error || null
    };
    
    this.logs.push(log);
    
    // Keep only last 500 entries
    if (this.logs.length > 500) {
      this.logs = this.logs.slice(-500);
    }
    
    this.save();
  },
  
  getLogs: function(filters = {}) {
    let filtered = this.logs;
    
    if (filters.userId) {
      filtered = filtered.filter(l => l.userId === filters.userId);
    }
    if (filters.action) {
      filtered = filtered.filter(l => l.action === filters.action);
    }
    if (filters.resource) {
      filtered = filtered.filter(l => l.resource === filters.resource);
    }
    
    return filtered;
  },
  
  save: function() {
    storageManager.save('auditLog', this.logs);
  }
};
```

---

## 8. Security Implementation

### Password Security

```javascript
// Hash function (Phase 3 - simple, Phase 4 - bcrypt)
function hashPassword(password) {
  const salt = Math.random().toString(36).substring(2);
  const hash = btoa(password + salt);
  return hash + ':' + salt;
}

function verifyPassword(password, stored) {
  const [hash, salt] = stored.split(':');
  return btoa(password + salt) === hash;
}
```

### Token Generation

```javascript
function generateSecureToken(length = 32) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let token = '';
  const values = new Uint32Array(length);
  crypto.getRandomValues(values);
  values.forEach(v => {
    token += chars[v % chars.length];
  });
  return token;
}
```

---

## 9. CSS Changes

New CSS classes (~400 lines):

```css
/* Auth UI */
.auth-modal { ... }
.login-form { ... }
.register-form { ... }
.password-strength { ... }

/* Admin Panels */
.admin-panel { ... }
.user-management { ... }
.api-configuration { ... }
.branding-customization { ... }

/* Language Switcher */
.language-selector { ... }
.language-option { ... }

/* Branding Preview */
.branding-preview { ... }
.color-picker { ... }
.font-selector { ... }

/* Responsive */
@media (max-width: 768px) { ... }
@media (max-width: 480px) { ... }
```

---

## 10. Performance Optimization

### Lazy Loading

```javascript
// Load managers on demand
const lazyManagers = {
  apiManager: false,
  brandingManager: false
};

function getManager(name) {
  if (!lazyManagers[name]) {
    // Initialize on first use
    window[name].init();
    lazyManagers[name] = true;
  }
  return window[name];
}
```

### Caching Strategy

```javascript
// Cache expensive operations
const cache = {
  permissions: {},
  translations: {},
  auditLogs: {}
};

function getCachedPermissions(userId) {
  if (!cache.permissions[userId]) {
    cache.permissions[userId] = rbacManager.getCurrentUserPermissions();
  }
  return cache.permissions[userId];
}
```

---

## 11. Testing Checklist

- [ ] User registration/login
- [ ] Session management
- [ ] Permission enforcement
- [ ] Language switching
- [ ] Branding application
- [ ] API synchronization
- [ ] Error handling
- [ ] Performance tests
- [ ] Security tests
- [ ] Cross-browser tests

---

*Technical Architecture Version: 1.0*  
*Created: 2026-08-29*
