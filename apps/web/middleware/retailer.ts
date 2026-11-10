export default defineNuxtRouteMiddleware(async (to) => {
  const user = useSupabaseUser()
  const localePath = useLocalePath()

  if (!user.value) {
    return navigateTo(localePath('/login'))
  }

  const { fetchRetailerProfile, currentRetailer, userRole } = useRetailer()
  
  if (!currentRetailer.value) {
    await fetchRetailerProfile()
  }

  // If user is accessing an existing retailer page but has no retailer created yet,
  // redirect them to onboarding unless they are already heading to onboarding
  if (!currentRetailer.value && !to.path.includes('/retailer/onboarding') && userRole.value !== 'admin') {
    return navigateTo(localePath('/retailer/onboarding'))
  }
})
