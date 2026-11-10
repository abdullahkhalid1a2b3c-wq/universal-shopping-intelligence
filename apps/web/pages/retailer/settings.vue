<template>
  <div class="min-h-screen bg-gray-50/50 dark:bg-gray-950 pb-20">
    <RetailerNav />

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      <!-- Retailer Profile Settings -->
      <div class="bg-white dark:bg-gray-800 rounded-3xl p-6 sm:p-8 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="flex items-center justify-between pb-4 border-b border-gray-100 dark:border-gray-700 mb-6">
          <div>
            <h2 class="text-lg font-bold text-gray-900 dark:text-white">Brand Profile Settings</h2>
            <p class="text-xs text-gray-400">Manage your official store details, domain, and return policies.</p>
          </div>
          <span :class="[
            'text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wider',
            currentRetailer?.status === 'verified' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300' :
            currentRetailer?.status === 'pending' ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300' :
            'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
          ]">
            Status: {{ currentRetailer?.status }}
          </span>
        </div>

        <form @submit.prevent="updateProfile" class="space-y-5">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                Retailer Name
              </label>
              <input
                v-model="profileForm.name"
                type="text"
                required
                class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                Store Slug
              </label>
              <input
                v-model="profileForm.slug"
                type="text"
                disabled
                class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800/60 text-sm font-mono text-gray-400 cursor-not-allowed"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                Website Domain
              </label>
              <input
                v-model="profileForm.website_domain"
                type="text"
                placeholder="e.g. brand.pk"
                class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                Brand Logo URL
              </label>
              <input
                v-model="profileForm.logo_url"
                type="url"
                placeholder="https://brand.pk/logo.png"
                class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
              Return Policy URL
            </label>
            <input
              v-model="profileForm.return_policy_url"
              type="url"
              placeholder="https://brand.pk/returns"
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div class="flex items-center gap-3 p-3.5 rounded-xl border border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/40">
            <input
              v-model="profileForm.supports_cod"
              id="settings_cod"
              type="checkbox"
              class="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500"
            />
            <label for="settings_cod" class="text-xs font-medium text-gray-800 dark:text-gray-200 cursor-pointer">
              Store supports Cash on Delivery (COD) shipping across Pakistan
            </label>
          </div>

          <div class="pt-3 flex justify-end">
            <button
              type="submit"
              :disabled="savingProfile || !isOwner"
              class="px-6 py-2.5 rounded-xl bg-indigo-600 text-white font-semibold text-xs hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-sm flex items-center gap-2"
            >
              <span v-if="savingProfile" class="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></span>
              <span>Save Profile Changes</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Team Members Management -->
      <div class="bg-white dark:bg-gray-800 rounded-3xl p-6 sm:p-8 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="flex items-center justify-between pb-4 border-b border-gray-100 dark:border-gray-700 mb-6">
          <div>
            <h2 class="text-lg font-bold text-gray-900 dark:text-white">Team Members</h2>
            <p class="text-xs text-gray-400">Collaborators who can edit size charts and product catalogue.</p>
          </div>

          <button
            v-if="isOwner"
            @click="showAddMemberModal = true"
            class="px-3.5 py-2 rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-semibold text-xs hover:bg-indigo-100 flex items-center gap-1.5"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
            <span>Add Member</span>
          </button>
        </div>

        <div v-if="loadingMembers" class="py-6 text-center text-xs text-gray-400">
          Loading team members...
        </div>

        <div v-else class="divide-y divide-gray-100 dark:divide-gray-700">
          <div
            v-for="member in teamMembers"
            :key="member.id"
            class="py-4 flex items-center justify-between"
          >
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center font-bold text-xs uppercase text-gray-600 dark:text-gray-300">
                {{ (member.profiles?.display_name || 'U').slice(0, 2) }}
              </div>
              <div>
                <div class="font-semibold text-sm text-gray-900 dark:text-white">
                  {{ member.profiles?.display_name || 'User' }}
                </div>
                <div class="text-xs text-gray-400">
                  Role: <span class="capitalize font-medium text-gray-600 dark:text-gray-300">{{ member.member_role }}</span> · Joined {{ new Date(member.created_at).toLocaleDateString() }}
                </div>
              </div>
            </div>

            <div v-if="isOwner && member.member_role !== 'owner'">
              <button
                @click="removeMember(member.id)"
                class="text-xs text-rose-500 hover:text-rose-700 font-medium p-1"
              >
                Remove
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Member Modal -->
    <div v-if="showAddMemberModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-3xl max-w-md w-full p-6 border border-gray-100 dark:border-gray-700 shadow-2xl">
        <div class="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-gray-700 mb-4">
          <h3 class="font-bold text-sm text-gray-900 dark:text-white">Add Team Editor</h3>
          <button @click="showAddMemberModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <form @submit.prevent="submitAddMember" class="space-y-4 text-xs">
          <p class="text-gray-500">
            Enter the registered email of an existing FitSense user to add them as an editor.
          </p>

          <div>
            <label class="block font-semibold mb-1 text-gray-700 dark:text-gray-300">User Email</label>
            <input
              v-model="newMemberEmail"
              type="email"
              required
              placeholder="colleague@brand.pk"
              class="w-full px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label class="block font-semibold mb-1 text-gray-700 dark:text-gray-300">Role</label>
            <select
              v-model="newMemberRole"
              class="w-full px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900"
            >
              <option value="editor">Editor (Can edit products & charts)</option>
              <option value="owner">Owner (Full admin rights)</option>
            </select>
          </div>

          <div class="flex justify-end gap-2 pt-3">
            <button
              type="button"
              @click="showAddMemberModal = false"
              class="px-4 py-2 rounded-xl border text-gray-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="addingMember || !newMemberEmail"
              class="px-5 py-2 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-1.5"
            >
              <span v-if="addingMember" class="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></span>
              <span>Add Member</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

definePageMeta({
  middleware: ['retailer'],
})

const { currentRetailer, isOwner, fetchRetailerProfile } = useRetailer()
const { showToast } = useToast()
const { apiFetch } = useApi()
const supabase = useSupabaseClient()

const savingProfile = ref(false)
const loadingMembers = ref(true)
const teamMembers = ref<any[]>([])

const showAddMemberModal = ref(false)
const newMemberEmail = ref('')
const newMemberRole = ref('editor')
const addingMember = ref(false)

const profileForm = reactive({
  name: '',
  slug: '',
  website_domain: '',
  logo_url: '',
  return_policy_url: '',
  supports_cod: true,
})

const loadSettings = async () => {
  if (!currentRetailer.value) {
    await fetchRetailerProfile()
  }
  if (!currentRetailer.value) return

  profileForm.name = currentRetailer.value.name
  profileForm.slug = currentRetailer.value.slug
  profileForm.website_domain = currentRetailer.value.website_domain || ''
  profileForm.logo_url = currentRetailer.value.logo_url || ''
  profileForm.return_policy_url = currentRetailer.value.return_policy_url || ''
  profileForm.supports_cod = currentRetailer.value.supports_cod

  // Fetch team members
  loadingMembers.value = true
  try {
    const { data: members, error } = await supabase
      .table('retailer_members')
      .select('id, user_id, member_role, created_at, profiles(display_name, preferred_language)')
      .eq('retailer_id', currentRetailer.value.id)

    if (error) throw error
    teamMembers.value = members || []
  } catch (err: any) {
    showToast(err.message || 'Failed to load team members', 'error')
  } finally {
    loadingMembers.value = false
  }
}

onMounted(() => {
  loadSettings()
})

const updateProfile = async () => {
  if (!currentRetailer.value) return
  savingProfile.value = true

  try {
    const { error } = await supabase
      .table('retailers')
      .update({
        name: profileForm.name.trim(),
        website_domain: profileForm.website_domain.trim() || null,
        logo_url: profileForm.logo_url.trim() || null,
        return_policy_url: profileForm.return_policy_url.trim() || null,
        supports_cod: profileForm.supports_cod,
      })
      .eq('id', currentRetailer.value.id)

    if (error) throw error
    showToast('Brand settings updated successfully', 'success')
    fetchRetailerProfile()
  } catch (err: any) {
    showToast(err.message || 'Failed to update brand profile', 'error')
  } finally {
    savingProfile.value = false
  }
}

const submitAddMember = async () => {
  if (!currentRetailer.value || !newMemberEmail.value) return
  addingMember.value = true

  try {
    await apiFetch('/v1/retailer/members', {
      method: 'POST',
      body: {
        retailer_id: currentRetailer.value.id,
        email: newMemberEmail.value.trim(),
        member_role: newMemberRole.value,
      },
    })

    showToast(`User ${newMemberEmail.value} added as ${newMemberRole.value}`, 'success')
    showAddMemberModal.value = false
    newMemberEmail.value = ''
    loadSettings()
  } catch (err: any) {
    showToast(err.message || 'Failed to add member. Ensure user exists.', 'error')
  } finally {
    addingMember.value = false
  }
}

const removeMember = async (memberId: string) => {
  if (!confirm('Remove this collaborator from the retailer team?')) return
  try {
    const { error } = await supabase.table('retailer_members').delete().eq('id', memberId)
    if (error) throw error
    teamMembers.value = teamMembers.value.filter((m) => m.id !== memberId)
    showToast('Member removed', 'success')
  } catch (err: any) {
    showToast(err.message || 'Failed to remove member', 'error')
  }
}
</script>
