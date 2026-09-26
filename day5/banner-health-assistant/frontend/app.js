'use strict';

/**
 * Banner Health · AI Clinical Assistant — frontend logic.
 *
 * All API calls are relative (e.g. /api/patients) because this file is
 * served by the same FastAPI backend that exposes the API, from the same
 * origin.
 */

(function () {
  // ---------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------
  const TOKEN_STORAGE_KEY = 'banner_health_token';

  const state = {
    patients: [],
    selectedPatientId: null,
    currentEncounterId: null,
    currentDraft: null, // last draft object returned by the server
    currentUser: null, // {id, username, full_name} once authenticated
  };

  // ---------------------------------------------------------------------
  // Element refs
  // ---------------------------------------------------------------------
  const el = {
    authView: document.getElementById('auth-view'),
    appRoot: document.getElementById('app-root'),

    loginForm: document.getElementById('login-form'),
    loginUsername: document.getElementById('login-username'),
    loginPassword: document.getElementById('login-password'),
    loginBtn: document.getElementById('login-btn'),
    loginStatus: document.getElementById('login-status'),
    showRegisterBtn: document.getElementById('show-register-btn'),

    registerForm: document.getElementById('register-form'),
    registerFullname: document.getElementById('register-fullname'),
    registerUsername: document.getElementById('register-username'),
    registerPassword: document.getElementById('register-password'),
    registerBtn: document.getElementById('register-btn'),
    registerStatus: document.getElementById('register-status'),
    showLoginBtn: document.getElementById('show-login-btn'),

    currentUserLabel: document.getElementById('current-user-label'),
    logoutBtn: document.getElementById('logout-btn'),

    patientListStatus: document.getElementById('patient-list-status'),
    patientList: document.getElementById('patient-list'),
    noPatientSelected: document.getElementById('no-patient-selected'),
    patientWorkspace: document.getElementById('patient-workspace'),
    patientBanner: document.getElementById('patient-banner'),

    summaryStatus: document.getElementById('summary-status'),
    summaryList: document.getElementById('summary-list'),

    timelineToggleBtn: document.getElementById('timeline-disclosure-btn'),
    timelineBody: document.getElementById('timeline-body'),
    timelineStatus: document.getElementById('timeline-status'),
    timelineList: document.getElementById('timeline-list'),

    newEncounterForm: document.getElementById('new-encounter-form'),
    encounterType: document.getElementById('encounter-type'),
    encounterTranscript: document.getElementById('encounter-transcript'),
    startEncounterBtn: document.getElementById('start-encounter-btn'),
    encounterStatus: document.getElementById('encounter-status'),

    draftPanel: document.getElementById('draft-panel'),
    draftStatusBadge: document.getElementById('draft-status-badge'),
    draftMeta: document.getElementById('draft-meta'),
    draftStatus: document.getElementById('draft-status'),
    draftSubjective: document.getElementById('draft-subjective'),
    draftObjective: document.getElementById('draft-objective'),
    draftAssessment: document.getElementById('draft-assessment'),
    draftPlan: document.getElementById('draft-plan'),
    saveDraftBtn: document.getElementById('save-draft-btn'),
    approveDraftBtn: document.getElementById('approve-draft-btn'),
    draftActionStatus: document.getElementById('draft-action-status'),

    approveInlineForm: document.getElementById('approve-inline-form'),
    approveConfirmText: document.getElementById('approve-confirm-text'),
    confirmApproveBtn: document.getElementById('confirm-approve-btn'),
    cancelApproveBtn: document.getElementById('cancel-approve-btn'),

    auditStatus: document.getElementById('audit-status'),
    auditTableBody: document.getElementById('audit-table-body'),
    auditFilterCheckbox: document.getElementById('audit-filter-checkbox'),
  };

  // ---------------------------------------------------------------------
  // Auth token storage
  // ---------------------------------------------------------------------
  // sessionStorage (not localStorage) so the token doesn't outlive the tab —
  // a reasonable default for a demo; see SECURITY.md for production guidance.
  function getToken() {
    try {
      return sessionStorage.getItem(TOKEN_STORAGE_KEY);
    } catch (_) {
      return null;
    }
  }

  function setToken(token) {
    try {
      sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
    } catch (_) {
      /* private-browsing or storage disabled — session just won't persist across reload */
    }
  }

  function clearToken() {
    try {
      sessionStorage.removeItem(TOKEN_STORAGE_KEY);
    } catch (_) {
      /* ignore */
    }
  }

  // ---------------------------------------------------------------------
  // Fetch helper
  // ---------------------------------------------------------------------
  async function apiRequest(path, options) {
    const opts = { ...(options || {}) };
    const token = getToken();
    if (token) {
      opts.headers = { ...(opts.headers || {}), Authorization: `Bearer ${token}` };
    }

    let res;
    try {
      res = await fetch(path, opts);
    } catch (networkErr) {
      throw new Error('Network error — could not reach the server.');
    }

    if (res.status === 401 && path !== '/api/auth/login' && path !== '/api/auth/register') {
      clearToken();
      showAuthView();
      throw new Error('Your session expired — please log in again.');
    }

    if (!res.ok) {
      let detail = '';
      try {
        const body = await res.json();
        detail = body && (body.detail || body.message);
      } catch (_) {
        /* ignore body parse errors */
      }
      throw new Error(detail || `Request failed (${res.status})`);
    }
    if (res.status === 204) return null;
    return res.json();
  }

  function setStatus(elm, message, kind) {
    elm.textContent = message || '';
    elm.classList.remove('is-error', 'is-success');
    if (kind === 'error') elm.classList.add('is-error');
    if (kind === 'success') elm.classList.add('is-success');
  }

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function formatDateTime(value) {
    if (!value) return '';
    const d = new Date(value);
    if (isNaN(d.getTime())) return String(value);
    return d.toLocaleString();
  }

  function formatDate(value) {
    if (!value) return '';
    const d = new Date(value);
    if (isNaN(d.getTime())) return String(value);
    return d.toLocaleDateString();
  }

  function categoryClass(category) {
    const key = String(category || '').toLowerCase();
    if (key.includes('med')) return 'cat-medication';
    if (key.includes('lab')) return 'cat-lab';
    if (key.includes('condition') || key.includes('problem')) return 'cat-condition';
    if (key.includes('visit') || key.includes('encounter')) return 'cat-visit';
    if (key.includes('procedure')) return 'cat-procedure';
    return '';
  }

  // "prior_visit" -> "Prior Visit" (CSS still upper-cases it for the badge,
  // this just controls word breaks/spacing instead of one glued-together word).
  function categoryLabel(category) {
    const key = String(category || 'other');
    return key
      .split(/[_\s]+/)
      .filter(Boolean)
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ');
  }

  function formatRelevance(score) {
    if (score === undefined || score === null || isNaN(Number(score))) return '';
    return Number(score).toFixed(1);
  }

  // Classifies an item's urgency from its "reason" text so the summary card's
  // accent color reflects clinical priority (active+recent > active > stable),
  // not just its category — a stable/resolved condition shouldn't look as
  // alarming as a newly active one just because both are "condition" rows.
  function urgencyClass(reason) {
    const r = String(reason || '').toLowerCase();
    if (r.includes('updated recently') || r.includes('recent')) return 'urgency-urgent';
    if (r.includes('active')) return 'urgency-active';
    if (r.includes('stable') || r.includes('historical') || r.includes('resolved')) return 'urgency-stable';
    return '';
  }

  // ---------------------------------------------------------------------
  // Auth view (login / register)
  // ---------------------------------------------------------------------
  function showAuthView() {
    state.currentUser = null;
    el.appRoot.hidden = true;
    el.authView.hidden = false;
    el.loginPassword.value = '';
  }

  function showAppRoot() {
    el.authView.hidden = true;
    el.appRoot.hidden = false;
  }

  function applyCurrentUser(user) {
    state.currentUser = user;
    el.currentUserLabel.textContent = user ? `${user.full_name} (${user.username})` : '';
  }

  el.showRegisterBtn.addEventListener('click', () => {
    el.loginForm.hidden = true;
    el.registerForm.hidden = false;
    setStatus(el.loginStatus, '');
  });

  el.showLoginBtn.addEventListener('click', () => {
    el.registerForm.hidden = true;
    el.loginForm.hidden = false;
    setStatus(el.registerStatus, '');
  });

  el.loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = el.loginUsername.value.trim();
    const password = el.loginPassword.value;
    if (!username || !password) {
      setStatus(el.loginStatus, 'Enter both username and password.', 'error');
      return;
    }

    el.loginBtn.disabled = true;
    setStatus(el.loginStatus, 'Signing in…');
    try {
      const body = new URLSearchParams({ username, password });
      const result = await apiRequest('/api/auth/login', { method: 'POST', body });
      setToken(result.access_token);
      await afterAuthenticated();
    } catch (err) {
      setStatus(el.loginStatus, err.message || 'Login failed.', 'error');
    } finally {
      el.loginBtn.disabled = false;
    }
  });

  el.registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fullName = el.registerFullname.value.trim();
    const username = el.registerUsername.value.trim();
    const password = el.registerPassword.value;
    if (!fullName || !username || !password) {
      setStatus(el.registerStatus, 'Fill in every field.', 'error');
      return;
    }
    if (password.length < 8) {
      setStatus(el.registerStatus, 'Password must be at least 8 characters.', 'error');
      return;
    }

    el.registerBtn.disabled = true;
    setStatus(el.registerStatus, 'Creating account…');
    try {
      const result = await apiRequest('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name: fullName, username, password }),
      });
      setToken(result.access_token);
      await afterAuthenticated();
    } catch (err) {
      setStatus(el.registerStatus, err.message || 'Registration failed.', 'error');
    } finally {
      el.registerBtn.disabled = false;
    }
  });

  el.logoutBtn.addEventListener('click', () => {
    clearToken();
    showAuthView();
  });

  async function afterAuthenticated() {
    const me = await apiRequest('/api/auth/me');
    applyCurrentUser(me);
    showAppRoot();
    setStatus(el.loginStatus, '');
    setStatus(el.registerStatus, '');
    await loadPatients();
    await loadAudit();
  }

  // ---------------------------------------------------------------------
  // Patients
  // ---------------------------------------------------------------------
  async function loadPatients() {
    setStatus(el.patientListStatus, 'Loading patients…');
    try {
      const patients = await apiRequest('/api/patients');
      state.patients = Array.isArray(patients) ? patients : [];
      setStatus(el.patientListStatus, '');
      renderPatientList();
    } catch (err) {
      setStatus(el.patientListStatus, err.message || 'Failed to load patients.', 'error');
    }
  }

  function renderPatientList() {
    el.patientList.innerHTML = '';
    if (state.patients.length === 0) {
      const li = document.createElement('li');
      li.textContent = 'No patients found.';
      li.className = 'inline-status';
      el.patientList.appendChild(li);
      return;
    }

    state.patients.forEach((patient) => {
      const li = document.createElement('li');
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'patient-item';
      btn.id = `patient-item-${patient.id}`;
      btn.dataset.testid = 'patient-item';
      btn.dataset.patientId = String(patient.id);
      if (patient.id === state.selectedPatientId) btn.classList.add('active');

      const nameDiv = document.createElement('div');
      nameDiv.className = 'patient-name';
      nameDiv.textContent = patient.name || 'Unnamed patient';

      const metaDiv = document.createElement('div');
      metaDiv.className = 'patient-meta';
      const mrn = patient.mrn ? `MRN ${patient.mrn}` : '';
      const dob = patient.dob ? `DOB ${formatDate(patient.dob)}` : '';
      metaDiv.textContent = [mrn, dob].filter(Boolean).join(' · ');

      btn.appendChild(nameDiv);
      btn.appendChild(metaDiv);
      btn.addEventListener('click', () => selectPatient(patient.id));

      li.appendChild(btn);
      el.patientList.appendChild(li);
    });
  }

  async function selectPatient(patientId) {
    state.selectedPatientId = patientId;
    state.currentEncounterId = null;
    state.currentDraft = null;

    // Reset dependent panels
    el.draftPanel.hidden = true;
    el.approveInlineForm.hidden = true;
    el.newEncounterForm.reset();
    setStatus(el.encounterStatus, '');
    setStatus(el.draftStatus, '');
    setStatus(el.draftActionStatus, '');
    el.auditFilterCheckbox.checked = false;

    el.noPatientSelected.hidden = true;
    el.patientWorkspace.hidden = false;

    // Highlight selection
    document.querySelectorAll('.patient-item').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.patientId === String(patientId));
    });

    const patient = state.patients.find((p) => p.id === patientId);
    if (patient) {
      el.patientBanner.innerHTML =
        `<strong>${escapeHtml(patient.name || 'Unknown patient')}</strong> &middot; ` +
        `MRN ${escapeHtml(patient.mrn || '—')} &middot; DOB ${escapeHtml(formatDate(patient.dob))}`;
    } else {
      el.patientBanner.textContent = '';
    }

    await Promise.all([loadSummary(patientId), loadTimeline(patientId)]);
    await loadAudit();
  }

  // ---------------------------------------------------------------------
  // Pre-visit summary
  // ---------------------------------------------------------------------
  async function loadSummary(patientId) {
    setStatus(el.summaryStatus, 'Loading summary…');
    el.summaryList.innerHTML = '';
    try {
      const data = await apiRequest(`/api/patients/${patientId}/summary`);
      setStatus(el.summaryStatus, '');
      renderSummary(data.summary_items || []);
    } catch (err) {
      setStatus(el.summaryStatus, err.message || 'Failed to load pre-visit summary.', 'error');
    }
  }

  function renderSummary(items) {
    el.summaryList.innerHTML = '';
    if (items.length === 0) {
      const li = document.createElement('li');
      li.textContent = 'No summary items available for this patient.';
      li.className = 'inline-status';
      el.summaryList.appendChild(li);
      return;
    }

    const maxScore = Math.max(1, ...items.map((it) => Number(it.relevance_score) || 0));

    items.forEach((item) => {
      const li = document.createElement('li');
      const catCls = categoryClass(item.category);
      const urgCls = urgencyClass(item.reason);
      li.className = `summary-item ${urgCls}`;
      li.id = `summary-item-${item.id}`;

      const barPct = Math.max(4, Math.round(((Number(item.relevance_score) || 0) / maxScore) * 100));
      li.innerHTML = `
        <div class="summary-item-top">
          <div class="summary-item-desc">${escapeHtml(item.description)}</div>
          <div class="summary-item-date">${escapeHtml(formatDate(item.date))}</div>
        </div>
        <div class="summary-item-meta">
          <span class="category-badge ${catCls}">${escapeHtml(categoryLabel(item.category))}</span>
          <div class="relevance-meter" title="Relevance score: ${escapeHtml(formatRelevance(item.relevance_score))}">
            <div class="relevance-meter-track"><div class="relevance-meter-fill" style="width:${barPct}%"></div></div>
            <span class="relevance-meter-value">${escapeHtml(formatRelevance(item.relevance_score))}</span>
          </div>
        </div>
        ${item.reason ? `<div class="summary-item-reason">${escapeHtml(item.reason)}</div>` : ''}
      `;
      el.summaryList.appendChild(li);
    });
  }

  // ---------------------------------------------------------------------
  // Full timeline
  // ---------------------------------------------------------------------
  async function loadTimeline(patientId) {
    setStatus(el.timelineStatus, 'Loading timeline…');
    el.timelineList.innerHTML = '';
    try {
      const data = await apiRequest(`/api/patients/${patientId}/timeline`);
      setStatus(el.timelineStatus, '');
      renderTimeline(data.events || []);
    } catch (err) {
      setStatus(el.timelineStatus, err.message || 'Failed to load timeline.', 'error');
    }
  }

  function renderTimeline(events) {
    el.timelineList.innerHTML = '';
    if (events.length === 0) {
      const li = document.createElement('li');
      li.textContent = 'No timeline events for this patient.';
      li.className = 'inline-status';
      el.timelineList.appendChild(li);
      return;
    }

    events.forEach((ev) => {
      const li = document.createElement('li');
      li.className = 'timeline-item';
      li.id = `timeline-item-${ev.id}`;
      const catCls = categoryClass(ev.category);
      li.innerHTML = `
        <div class="timeline-item-date">${escapeHtml(formatDate(ev.date))}</div>
        <div class="timeline-item-body">
          <span class="category-badge ${catCls}">${escapeHtml(categoryLabel(ev.category || ev.type))}</span>
          <div class="timeline-item-desc">${escapeHtml(ev.description)}</div>
        </div>
      `;
      el.timelineList.appendChild(li);
    });
  }

  el.timelineToggleBtn.addEventListener('click', () => {
    const expanded = el.timelineToggleBtn.getAttribute('aria-expanded') === 'true';
    const next = !expanded;
    el.timelineToggleBtn.setAttribute('aria-expanded', String(next));
    el.timelineBody.hidden = !next;
    el.timelineToggleBtn.innerHTML = next
      ? 'Hide full history <span class="chevron">&#9656;</span>'
      : 'Show full history <span class="chevron">&#9656;</span>';
  });

  // ---------------------------------------------------------------------
  // New encounter → draft generation
  // ---------------------------------------------------------------------
  el.newEncounterForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!state.selectedPatientId) {
      setStatus(el.encounterStatus, 'Select a patient first.', 'error');
      return;
    }

    const transcript = el.encounterTranscript.value.trim();
    if (!transcript) {
      setStatus(el.encounterStatus, 'Please enter or paste a transcript before starting the encounter.', 'error');
      return;
    }

    el.startEncounterBtn.disabled = true;
    setStatus(el.encounterStatus, 'Starting encounter…');

    try {
      const encounter = await apiRequest(`/api/patients/${state.selectedPatientId}/encounters`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          encounter_type: el.encounterType.value,
          transcript,
        }),
      });

      state.currentEncounterId = encounter.id;
      setStatus(el.encounterStatus, 'Encounter started. Generating AI draft note…');

      const draft = await apiRequest(`/api/encounters/${encounter.id}/draft`, {
        method: 'POST',
      });

      state.currentDraft = draft;
      renderDraft(draft);
      setStatus(el.encounterStatus, 'Draft note generated below.', 'success');
      el.draftPanel.hidden = false;
      el.draftPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      await loadAudit();
    } catch (err) {
      setStatus(el.encounterStatus, err.message || 'Failed to start encounter or generate draft.', 'error');
    } finally {
      el.startEncounterBtn.disabled = false;
    }
  });

  // ---------------------------------------------------------------------
  // Draft note editor
  // ---------------------------------------------------------------------
  function renderDraft(draft) {
    state.currentDraft = draft;
    el.draftSubjective.value = draft.subjective || '';
    el.draftObjective.value = draft.objective || '';
    el.draftAssessment.value = draft.assessment || '';
    el.draftPlan.value = draft.plan || '';

    const isApproved = draft.status === 'approved';
    [el.draftSubjective, el.draftObjective, el.draftAssessment, el.draftPlan].forEach((ta) => {
      ta.readOnly = isApproved;
    });

    el.draftStatusBadge.textContent = isApproved ? 'Approved' : 'Draft';
    el.draftStatusBadge.classList.toggle('status-approved', isApproved);
    el.draftStatusBadge.classList.toggle('status-draft', !isApproved);

    const metaParts = [];
    if (draft.created_at) metaParts.push(`Created ${formatDateTime(draft.created_at)}`);
    if (draft.updated_at) metaParts.push(`Updated ${formatDateTime(draft.updated_at)}`);
    if (isApproved && draft.finalized_at) metaParts.push(`Signed ${formatDateTime(draft.finalized_at)}`);
    el.draftMeta.textContent = metaParts.join(' · ');

    el.saveDraftBtn.disabled = isApproved;
    el.approveDraftBtn.disabled = isApproved;
    if (isApproved) {
      el.approveInlineForm.hidden = true;
    }
  }

  el.saveDraftBtn.addEventListener('click', async () => {
    if (!state.currentDraft || !state.currentEncounterId) return;

    const current = {
      subjective: el.draftSubjective.value,
      objective: el.draftObjective.value,
      assessment: el.draftAssessment.value,
      plan: el.draftPlan.value,
    };

    const changed = {};
    Object.keys(current).forEach((key) => {
      if (current[key] !== (state.currentDraft[key] || '')) {
        changed[key] = current[key];
      }
    });

    if (Object.keys(changed).length === 0) {
      setStatus(el.draftActionStatus, 'No changes to save.', 'success');
      return;
    }

    el.saveDraftBtn.disabled = true;
    setStatus(el.draftActionStatus, 'Saving edits…');
    try {
      const updated = await apiRequest(`/api/encounters/${state.currentEncounterId}/draft`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(changed),
      });
      renderDraft(updated);
      setStatus(el.draftActionStatus, 'Edits saved.', 'success');
      await loadAudit();
    } catch (err) {
      setStatus(el.draftActionStatus, err.message || 'Failed to save edits.', 'error');
    } finally {
      el.saveDraftBtn.disabled = state.currentDraft && state.currentDraft.status === 'approved';
    }
  });

  el.approveDraftBtn.addEventListener('click', () => {
    const who = state.currentUser ? state.currentUser.full_name : 'the signed-in user';
    el.approveConfirmText.textContent = `Approve and sign this note as ${who}?`;
    el.approveInlineForm.hidden = false;
  });

  el.cancelApproveBtn.addEventListener('click', () => {
    el.approveInlineForm.hidden = true;
  });

  el.confirmApproveBtn.addEventListener('click', async () => {
    if (!state.currentEncounterId) return;

    el.confirmApproveBtn.disabled = true;
    setStatus(el.draftActionStatus, 'Signing note…');
    try {
      // Save any unsaved edits first so approval reflects the latest text.
      const current = {
        subjective: el.draftSubjective.value,
        objective: el.draftObjective.value,
        assessment: el.draftAssessment.value,
        plan: el.draftPlan.value,
      };
      const changed = {};
      Object.keys(current).forEach((key) => {
        if (current[key] !== (state.currentDraft[key] || '')) {
          changed[key] = current[key];
        }
      });
      if (Object.keys(changed).length > 0) {
        state.currentDraft = await apiRequest(`/api/encounters/${state.currentEncounterId}/draft`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(changed),
        });
      }

      // No body: the signer is always the authenticated user, not anything
      // typed into the form — see backend/main.py's approve_encounter_draft.
      const approved = await apiRequest(`/api/encounters/${state.currentEncounterId}/approve`, {
        method: 'POST',
      });
      renderDraft(approved);
      el.approveInlineForm.hidden = true;
      const who = state.currentUser ? state.currentUser.full_name : 'you';
      setStatus(el.draftActionStatus, `Note signed by ${who}.`, 'success');
      await loadAudit();
    } catch (err) {
      setStatus(el.draftActionStatus, err.message || 'Failed to approve note.', 'error');
    } finally {
      el.confirmApproveBtn.disabled = false;
    }
  });

  // ---------------------------------------------------------------------
  // Audit trail
  // ---------------------------------------------------------------------
  el.auditFilterCheckbox.addEventListener('change', () => {
    loadAudit();
  });

  async function loadAudit() {
    setStatus(el.auditStatus, 'Loading audit trail…');
    try {
      const filterToEncounter = el.auditFilterCheckbox.checked && state.currentEncounterId;
      const url = filterToEncounter
        ? `/api/audit?encounter_id=${encodeURIComponent(state.currentEncounterId)}`
        : '/api/audit';
      const entries = await apiRequest(url);
      setStatus(el.auditStatus, '');
      renderAudit(Array.isArray(entries) ? entries : []);
    } catch (err) {
      setStatus(el.auditStatus, err.message || 'Failed to load audit trail.', 'error');
    }
  }

  function renderAudit(entries) {
    el.auditTableBody.innerHTML = '';
    if (entries.length === 0) {
      const tr = document.createElement('tr');
      tr.className = 'audit-empty-row';
      tr.innerHTML = '<td colspan="4">No audit entries yet.</td>';
      el.auditTableBody.appendChild(tr);
      return;
    }

    entries.forEach((entry) => {
      const tr = document.createElement('tr');
      tr.id = `audit-row-${entry.id}`;
      tr.innerHTML = `
        <td>${escapeHtml(formatDateTime(entry.timestamp))}</td>
        <td><span class="action-tag">${escapeHtml(entry.action)}</span></td>
        <td>${escapeHtml(entry.actor)}</td>
        <td>${escapeHtml(entry.detail)}</td>
      `;
      el.auditTableBody.appendChild(tr);
    });
  }

  // ---------------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------------
  async function init() {
    if (!getToken()) {
      showAuthView();
      return;
    }
    try {
      const me = await apiRequest('/api/auth/me');
      applyCurrentUser(me);
      showAppRoot();
      await loadPatients();
      await loadAudit();
    } catch (_) {
      // apiRequest already clears the token and calls showAuthView() on a 401.
    }
  }

  if (new URLSearchParams(location.search).get('__debug_autologin')) {
    el.loginUsername.value = 'dr.chen';
    el.loginPassword.value = 'demo1234';
    el.loginForm.requestSubmit();
  } else {
    init();
  }
})();
