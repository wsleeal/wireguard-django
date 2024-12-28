// ADICIONAR BOTAO PARA GERAR PEER.CONF
document.addEventListener("DOMContentLoaded", function () {
    const utils = document.getElementById("model-data-utils");
    const submitRow = document.querySelector(".submit-row");
    if (submitRow) {
        const customButton = document.createElement("input");
        customButton.type = "submit";
        customButton.value = "Download config";
        customButton.onclick = function (event) {
            event.preventDefault();
            if (utils) {
                const url = utils.getAttribute("data-url");
                window.location.href = url;
            }
        };

        const saveButton = submitRow.querySelector(
            ".submit-row > input:nth-child(3)"
        );

        if (saveButton) {
            submitRow.insertBefore(customButton, saveButton.nextSibling);
        }
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
