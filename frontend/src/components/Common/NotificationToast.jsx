// Note: Using sonner library (already imported in main.jsx)
// This is just a wrapper/helper if needed

import { toast } from 'sonner'

export const showSuccess = (message) => {
  toast.success(message)
}

export const showError = (message) => {
  toast.error(message)
}

export const showInfo = (message) => {
  toast.info(message)
}

export const showWarning = (message) => {
  toast.warning(message)
}

export const showLoading = (message) => {
  return toast.loading(message)
}

export const dismissToast = (toastId) => {
  toast.dismiss(toastId)
}
