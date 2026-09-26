/**
 * Query String Helper Functions (JavaScript)
 * Utility functions for building and parsing query strings
 */

/**
 * Build query string from object parameters
 * @param {Object} params - Object with key-value pairs
 * @returns {string} Formatted query string (without leading ?)
 */
function buildQueryString(params) {
  return Object.entries(params)
    .filter(([, value]) => value !== null && value !== undefined && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join('&');
}

/**
 * Parse query string into object
 * @param {string} queryString - Query string (with or without leading ?)
 * @returns {Object} Object with parsed parameters
 */
function parseQueryString(queryString) {
  const params = new URLSearchParams(queryString.startsWith('?') ? queryString.slice(1) : queryString);
  const result = {};

  params.forEach((value, key) => {
    result[key] = value;
  });

  return result;
}

/**
 * Build URL with query parameters
 * @param {string} baseUrl - Base URL
 * @param {Object} params - Object with parameters
 * @returns {string} Complete URL with query string
 */
function buildUrl(baseUrl, params) {
  if (!params || Object.keys(params).length === 0) {
    return baseUrl;
  }

  const queryString = buildQueryString(params);
  return `${baseUrl}${queryString ? `?${queryString}` : ''}`;
}

/**
 * Get query parameter value from URL
 * @param {string} paramName - Parameter name to retrieve
 * @param {string} url - URL to parse (defaults to current window.location.search)
 * @returns {string|null} Parameter value or null if not found
 */
function getQueryParam(paramName, url) {
  const queryString = url || (typeof window !== 'undefined' ? window.location.search : '');
  const params = parseQueryString(queryString);
  return params[paramName] || null;
}

/**
 * Add or update query parameter in URL
 * @param {string} url - Base URL
 * @param {string} key - Parameter key
 * @param {any} value - Parameter value
 * @returns {string} URL with updated parameter
 */
function addQueryParam(url, key, value) {
  const [baseUrl, existingQuery] = url.split('?');
  const params = existingQuery ? parseQueryString(existingQuery) : {};

  params[key] = String(value);
  const queryString = buildQueryString(params);

  return `${baseUrl}${queryString ? `?${queryString}` : ''}`;
}

/**
 * Remove query parameter from URL
 * @param {string} url - URL with query string
 * @param {string} key - Parameter key to remove
 * @returns {string} URL without the specified parameter
 */
function removeQueryParam(url, key) {
  const [baseUrl, existingQuery] = url.split('?');
  if (!existingQuery) return url;

  const params = parseQueryString(existingQuery);
  delete params[key];

  const queryString = buildQueryString(params);
  return `${baseUrl}${queryString ? `?${queryString}` : ''}`;
}

/**
 * Build API endpoint URL with query parameters
 * @param {string} endpoint - API endpoint path
 * @param {Object} filters - Object with filter parameters
 * @param {Object} options - Additional options (skip, limit, sort)
 * @returns {string} Complete API URL
 */
function buildApiUrl(endpoint, filters, options) {
  const params = { ...filters };

  if (options?.skip !== undefined) params.skip = options.skip;
  if (options?.limit !== undefined) params.limit = options.limit;
  if (options?.sort) params.sort = options.sort;

  return buildUrl(endpoint, params);
}

/**
 * Format query parameters for display
 * @param {Object} params - Object with parameters
 * @returns {string} Formatted string for logging/display
 */
function formatQueryParams(params) {
  return Object.entries(params)
    .filter(([, value]) => value !== null && value !== undefined)
    .map(([key, value]) => `${key}=${value}`)
    .join(', ');
}

/**
 * Check if URL has query parameters
 * @param {string} url - URL to check
 * @returns {boolean} true if URL contains query string
 */
function hasQueryParams(url) {
  return url.includes('?');
}

/**
 * Get all query parameters from URL
 * @param {string} url - URL to parse (defaults to current window.location.search)
 * @returns {Object} Object with all parameters
 */
function getAllQueryParams(url) {
  const queryString = url || (typeof window !== 'undefined' ? window.location.search : '');
  return parseQueryString(queryString);
}

// Export for use in modules or global scope
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
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
  };
}
