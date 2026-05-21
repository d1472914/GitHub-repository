document.addEventListener('DOMContentLoaded', () => {
    // Simulate the local client version.
    // In a real app, this might come from localStorage or build config.
    // We set it to 1.0 to simulate an outdated client.
    const LOCAL_VERSION = "1.0";
    
    // Function to check version against the server
    async function checkVersion() {
        try {
            console.log(`Current Local Version: ${LOCAL_VERSION}`);
            console.log('Checking with server for minimum required version...');
            
            const response = await fetch('/api/version');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            const minRequiredVersion = data.min_version;
            
            console.log(`Server requires version: ${minRequiredVersion}`);
            
            // Simple version comparison (assuming format like "1.0", "2.0")
            if (parseFloat(LOCAL_VERSION) < parseFloat(minRequiredVersion)) {
                console.warn('Version is outdated! Triggering lock mechanism.');
                triggerVersionLock();
            } else {
                console.log('Version is up to date.');
            }
            
        } catch (error) {
            console.error('Failed to check version:', error);
            // In a production app, you might want to handle network failures gracefully.
        }
    }
    
    // Function to lock the UI and show the modal
    function triggerVersionLock() {
        // Lock the body background (applies blur and pointer-events: none to main content)
        document.body.classList.add('locked');
        
        // Show the modal
        const modal = document.getElementById('version-lock-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }
    
    // Execute the version check
    checkVersion();
});
