// ADICIONAR BOTAO PARA GERAR PEER.CONF
document.addEventListener("DOMContentLoaded", function () {
    const utils = document.getElementById("model-data-utils");
    const submitRow = document.querySelector(".submit-row");
    if (submitRow) {
        const custonInput1 = document.createElement("input");
        custonInput1.type = "submit";
        custonInput1.value = "Download config";
        custonInput1.onclick = function (event) {
            event.preventDefault();
            const url = utils.getAttribute("data-url");
            window.location.href = url; 
        };

//         const custonInput2= document.createElement("input");
//         custonInput2.type = "submit";
//         custonInput2.value = "Open Modal";
//         custonInput2.className = "btn-open-modal";
//         custonInput2.onclick = (event) => event.preventDefault(); 
        
        const saveButton = submitRow.querySelector(".submit-row > input:nth-child(3)");
        if (saveButton && utils) {            
            // submitRow.insertBefore(custonInput2, saveButton.nextSibling);
            submitRow.insertBefore(custonInput1, saveButton.nextSibling);
        }
    }

//     document.querySelectorAll(".btn-open-modal").forEach((button) => {
//         button.addEventListener("click", function () {
//             const modal = document.getElementById("custom-modal");
//             const id = this.getAttribute("data-id");
//             modal.querySelector(".modal-body").innerHTML = `ID do Objeto: ${id}`;
//             modal.style.display = "block";
//         });
//     });

//     // Fechar o modal
//     document.querySelector(".modal-close").addEventListener("click", function () {
//         document.getElementById("custom-modal").style.display = "none";
//     });
});
