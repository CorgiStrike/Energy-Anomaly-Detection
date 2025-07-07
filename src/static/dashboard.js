const input = document.getElementById('file-upload');
if (input) {
    input.addEventListener('change', () => {
        const msg = document.createElement('div');
        msg.innerHTML = "Processing...";
        msg.style.color = "white";
        msg.style.marginTop = "1em";
        document.body.appendChild(msg);
    });
}

const toggleBtn = document.getElementById('toggleAlertsBtn');
const alertDiv = document.getElementById('combinedAlert');
if (toggleBtn && alertDiv) {
    toggleBtn.addEventListener('click', () => {
        const visible = alertDiv.style.display !== 'none';
        alertDiv.style.display = visible ? 'none' : 'block';
        toggleBtn.textContent = visible ? 'Show alerts' : 'Hide alerts';
    });
}