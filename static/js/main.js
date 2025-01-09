async function openSettingsModal() {
    const modal = document.getElementById('settings-modal');
    const nameInput = document.getElementById('name-input');
    const hiddenAddressField = document.getElementById("hiddenWalletAddress");
    const walletAddress = hiddenAddressField.value;

    if (!walletAddress) {
        alert("Wallet address is missing.");
        return;
    }

    try {
        // Fetch user details
        const response = await fetch('http://localhost:5000/get-user-details', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallet_address: walletAddress })
        });

        const result = await response.json();
        if (result.success) {
            // Prefill the name input with the current name
            nameInput.value = result.user.name || '';
        } else {
            alert(`Error fetching user details: ${result.error || "Unknown error"}`);
            nameInput.value = ''; // Clear the input field if no user found
        }

        // Show the modal
        modal.classList.remove('hidden');
    } catch (error) {
        console.error("Error fetching user details:", error);
    }
}

function closeSettingsModal() {
    document.getElementById('settings-modal').classList.add('hidden');
}

async function saveSettings() {
    const nameInput = document.getElementById('name-input').value;

    if (!nameInput.trim()) {
        alert("Name cannot be empty.");
        return;
    }

    try {
        const hiddenAddressField = document.getElementById("hiddenWalletAddress")
        const walletAddress = hiddenAddressField.value;

        const response = await fetch('http://localhost:5000/update-record', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallet_address: walletAddress, name: nameInput })
        });

        const result = await response.json();
        if (result.success) {
            closeSettingsModal();

            // Refresh the leaderboard
            const leaderboardBody = document.getElementById('leaderboard-body');
            leaderboardBody.innerHTML = ''; // Clear existing content
            const updateResponse = await fetch('http://localhost:5000/update-leaderboard');
            leaderboardBody.innerHTML = await updateResponse.text();
        } else {
            alert(`Error updating settings: ${result.error || "Unknown error"}`);
        }
    } catch (error) {
        console.error("Error updating settings:", error);
    }
}

async function signInWithWallet() {
    if (!window.solana || !window.solana.isPhantom) {
        alert("Phantom Wallet is not installed.");
        return;
    }

    try {
        // Connect to the wallet
        const response = await window.solana.connect();
        const walletAddress = response.publicKey.toString();

        // Fetch a message to sign
        const messageResponse = await fetch('http://localhost:5000/generate-message');
        const { message } = await messageResponse.json();

        // Sign the message
        const encodedMessage = new TextEncoder().encode(message);
        const signedMessage = await window.solana.signMessage(encodedMessage, "utf8");

        // Send the signature to the backend
        const verifyResponse = await fetch('http://localhost:5000/verify-signature', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                wallet_address: walletAddress,
                message: message,
                signature: signedMessage.signature
            })
        });

        const verifyResult = await verifyResponse.json();
        if (verifyResult.success) {
            // Update Connect button text
            const connectButton = document.getElementById('connect-button');
            connectButton.textContent = `${walletAddress.slice(0, 5)}...`;

            // Enable the settings cogwheel
            const settingsButton = document.getElementById('settings-button');
            settingsButton.classList.remove('bg-gray-300', 'text-gray-400', 'cursor-not-allowed');
            settingsButton.classList.add('bg-gray-100', 'text-gray-800', 'hover:bg-gray-200');
            settingsButton.disabled = false;

            // Add the wallet address to mock_data.json
            const addRecordResponse = await fetch('http://localhost:5000/add-record', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wallet_address: walletAddress })
            });

            const hiddenAddressField = document.getElementById('hiddenWalletAddress');
            hiddenAddressField.value = walletAddress;

            const addRecordResult = await addRecordResponse.json();
            if (addRecordResult.success) {
                console.log("Record added:", addRecordResult.message);
            } else {
                console.warn("Could not add record:", addRecordResult.message || addRecordResult.error);
            }
        } else {
            alert("Signature verification failed: " + verifyResult.error);
        }
    } catch (error) {
        console.error("Wallet signing error:", error);
    }
}