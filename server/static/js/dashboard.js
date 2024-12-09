// Ensure the DOM is fully loaded before executing scripts
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await initializeDashboard();
    } catch (error) {
        console.error("Error initializing dashboard:", error);
    }
});

// Initialize the dashboard
async function initializeDashboard() {
    try {
        // Set the client name dynamically (replace with API call if needed)
        const clientName = await fetchClientName();
        updateClientName(clientName);

        // Fetch and display the initial blocked count
        const blockedCount = await fetchBlockedCount();
        updateBlockedCount(blockedCount);
    } catch (error) {
        console.error("Error during initialization:", error);
    }
}

// Fetch the client name (simulate or replace with API call)
async function fetchClientName() {
    // Simulated fetch logic
    return "Client Site 1";
}

// Fetch the blocked count (simulate or replace with API call)
async function fetchBlockedCount() {
    // Simulated fetch logic
    return 0; // Replace with real blocked count from the server
}

// Update the client name in the DOM
function updateClientName(clientName) {
    const clientNameElement = document.getElementById('client-name');
    if (clientNameElement) {
        clientNameElement.textContent = clientName;
    }
}

// Update the blocked count in the DOM
function updateBlockedCount(blockedCount) {
    const blockedCountElement = document.getElementById('blocked-count');
    if (blockedCountElement) {
        blockedCountElement.textContent = blockedCount;
    }
}

// Handler for setting traffic limit
document.getElementById('set-limit-btn').addEventListener('click', async () => {
    const trafficLimitInput = document.getElementById('traffic-limit');
    const trafficLimit = trafficLimitInput.value;

    if (!trafficLimit || isNaN(trafficLimit) || Number(trafficLimit) <= 0) {
        alert("Please enter a valid traffic limit greater than zero.");
        return;
    }

    try {
        await setTrafficLimit(trafficLimit); // Replace with an API call
        alert(`Traffic limit of ${trafficLimit} has been set successfully.`);
        trafficLimitInput.value = ""; // Clear input field
    } catch (error) {
        console.error("Error setting traffic limit:", error);
        alert("Failed to set traffic limit. Please try again.");
    }
});

// Set traffic limit (simulate or replace with API call)
async function setTrafficLimit(limit) {
    // Simulated API call delay
    return new Promise((resolve) => setTimeout(resolve, 500));
}

// Handler for starting the service
document.getElementById('start-service-btn').addEventListener('click', async () => {
    try {
        await startService(); // Replace with an API call
        alert("Service has been started for the selected client site.");
    } catch (error) {
        console.error("Error starting service:", error);
        alert("Failed to start service. Please try again.");
    }
});

// Start the service (simulate or replace with API call)
async function startService() {
    // Simulated API call delay
    return new Promise((resolve) => setTimeout(resolve, 500));
}

// Periodic updates for blocked count
setInterval(async () => {
    try {
        const newBlockedCount = await fetchBlockedCount(); // Replace with real-time API call
        updateBlockedCount(newBlockedCount);
    } catch (error) {
        console.error("Error fetching blocked count:", error);
    }
}, 5000); // Update every 5 seconds
