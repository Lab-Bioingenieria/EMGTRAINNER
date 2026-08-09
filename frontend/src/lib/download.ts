import { authService } from '@/services/auth.service'

/**
 * Downloads a protected backend resource.
 *
 * A plain `<a href download>` cannot send an Authorization header, so protected
 * endpoints must be fetched with the JWT and saved from an object URL instead.
 */
export async function downloadProtectedFile(url: string, filename: string): Promise<void> {
  const response = await authService.authFetch(url)
  if (!response.ok) {
    throw new Error(`No se pudo descargar el archivo (${response.status})`)
  }

  const blob = await response.blob()
  const objectUrl = URL.createObjectURL(blob)
  try {
    const link = document.createElement('a')
    link.href = objectUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
  } finally {
    URL.revokeObjectURL(objectUrl)
  }
}
