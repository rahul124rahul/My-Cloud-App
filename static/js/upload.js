/* ===== Drag & Drop ===== */
let dropArea = document.getElementById("drop-area");
let fileInput = document.getElementById("fileElem");
let fileLabel = document.getElementById("file-chosen-name");

if (dropArea && fileInput) {
    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropArea.classList.add("drag-over");
    });

    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("drag-over");
    });

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.classList.remove("drag-over");
        fileInput.files = e.dataTransfer.files;
        if (fileLabel && fileInput.files.length) {
            fileLabel.textContent = fileInput.files[0].name;
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileLabel && fileInput.files.length) {
            fileLabel.textContent = fileInput.files[0].name;
        }
    });
}

/* ===== Upload with Progress ===== */
let form = document.getElementById("uploadForm");

if (form) {
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        let fi = document.getElementById("fileElem");
        if (!fi.files.length) {
            alert("Please select a file first.");
            return;
        }

        let formData = new FormData(form);
        let xhr = new XMLHttpRequest();

        xhr.open("POST", "/upload", true);

        xhr.upload.onprogress = function (e) {
            if (e.lengthComputable) {
                let percent = (e.loaded / e.total) * 100;
                document.getElementById("progress").style.width = percent + "%";
            }
        };

        xhr.onload = function () {
            location.reload();
        };

        xhr.send(formData);
    });
}

/* ===== Rename Modal ===== */
function openRename(fileId, currentName) {
    document.getElementById("renameFileId").value = fileId;
    document.getElementById("renameInput").value = currentName;
    document.getElementById("renameModal").style.display = "flex";
    setTimeout(() => document.getElementById("renameInput").focus(), 100);
}

function closeRename() {
    document.getElementById("renameModal").style.display = "none";
}

// Close modal on Escape key
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeRename();
});

// Close modal on clicking overlay background
let overlay = document.getElementById("renameModal");
if (overlay) {
    overlay.addEventListener("click", (e) => {
        if (e.target === overlay) closeRename();
    });
}