export default defineNuxtRouteMiddleware(async () => {
  const user = useSupabaseUser()
  const localePath = useLocalePath()
  const supabase = useSupabaseClient()

  if (!user.value) {
    return navigateTo(localePath('/login'))
  }

  // Fetch role directly from profiles to enforce real role check
  const { data: profile } = await supabase
    .from('profiles')
    .select('role')
    .eq('user_id', user.value.id)
    .single<{ role: string }>()

  if (!profile || (profile as { role?: string }).role !== 'admin') {
    return navigateTo(localePath('/'))
  }
})
