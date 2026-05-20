export function formatCurrency(amount, decimals = 2) {
  if (amount >= 10000000) {
    return `₹${(amount / 10000000).toFixed(decimals)} Cr`
  } else if (amount >= 100000) {
    return `₹${(amount / 100000).toFixed(decimals)} L`
  } else if (amount >= 1000) {
    return `₹${(amount / 1000).toFixed(decimals)} K`
  } else {
    return `₹${amount.toFixed(decimals)}`
  }
}

export function formatPercentage(value, decimals = 2) {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(decimals)}%`
}

export function formatNumber(value, decimals = 2) {
  return new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value)
}

export function formatVolume(volume) {
  if (volume >= 10000000) {
    return `${(volume / 10000000).toFixed(2)} Cr`
  } else if (volume >= 1000000) {
    return `${(volume / 1000000).toFixed(2)} M`
  } else if (volume >= 1000) {
    return `${(volume / 1000).toFixed(2)} K`
  } else {
    return volume.toString()
  }
}

export function truncateText(text, maxLength = 50) {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
