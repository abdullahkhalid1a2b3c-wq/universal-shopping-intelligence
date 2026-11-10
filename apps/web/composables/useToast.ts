export interface ToastMessage {
  id: string
  type: 'success' | 'error' | 'info'
  text: string
}

export function useToast() {
  const toasts = useState<ToastMessage[]>('fit_toasts', () => [])

  function add(type: 'success' | 'error' | 'info', text: string, duration = 4000) {
    const id = Math.random().toString(36).substring(2, 9)
    toasts.value.push({ id, type, text })
    setTimeout(() => {
      remove(id)
    }, duration)
  }

  function remove(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return {
    toasts: readonly(toasts),
    success: (text: string) => add('success', text),
    error: (text: string) => add('error', text),
    info: (text: string) => add('info', text),
    remove,
  }
}

