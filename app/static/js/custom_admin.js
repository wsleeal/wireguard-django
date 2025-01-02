// ADICIONAR BOTAO PARA GERAR PEER.CONF
document.addEventListener("DOMContentLoaded", function () {
    const utils = document.getElementById("model-data-utils");
    const submitRow = document.querySelector(".object-tools");
    if (submitRow && utils) {
        console.log("1");
        const custonInput1 = document.createElement("input");
        custonInput1.type = "submit";
        custonInput1.value = "Download config";
        custonInput1.className = "btn btn-block btn-secondary btn-sm";
        custonInput1.onclick = function (event) {
            event.preventDefault();
            const url = utils.getAttribute("data-url");
            window.location.href = url; 
        };

        const custonInput2= document.createElement("input");
        custonInput2.type = "submit";
        custonInput2.value = "Show QRCode";
        custonInput2.className = "btn btn-block btn-secondary btn-sm btn-open-modal";
        custonInput2.onclick = function (event) {
            event.preventDefault();
        
        };
            
        const saveButton = submitRow.querySelector(".btn-block");
        if (saveButton && utils) {            
            submitRow.insertBefore(custonInput2, saveButton.nextSibling);
            submitRow.insertBefore(custonInput1, saveButton.nextSibling);
        }
    }

    document.querySelectorAll(".btn-open-modal").forEach((button) => {
        button.addEventListener("click", function () {
            const modal = document.getElementById("custom-modal");
            modal.style.display = "block";

            if (utils) {
                // URL da página que você deseja buscar
                const url = utils.getAttribute("data-url");

                fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`Erro ao buscar dados: ${response.status}`);
                        }
                        return response.text(); // Para texto simples ou HTML
                    })
                    .then(wireGuardConfig => {
                        const qrcode = document.getElementById("qrcode");
                        qrcode.innerHTML = "";
                        new QRCode(qrcode, {
                            text: wireGuardConfig,
                            width: 256,
                            height: 256
                        });
                    })
                    .catch(error => {
                        console.error('Erro:', error);
                    });
            }
        });
    });

    const modalClose =  document.querySelector(".modal-close");
    if (modalClose) {
        modalClose.addEventListener("click", function () {
            document.getElementById("custom-modal").style.display = "none";
        });
    }
});
