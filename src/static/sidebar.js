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