import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Users, UserPlus, Shield, Trash2, Loader2, AlertCircle } from 'lucide-react'
import { authApi, type AuthUser, type TeamMembership } from '@/lib/api'
import { useAdminStore, useAuthStore } from '@/lib/store'

interface MemberWithUser extends TeamMembership {
  user?: AuthUser
}

export default function TeamPage() {
  const { businessId } = useAdminStore()
  const { user: currentUser, isAdminOf } = useAuthStore()
  const isAdmin = isAdminOf(businessId)

  const [members, setMembers] = useState<MemberWithUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newUserEmail, setNewUserEmail] = useState('')
  const [newUserRole, setNewUserRole] = useState<'admin' | 'staff'>('staff')
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    loadMembers()
  }, [businessId])

  const loadMembers = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await authApi.getBusinessMembers(businessId)
      setMembers(data || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load team members')
    } finally {
      setLoading(false)
    }
  }

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newUserEmail) return

    try {
      setAdding(true)
      const result = await authApi.assignRole({
        business_id: businessId,
        email: newUserEmail,
        role: newUserRole
      })

      // Reload members to get full user details
      await loadMembers()

      setShowAddModal(false)
      setNewUserEmail('')
      setNewUserRole('staff')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add member')
    } finally {
      setAdding(false)
    }
  }

  const handleRemoveMember = async (userId: string) => {
    if (!confirm('Are you sure you want to remove this team member?')) return

    try {
      await authApi.removeRole(businessId, userId)
      setMembers(members.filter(m => m.userId !== userId))
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to remove member')
    }
  }

  const handleChangeRole = async (userId: string, newRole: 'admin' | 'staff') => {
    try {
      await authApi.assignRole({ business_id: businessId, user_id: userId, role: newRole })
      setMembers(members.map(m =>
        m.userId === userId ? { ...m, role: newRole } : m
      ))
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to change role')
    }
  }

  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Shield className="w-16 h-16 text-amber-400 mx-auto mb-4" />
          <h2 className="font-display text-2xl font-semibold mb-2">Admin Access Required</h2>
          <p className="text-white/60">Only admins can manage team members</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-12 h-12 text-brand-400 animate-spin" />
      </div>
    )
  }

  return (
    <div>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8 flex items-center justify-between"
      >
        <div>
          <h1 className="font-display text-3xl font-bold mb-2">Team Management</h1>
          <p className="text-white/60">Manage team members and their roles</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 bg-brand-500 hover:bg-brand-400 text-white rounded-xl flex items-center gap-2 transition-colors font-medium"
        >
          <UserPlus className="w-5 h-5" />
          Add Member
        </button>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-red-400 flex items-center gap-3"
        >
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card"
      >
        <div className="p-6 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Users className="w-5 h-5 text-white/60" />
            <h2 className="font-semibold">Team Members</h2>
            <span className="text-white/40 text-sm">({members.length})</span>
          </div>
        </div>

        <div className="divide-y divide-white/10">
          {members.length === 0 ? (
            <div className="p-12 text-center text-white/40">
              <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No team members yet</p>
            </div>
          ) : (
            members.map((member) => (
              <motion.div
                key={member.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-4 flex items-center gap-4 hover:bg-white/5 transition-colors"
              >
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center text-white font-semibold text-lg">
                  {member.user?.name?.charAt(0) || '?'}
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{member.user?.name || 'Unknown'}</span>
                    {member.userId === currentUser?.id && (
                      <span className="px-2 py-0.5 text-xs bg-brand-500/20 text-brand-400 rounded-full">You</span>
                    )}
                  </div>
                  <p className="text-white/60 text-sm">{member.user?.email}</p>
                </div>

                <div className="flex items-center gap-3">
                  <select
                    value={member.role}
                    onChange={(e) => handleChangeRole(member.userId, e.target.value as 'admin' | 'staff')}
                    disabled={member.userId === currentUser?.id}
                    className="bg-surface-800 border border-white/10 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400 disabled:opacity-50"
                  >
                    <option value="admin">Admin</option>
                    <option value="staff">Staff</option>
                  </select>

                  {member.userId !== currentUser?.id && (
                    <button
                      onClick={() => handleRemoveMember(member.userId)}
                      className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </motion.div>
            ))
          )}
        </div>
      </motion.div>

      <div className="mt-6 p-4 bg-white/5 rounded-xl border border-white/10">
        <p className="text-white/60 text-sm">
          <strong className="text-white">Note:</strong> To add new team members, they first need to sign up on the platform.
          Then you can find them by their email and assign them a role.
        </p>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-surface-900 border border-white/10 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl"
          >
            <div className="p-6 border-b border-white/10">
              <h3 className="font-display text-xl font-bold">Add Team Member</h3>
            </div>

            <form onSubmit={handleAddMember} className="p-6 space-y-4">
              <div>
                <label className="block text-sm text-white/60 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={newUserEmail}
                  onChange={(e) => setNewUserEmail(e.target.value)}
                  placeholder="Enter user email"
                  className="w-full bg-surface-800 border border-white/10 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand-400"
                />
                <p className="text-xs text-white/40 mt-1">User must already have an account</p>
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-1">Role</label>
                <select
                  value={newUserRole}
                  onChange={(e) => setNewUserRole(e.target.value as 'admin' | 'staff')}
                  className="w-full bg-surface-800 border border-white/10 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand-400"
                >
                  <option value="staff">Staff</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div className="pt-4 flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 px-4 py-2 rounded-xl border border-white/10 hover:bg-white/5 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={adding}
                  className="flex-1 px-4 py-2 bg-brand-500 hover:bg-brand-400 text-white rounded-xl font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {adding && <Loader2 className="w-4 h-4 animate-spin" />}
                  Add Member
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  )
}
