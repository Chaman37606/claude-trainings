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
  const state = {
    patients: [],
    selectedPatientId: null,
    currentEncounterId: null,
    currentDraft: null, // last draft object returned by the server
  };

  // ---------------------------------------------------------------------
  // Element refs
  // ---------------------------------------------------------------------
  const el = {
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
    approvedByInput: document.getElementById('approved-by-input'),
    confirmApproveBtn: document.getElementById('confirm-approve-btn'),
    cancelApproveBtn: document.getElementById('cancel-approve-btn'),

    auditStatus: document.getElementById('audit-status'),
    auditTableBody: document.getElementById('audit-table-body'),
    auditFilterCheckbox: document.getElementById('audit-filter-checkbox'),
  };

  // ---------------------------------------------------------------------
  // Fetch helper
  // ---------------------------------------------------------------------
  async function apiRequest(path, options) {
    let res;
    try {
      res = await fetch(path, options);
    } catch (networkErr) {
      throw new Error('Network error — could not reach the server.');
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

    items.forEach((item) => {
      const li = document.createElement('li');
      li.className = 'summary-item';
      li.id = `summary-item-${item.id}`;

      const catCls = categoryClass(item.category);
      li.innerHTML = `
        <div class="summary-item-top">
          <div class="summary-item-desc">${escapeHtml(item.description)}</div>
          <div class="summary-item-date">${escapeHtml(formatDate(item.date))}</div>
        </div>
        <span class="category-badge ${catCls}">${escapeHtml(item.category || 'other')}</span>
        ${item.relevance_score !== undefined && item.relevance_score !== null
          ? `<span class="relevance-pip">relevance: ${escapeHtml(item.relevance_score)}</span>`
          : ''}
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
          <span class="category-badge ${catCls}">${escapeHtml(ev.category || ev.type || 'other')}</span>
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
    el.approveInlineForm.hidden = false;
    el.approvedByInput.value = '';
    el.approvedByInput.focus();
  });

  el.cancelApproveBtn.addEventListener('click', () => {
    el.approveInlineForm.hidden = true;
  });

  el.confirmApproveBtn.addEventListener('click', async () => {
    if (!state.currentEncounterId) return;
    const approvedBy = el.approvedByInput.value.trim();
    if (!approvedBy) {
      setStatus(el.draftActionStatus, 'Enter the physician name to sign the note.', 'error');
      el.approvedByInput.focus();
      return;
    }

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

      const approved = await apiRequest(`/api/encounters/${state.currentEncounterId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved_by: approvedBy }),
      });
      renderDraft(approved);
      el.approveInlineForm.hidden = true;
      setStatus(el.draftActionStatus, `Note signed by ${approvedBy}.`, 'success');
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
  document.addEventListener('DOMContentLoaded', () => {
    // no-op: script is loaded at end of body, but kept for safety if moved.
  });

  loadPatients().then(() => {
    const params = new URLSearchParams(location.search);
    const p = params.get('__debug_patient');
    if (p) selectPatient(Number(p)).then(() => {
      if (params.get('__debug_timeline')) el.timelineToggleBtn.click();
    });
  });
  loadAudit(); // show global audit trail before any patient is selected
})();
