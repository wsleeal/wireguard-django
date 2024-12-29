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

        const custonInput2= document.createElement("input");
        custonInput2.type = "submit";
        custonInput2.value = "Show QRCode";
        custonInput2.className = "btn-open-modal";
        custonInput2.onclick = function (event) {
            event.preventDefault();
        
        };
            
        const saveButton = submitRow.querySelector(".submit-row > input:nth-child(3)");
        if (saveButton && utils) {            
            submitRow.insertBefore(custonInput2, saveButton.nextSibling);
            submitRow.insertBefore(custonInput1, saveButton.nextSibling);
        }
    }

    document.querySelectorAll(".btn-open-modal").forEach((button) => {
        button.addEventListener("click", function () {
            const modal = document.getElementById("custom-modal");
            const id = this.getAttribute("data-id");

            const wireGuardConfig = `
            [Interface]
            Address = 1.1.1.2
            PrivateKey = MvWgvrgrvDwLSFk7kVBwcsb/DsOIJx8e9mRUN+X9i2Y=
            ListenPort = 51820

            [Peer]
            PublicKey = rT8Z4KP4fdgbMmPZDIQEoNk9mt0F36mMN4BsjnOMckk=
            PresharedKey = k0OEOyRNJ9E9lpdot4GzJT2j87iI5VmQaHv5JNuzJ4Y=
            Endpoint = 152.231.25.14:51820
            AllowedIPs = 1.1.1.2/32, 1.1.1.1/32
            PersistentKeepalive = 25
            `;

            new QRCode(document.getElementById("qrcode"), {
                text: wireGuardConfig,
                width: 256,
                height: 256
            });

            modal.style.display = "block";
        });
    });

    document.querySelector(".modal-close").addEventListener("click", function () {
        document.getElementById("custom-modal").style.display = "none";
    });
});
