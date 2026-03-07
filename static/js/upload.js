// let dropArea = document.getElementById("drop-area")
//
// dropArea.addEventListener("dragover", (e)=>{
// e.preventDefault()
// })
//
// dropArea.addEventListener("drop", (e)=>{
// e.preventDefault()
//
// let fileInput = document.getElementById("fileElem")
//
// fileInput.files = e.dataTransfer.files
// })
//
// let form = document.getElementById("uploadForm")
//
// form.addEventListener("submit", function(e){
//
// e.preventDefault()
//
// let formData = new FormData(form)
//
// let xhr = new XMLHttpRequest()
//
// xhr.open("POST","/upload",true)
//
// xhr.upload.onprogress = function(e){
//
// if(e.lengthComputable){
//
// let percent = (e.loaded/e.total)*100
//
// document.getElementById("progress").style.width = percent+"%"
//
// }
//
// }
//
// xhr.onload = function(){
// location.reload()
// }
//
// xhr.send(formData)
//
// })


let dropArea = document.getElementById("drop-area");

dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.style.borderColor = "#4a90e2";
});

dropArea.addEventListener("dragleave", () => {
    dropArea.style.borderColor = "#ccc";
});

dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.style.borderColor = "#ccc";

    let fileInput = document.getElementById("fileElem");
    fileInput.files = e.dataTransfer.files;
});

let form = document.getElementById("uploadForm");

form.addEventListener("submit", function (e) {
    e.preventDefault();

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