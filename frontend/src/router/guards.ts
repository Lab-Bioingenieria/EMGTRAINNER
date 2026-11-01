import type { RouteLocationNormalized, RouteLocationRaw } from 'vue-router'
import { authService } from '@/services/auth.service'

/** Routes reachable without being logged in. */
export const PUBLIC_ROUTES = new Set(['Login'])

/**
 * Same "session is gone" check the router used inline before: not logged
 * in and not headed to a public route -> bounce to /login, preserving the
 * intended destination.
 */
export function authGuard(to: RouteLocationNormalized): true | RouteLocationRaw {
  if (PUBLIC_ROUTES.has(to.name as string)) return true
  if (authService.isLoggedIn()) return true
  return { name: 'Login', query: { redirect: to.fullPath } }
}

/**
 * Keeps the doctor and patient interfaces actually separate: a route
 * tagged with `meta.role` is off-limits to a logged-in user whose account
 * is the other role (typing the URL directly, an old bookmark, a shared
 * link). This is a UX guard, not the security boundary — the backend's
 * `RequireRole` dependency is what actually enforces it on every request,
 * since a route guard only ever runs client-side.
 *
 * A role mismatch sends the user back to Home instead of an error page:
 * Home itself only shows the modules that match the account's real role,
 * so it's always a safe, non-confusing landing spot.
 */
export function roleGuard(to: RouteLocationNormalized): true | RouteLocationRaw {
  const requiredRole = to.meta?.role as ('doctor' | 'patient' | undefined)
  if (!requiredRole) return true

  const role = authService.getRole()
  if (role === requiredRole) return true

  return { name: 'Home' }
}
