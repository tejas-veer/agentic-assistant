import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number | undefined | null): string {
  if (price == null) return '₹0'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(price)
}

export function formatTime(date: string | Date | undefined | null): string {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function getStatusColor(status: string | undefined | null): string {
  if (!status) return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  
  const colors: Record<string, string> = {
    draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    pending: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    pending_approval: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    confirmed: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    in_progress: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    preparing: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    ready: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    completed: 'bg-green-500/20 text-green-400 border-green-500/30',
    delivered: 'bg-green-500/20 text-green-400 border-green-500/30',
    cancelled: 'bg-red-500/20 text-red-400 border-red-500/30',
    abandoned: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    paid: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    partial: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    refunded: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    // Resource statuses
    available: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    occupied: 'bg-red-500/20 text-red-400 border-red-500/30',
    reserved: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    maintenance: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  }
  return colors[status] || colors.pending
}
