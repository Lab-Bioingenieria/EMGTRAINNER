/**
 * Centralized "session is gone" handling.
 *
 * It deliberately does NOT import the vue-router instance: the router already
 * imports authService, and authService needs this helper, so importing the
 * router here would create a cycle. The app uses hash history, so navigating
 * through `window.location.hash` is equivalent to `router.push`.
 */

const LOGIN_PATH = '/login'

/** Current in-app path (hash history), e.g. "/storage?tab=csv". */
export function currentAppPath(): string {
  const hash = window.location.hash
  return hash.startsWith('#') ? hash.slice(1) || '/' : '/'
}

/** True when the user is already on the login screen. */
export function isOnLoginRoute(): boolean {
  return currentAppPath().split('?')[0] === LOGIN_PATH
}

/**
 * Redirect to login, preserving the current location so the user can be sent
 * back after signing in. No-op when already on /login, which prevents redirect
 * loops when the login request itself returns 401.
 */
export function redirectToLogin(): void {
  if (isOnLoginRoute()) return
  const redirect = currentAppPath()
  window.location.hash = `#${LOGIN_PATH}?redirect=${encodeURIComponent(redirect)}`
}
