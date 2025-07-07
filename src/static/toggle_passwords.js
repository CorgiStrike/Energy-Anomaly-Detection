function togglePasswords() {
    const passwordFields = document.querySelectorAll('.sync-password');
    passwordFields.forEach(input => {
        input.type = input.type === 'password' ? 'text' : 'password';
    });

    const icons = document.querySelectorAll('.toggle-icon i');
    icons.forEach(icon => {
        if (icon.classList.contains('bi-eye')) {
            icon.classList.remove('bi-eye');
            icon.classList.add('bi-eye-slash');
        } else {
            icon.classList.remove('bi-eye-slash');
            icon.classList.add('bi-eye');
        }
    });
}