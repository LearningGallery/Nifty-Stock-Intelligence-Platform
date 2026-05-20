export function validateStockSymbol(symbol) {
  const pattern = /^[A-Z]{2,10}$/
  return pattern.test(symbol)
}

export function validateEmail(email) {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return pattern.test(email)
}

export function validatePassword(password) {
  // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
  const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/
  return pattern.test(password)
}

export function sanitizeInput(input) {
  return input.trim().replace(/<[^>]*>/g, '')
}
