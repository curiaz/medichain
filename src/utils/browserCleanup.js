/**
 * Browser Console Utility for Quick Data Cleanup
 * Run this in the browser console to clear local data
 */

// Quick cleanup function for browser console
window.quickCleanup = () => {
  console.log('🧹 Starting quick cleanup...');
  
  // Clear localStorage
  localStorage.clear();
  console.log('✅ localStorage cleared');
  
  // Clear sessionStorage
  sessionStorage.clear();
  console.log('✅ sessionStorage cleared');
  
  // Clear specific cookies if any
  document.cookie.split(";").forEach(function(c) { 
    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
  });
  console.log('✅ Cookies cleared');
  
  // Clear indexedDB if used
  if (window.indexedDB) {
    indexedDB.databases().then(databases => {
      databases.forEach(db => {
        indexedDB.deleteDatabase(db.name);
      });
    }).catch(() => {
      console.log('ℹ️ IndexedDB cleanup skipped');
    });
  }
  
  console.log('✅ Quick cleanup completed');
  console.log('🔄 Reloading page in 2 seconds...');
  
  setTimeout(() => {
    window.location.reload();
  }, 2000);
};

// Show usage instructions
console.log(`
🧹 MediChain Browser Data Cleanup Utility
==========================================

To clear all local data, run:
> quickCleanup()

This will clear:
- localStorage
- sessionStorage  
- Cookies
- IndexedDB (if used)

The page will reload automatically after cleanup.
`);

export default window.quickCleanup;