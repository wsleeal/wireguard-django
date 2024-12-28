// ADICIONAR BOTAO PARA GERAR PEER.CONF
document.addEventListener("DOMContentLoaded", function () {
    const submitRow = document.querySelector(".submit-row");
    if (submitRow) {
        const custonInput = document.createElement("input");
        custonInput.type = "submit";
        custonInput.value = "Download config";
        custonInput.onclick = function (event) {
            event.preventDefault();
            const utils = document.getElementById("model-data-utils");
            const url = utils.getAttribute("data-url");
            window.location.href = url; 
        };

        const custonButton= document.createElement("input");
        custonButton.type = "submit";
        custonButton.value = "Open Modal";
        custonButton.className = "btn-open-modal";
        custonButton.onclick = (event) => event.preventDefault(); 
        
        const saveButton = submitRow.querySelector(".submit-row > input:nth-child(3)");
        submitRow.insertBefore(custonButton, saveButton.nextSibling);
        submitRow.insertBefore(custonInput, saveButton.nextSibling);
    }

    document.querySelectorAll(".btn-open-modal").forEach((button) => {
        button.addEventListener("click", function () {
            const modal = document.getElementById("custom-modal");
            const id = this.getAttribute("data-id");
            modal.querySelector(".modal-body").innerHTML = `ID do Objeto: ${id}`;
            modal.style.display = "block";
        });
    });

    // Fechar o modal
    document.querySelector(".modal-close").addEventListener("click", function () {
        document.getElementById("custom-modal").style.display = "none";
    });
});
