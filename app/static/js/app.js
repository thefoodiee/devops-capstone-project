// Cloud Notes App Client Logic
document.addEventListener("DOMContentLoaded", function () {
    // Populate Edit Note Modal dynamically
    const editModal = document.getElementById("editNoteModal");
    if (editModal) {
        editModal.addEventListener("show.bs.modal", function (event) {
            const button = event.relatedTarget;
            const noteId = button.getAttribute("data-id");
            const title = button.getAttribute("data-title");
            const content = button.getAttribute("data-content");
            const category = button.getAttribute("data-category");
            const isPinned = button.getAttribute("data-pinned") === "true";

            const form = document.getElementById("editNoteForm");
            form.action = `/notes/${noteId}/edit`;

            document.getElementById("editNoteTitle").value = title || "";
            document.getElementById("editNoteContent").value = content || "";
            document.getElementById("editNoteCategory").value = category || "General";
            document.getElementById("editNotePinned").checked = isPinned;
        });
    }

    // Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
});
