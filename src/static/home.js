document.querySelectorAll('.rename-btn').forEach(button => {
    button.addEventListener('click', event => {
        event.preventDefault();
        const workflowId = button.getAttribute('data-workflow-id');
        const workflowName = button.getAttribute('data-workflow-name');

        document.getElementById('renameWorkflowId').value = workflowId;
        document.getElementById('newNameInput').value = workflowName;

        const renameModal = new bootstrap.Modal(document.getElementById('renameModal'));
        renameModal.show();
    });
});

document.getElementById('renameForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const workflowId = document.getElementById('renameWorkflowId').value;
    const newName = document.getElementById('newNameInput').value;

    const formData = new FormData();
    formData.append('new_name', newName);

    try {
        const response = await fetch(`/workflow/rename/${workflowId}`, {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            location.reload();
        } else {
            alert('Failed to rename workflow.');
        }
    } catch (error) {
        alert('An error occurred.');
        console.error(error);
    }
});