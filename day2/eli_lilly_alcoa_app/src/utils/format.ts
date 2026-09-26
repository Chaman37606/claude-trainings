/**
 * Query String Helper Functions
 * Utility functions for building and parsing query strings
 */

/**
 * Build query string from object parameters
 * @param params - Object with key-value pairs
 * @returns Formatted query string (without leading ?)
 * @example
 * buildQueryString({ status: 'approved', limit: 10 })
 * // Returns: 'status=approved&limit=10'
 */
export function buildQueryString(params: Record<string, any>): string {
  return Object.entries(params)
    .filter(([, value]) => value !== null && value !== undefined && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join('&');
}

/**
 * Parse query string into object
 * @param queryString - Query string (with or without leading ?)
 * @returns Object with parsed parameters
 * @example
 * parseQueryString('status=approved&limit=10')
 * // Returns: { status: 'approved', limit: '10' }
 */
export function parseQueryString(queryString: string): Record<string, string> {
  const params = new URLSearchParams(queryString.startsWith('?') ? queryString.slice(1) : queryString);
  const result: Record<string, string> = {};

  params.forEach((value, key) => {
    result[key] = value;
  });

  return result;
}

/**
 * Build URL with query parameters
 * @param baseUrl - Base URL
 * @param params - Object with parameters
 * @returns Complete URL with query string
 * @example
 * buildUrl('http://localhost:8000/api/records', { status: 'approved' })
 * // Returns: 'http://localhost:8000/api/records?status=approved'
 */
export function buildUrl(baseUrl: string, params?: Record<string, any>): string {
  if (!params || Object.keys(params).length === 0) {
    return baseUrl;
  }

  const queryString = buildQueryString(params);
  return `${baseUrl}${queryString ? `?${queryString}` : ''}`;
}

/**
 * Get query parameter value from URL
 * @param paramName - Parameter name to retrieve
 * @param url - URL to parse (defaults to current window.location.search)
 * @returns Parameter value or null if not found
 * @example
 * getQueryParam('status')
 * // Returns value of status parameter from URL
 */
export function getQueryParam(paramName: string, url?: string): string | null {
  const queryString = url || (typeof window !== 'undefined' ? window.location.search : '');
  const params = parseQueryString(queryString);
  return params[paramName] || null;
}

/**
 * Add or update query parameter in URL
 * @param url - Base URL
 * @param key - Parameter key
 * @param value - Parameter value
 * @returns URL with updated parameter
 * @example
 * addQueryParam('http://localhost/api', 'status', 'approved')
 * // Returns: 'http://localhost/api?status=approved'
 */
export function addQueryParam(url: string, key: string, value: any): string {
  const [baseUrl, existingQuery] = url.split('?');
  const params = existingQuery ? parseQueryString(existingQuery) : {};

  params[key] = String(value);
  const queryString = buildQueryString(params);

  return `${baseUrl}${queryString ? `?${queryString}` : ''}`;
}

/**
 * Remove query parameter from URL
 * @param url - URL with query string
 * @param key - Parameter key to remove
 * @returns URL without the specified parameter
 * @example
 * removeQueryParam('http://localhost?status=approved&limit=10', 'status')
 * // Returns: 'http://localhost?limit=10'
 */
export function removeQueryParam(url: string, key: string): string {
  const [baseUrl, existingQuery] = url.split('?');
  if (!existingQuery) return url;

  const params = parseQueryString(existingQuery);
  delete params[key];

  const queryString = buildQueryString(params);
  return `${baseUrl}${queryString ? `?${queryString}` : ''}`;
}

/**
 * Build API endpoint URL with query parameters
 * @param endpoint - API endpoint path
 * @param filters - Object with filter parameters
 * @param options - Additional options (skip, limit, sort)
 * @returns Complete API URL
 * @example
 * buildApiUrl('/api/qa-records', { status: 'approved' }, { skip: 0, limit: 10 })
 * // Returns: '/api/qa-records?status=approved&skip=0&limit=10'
 */
export function buildApiUrl(
  endpoint: string,
  filters?: Record<string, any>,
  options?: { skip?: number; limit?: number; sort?: string }
): string {
  const params: Record<string, any> = { ...filters };

  if (options?.skip !== undefined) params.skip = options.skip;
  if (options?.limit !== undefined) params.limit = options.limit;
  if (options?.sort) params.sort = options.sort;

  return buildUrl(endpoint, params);
}

/**
 * Format query parameters for display
 * @param params - Object with parameters
 * @returns Formatted string for logging/display
 * @example
 * formatQueryParams({ status: 'approved', limit: 10 })
 * // Returns: 'status=approved, limit=10'
 */
export function formatQueryParams(params: Record<string, any>): string {
  return Object.entries(params)
    .filter(([, value]) => value !== null && value !== undefined)
    .map(([key, value]) => `${key}=${value}`)
    .join(', ');
}

/**
 * Check if URL has query parameters
 * @param url - URL to check
 * @returns true if URL contains query string
 * @example
 * hasQueryParams('http://localhost?status=approved')
 * // Returns: true
 */
export function hasQueryParams(url: string): boolean {
  return url.includes('?');
}

/**
 * Get all query parameters from URL
 * @param url - URL to parse (defaults to current window.location.search)
 * @returns Object with all parameters
 * @example
 * getAllQueryParams('?status=approved&limit=10')
 * // Returns: { status: 'approved', limit: '10' }
 */
export function getAllQueryParams(url?: string): Record<string, string> {
  const queryString = url || (typeof window !== 'undefined' ? window.location.search : '');
  return parseQueryString(queryString);
}
