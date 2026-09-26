# Query String Helper Functions - Usage Guide

Complete reference for using query string utility functions in the Eli Lilly ALCOA+ QA System.

## 📦 Import

### TypeScript / React
```typescript
import {
  buildQueryString,
  parseQueryString,
  buildUrl,
  getQueryParam,
  addQueryParam,
  removeQueryParam,
  buildApiUrl,
  formatQueryParams,
  hasQueryParams,
  getAllQueryParams
} from './utils/format';
```

### JavaScript (Direct HTML)
```html
<script src="./src/utils/format.js"></script>
<script>
  // Functions available globally
  const url = buildUrl('/api/records', { status: 'approved' });
</script>
```

## 🔧 Functions Reference

### 1. `buildQueryString(params)`
Build query string from object parameters.

```typescript
// Basic usage
buildQueryString({ status: 'approved', limit: 10 })
// Output: 'status=approved&limit=10'

// Filtering empty values
buildQueryString({ status: 'approved', notes: '', limit: 10 })
// Output: 'status=approved&limit=10'
```

### 2. `parseQueryString(queryString)`
Parse query string into object.

```typescript
// Parse URL query string
parseQueryString('?status=approved&limit=10')
// Output: { status: 'approved', limit: '10' }

// Parse without leading ?
parseQueryString('status=approved&limit=10')
// Output: { status: 'approved', limit: '10' }
```

### 3. `buildUrl(baseUrl, params)`
Build complete URL with query parameters.

```typescript
// Build API URL
buildUrl('http://localhost:8000/api/qa-records', {
  status: 'approved',
  limit: 10,
  skip: 0
})
// Output: 'http://localhost:8000/api/qa-records?status=approved&limit=10&skip=0'

// Empty params
buildUrl('http://localhost:8000/api/qa-records', {})
// Output: 'http://localhost:8000/api/qa-records'
```

### 4. `getQueryParam(paramName, url?)`
Get single query parameter value.

```typescript
// Get from current URL
getQueryParam('status')
// Output: 'approved' (if current URL is ?status=approved)

// Get from specific URL
getQueryParam('status', '?status=submitted&limit=10')
// Output: 'submitted'

// Get non-existent parameter
getQueryParam('nonexistent')
// Output: null
```

### 5. `addQueryParam(url, key, value)`
Add or update query parameter in URL.

```typescript
// Add to URL without params
addQueryParam('http://localhost/api', 'status', 'approved')
// Output: 'http://localhost/api?status=approved'

// Update existing parameter
addQueryParam('http://localhost/api?status=draft', 'status', 'approved')
// Output: 'http://localhost/api?status=approved'

// Add parameter to URL with existing params
addQueryParam('http://localhost/api?limit=10', 'status', 'approved')
// Output: 'http://localhost/api?limit=10&status=approved'
```

### 6. `removeQueryParam(url, key)`
Remove query parameter from URL.

```typescript
// Remove from URL
removeQueryParam('http://localhost/api?status=approved&limit=10', 'status')
// Output: 'http://localhost/api?limit=10'

// Remove non-existent parameter
removeQueryParam('http://localhost/api?status=approved', 'filter')
// Output: 'http://localhost/api?status=approved'

// Remove only parameter
removeQueryParam('http://localhost/api?status=approved', 'status')
// Output: 'http://localhost/api'
```

### 7. `buildApiUrl(endpoint, filters?, options?)`
Build API endpoint URL with filters and options.

```typescript
// Simple endpoint
buildApiUrl('/api/qa-records')
// Output: '/api/qa-records'

// With filters
buildApiUrl('/api/qa-records', { status: 'approved', batch: 'BTH-001' })
// Output: '/api/qa-records?status=approved&batch=BTH-001'

// With filters and options
buildApiUrl('/api/qa-records', 
  { status: 'approved' },
  { skip: 0, limit: 10, sort: 'created_at' }
)
// Output: '/api/qa-records?status=approved&skip=0&limit=10&sort=created_at'
```

### 8. `formatQueryParams(params)`
Format query parameters for display/logging.

```typescript
// Format for logging
formatQueryParams({ status: 'approved', limit: 10 })
// Output: 'status=approved, limit=10'

// Filtering null values
formatQueryParams({ status: 'approved', notes: null, limit: 10 })
// Output: 'status=approved, limit=10'
```

### 9. `hasQueryParams(url)`
Check if URL contains query parameters.

```typescript
// URL with params
hasQueryParams('http://localhost/api?status=approved')
// Output: true

// URL without params
hasQueryParams('http://localhost/api')
// Output: false
```

### 10. `getAllQueryParams(url?)`
Get all query parameters from URL.

```typescript
// Get from current URL
getAllQueryParams()
// Output: { status: 'approved', limit: '10' }

// Get from specific URL
getAllQueryParams('?status=approved&limit=10')
// Output: { status: 'approved', limit: '10' }
```

## 💡 Real-World Examples

### Filter QA Records
```typescript
// Build filtered API call
const filters = {
  batch_number: 'BTH-2024-001',
  status: 'submitted',
  test_type: 'Physical'
};

const apiUrl = buildApiUrl('/api/qa-records', filters, {
  skip: 0,
  limit: 100,
  sort: 'created_at'
});

// apiUrl: '/api/qa-records?batch_number=BTH-2024-001&status=submitted&test_type=Physical&skip=0&limit=100&sort=created_at'

const response = await fetch(apiUrl);
```

### Update URL Parameters
```typescript
// Current URL: http://localhost:8080?status=draft&limit=10

// Change status to approved
let url = window.location.href;
url = removeQueryParam(url, 'status');
url = addQueryParam(url, 'status', 'approved');
// Result: http://localhost:8080?limit=10&status=approved

// Navigate
window.location.href = url;
```

### Handle URL Navigation
```typescript
// Build pagination URL
function goToPage(page) {
  const url = addQueryParam(window.location.href, 'skip', (page - 1) * 10);
  window.history.pushState({}, '', url);
  loadRecords();
}

// Get current filters
function getCurrentFilters() {
  const params = getAllQueryParams();
  return {
    status: params.status || 'all',
    limit: parseInt(params.limit || '10'),
    skip: parseInt(params.skip || '0')
  };
}
```

### Build Dynamic Audit Trail Filter
```typescript
// Filter audit logs by date range
async function getAuditLogs(recordId, startDate, endDate) {
  const filters = {
    qa_record_id: recordId,
    start_date: startDate.toISOString(),
    end_date: endDate.toISOString()
  };

  const url = buildApiUrl(
    `/api/audit-logs/${recordId}`,
    filters,
    { limit: 50 }
  );

  return fetch(url).then(r => r.json());
}
```

## 🎯 Best Practices

1. **Always filter empty values** - Use `buildQueryString()` which automatically removes null/undefined/empty string values

2. **Use `buildApiUrl()` for API calls** - Consistent formatting for API endpoints:
   ```typescript
   const url = buildApiUrl('/api/endpoint', filters, options);
   ```

3. **Use `addQueryParam()` for updating URLs** - Maintains existing parameters:
   ```typescript
   let url = addQueryParam(url, 'page', 2);
   ```

4. **Parse params early** - Get all params at component mount:
   ```typescript
   const params = getAllQueryParams();
   ```

5. **Handle encoding automatically** - Functions use `encodeURIComponent()`:
   ```typescript
   buildQueryString({ notes: 'Special chars: &=?' })
   // Safely encodes special characters
   ```

## 📋 Parameter Types

| Function | Input | Output |
|----------|-------|--------|
| `buildQueryString` | Object | string |
| `parseQueryString` | string | Object |
| `buildUrl` | (string, Object) | string |
| `getQueryParam` | (string, string?) | string\|null |
| `addQueryParam` | (string, string, any) | string |
| `removeQueryParam` | (string, string) | string |
| `buildApiUrl` | (string, Object?, Object?) | string |
| `formatQueryParams` | Object | string |
| `hasQueryParams` | string | boolean |
| `getAllQueryParams` | string? | Object |

## 🔒 Security Notes

- All functions use `encodeURIComponent()` to safely encode parameters
- Never trust query parameters directly - always validate on the backend
- For sensitive data, use POST requests instead of query strings
