const toggleButton = document.getElementsByClassName("hamburger")[0];
const sidebar = document.getElementById("sidebar");
const mainContent = document.getElementById("mainContent");

toggleButton.addEventListener("click", () => {
    sidebar.classList.toggle("expanded");
    sidebar.classList.toggle("collapsed");

    if (sidebar.classList.contains("expanded")) {
        mainContent.style.marginLeft = "220px";
    } else {
        mainContent.style.marginLeft = "60px";
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('themeToggle');
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme === 'light') {
        document.body.classList.add('light-mode');
    }

    toggleButton.addEventListener('click', () => {
        document.body.classList.toggle('light-mode');
        const isLight = document.body.classList.contains('light-mode');
        localStorage.setItem('theme', isLight ? 'light' : 'dark');
    });
});