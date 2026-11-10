import { ref, computed } from 'vue'

export interface Retailer {
  id: string
  name: string
  slug: string
  website_domain?: string | null
  logo_url?: string | null
  supports_cod: boolean
  return_policy_url?: string | null
  status: 'pending' | 'verified' | 'suspended'
  created_at?: string
}

export interface RetailerMember {
  id: string
  retailer_id: string
  user_id: string
  member_role: 'owner' | 'editor'
  created_at?: string
}

export const useRetailer = () => {
  const supabase = useSupabaseClient()
  const user = useSupabaseUser()
  const currentRetailer = useState<Retailer | null>('fitsense_current_retailer', () => null)
  const currentMember = useState<RetailerMember | null>('fitsense_current_member', () => null)
  const userRole = useState<string>('fitsense_user_role', () => 'customer')
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isOwner = computed(() => currentMember.value?.member_role === 'owner' || userRole.value === 'admin')
  const isVerified = computed(() => currentRetailer.value?.status === 'verified')
  const isPending = computed(() => currentRetailer.value?.status === 'pending')

  const fetchRetailerProfile = async (): Promise<Retailer | null> => {
    if (!user.value) {
      currentRetailer.value = null
      currentMember.value = null
      return null
    }

    loading.value = true
    error.value = null

    try {
      // 1. Fetch user profile role
      const { data: profile } = await supabase
        .from('profiles')
        .select('role')
        .eq('user_id', user.value.id)
        .single<{ role: string }>()

      if ((profile as any)?.role) {
        userRole.value = (profile as any).role
      }

      // 2. Fetch retailer membership
      const { data: membership, error: memberErr } = await supabase
        .from('retailer_members')
        .select('*')
        .eq('user_id', user.value.id)
        .limit(1)
        .maybeSingle<RetailerMember>()

      if (memberErr || !membership) {
        currentMember.value = null
        currentRetailer.value = null
        return null
      }

      currentMember.value = membership as RetailerMember

      // 3. Fetch retailer data
      const { data: retData, error: retErr } = await supabase
        .from('retailers')
        .select('*')
        .eq('id', (membership as any).retailer_id)
        .single<Retailer>()

      if (retErr || !retData) {
        currentRetailer.value = null
        return null
      }

      currentRetailer.value = retData as Retailer
      return retData as Retailer
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch retailer profile'
      return null
    } finally {
      loading.value = false
    }
  }

  const createRetailer = async (form: {
    name: string
    slug: string
    website_domain?: string
    supports_cod: boolean
    return_policy_url?: string
  }): Promise<{ success: boolean; retailer?: Retailer; error?: string }> => {
    if (!user.value) return { success: false, error: 'User must be signed in' }

    loading.value = true
    error.value = null

    try {
      // 1. Insert retailer (defaults to status: 'pending')
      const { data: retailer, error: retErr } = await (supabase.from('retailers') as any)
        .insert({
          name: form.name.trim(),
          slug: form.slug.trim().toLowerCase(),
          website_domain: form.website_domain?.trim() || null,
          supports_cod: form.supports_cod,
          return_policy_url: form.return_policy_url?.trim() || null,
          status: 'pending',
        })
        .select()
        .single()

      if (retErr || !retailer) {
        throw new Error(retErr?.message || 'Failed to create retailer record.')
      }

      // 2. Update user profile role to 'retailer' (if not already admin)
      if (userRole.value !== 'admin') {
        try {
          await (supabase.from('profiles') as any)
            .update({ role: 'retailer' })
            .eq('user_id', user.value.id)
          userRole.value = 'retailer'
        } catch {
          // Silently ignore if RLS trigger prevents non-admins from changing profiles.role
        }
      }

      // 3. Ensure membership is recorded
      const { data: member } = await (supabase.from('retailer_members') as any)
        .upsert(
          {
            retailer_id: (retailer as any).id,
            user_id: user.value.id,
            member_role: 'owner',
          },
          { onConflict: 'retailer_id,user_id' }
        )
        .select()
        .single()

      currentRetailer.value = retailer as Retailer
      if (member) currentMember.value = member as RetailerMember

      return { success: true, retailer: retailer as Retailer }
    } catch (err: any) {
      error.value = err.message || 'Error creating retailer'
      return { success: false, error: error.value ?? undefined }
    } finally {
      loading.value = false
    }
  }

  return {
    currentRetailer,
    currentMember,
    userRole,
    isOwner,
    isVerified,
    isPending,
    loading,
    error,
    fetchRetailerProfile,
    createRetailer,
  }
}
