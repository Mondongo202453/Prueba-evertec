const processUrlElement = document.querySelector("meta[name='placetopay-process-url']");
const processUrl = processUrlElement?.content;

if (processUrl && typeof P !== "undefined") {
    P.init(processUrl);

    P.on("response", function(response) {
        if (!response || !response.requestId) {
            console.error("La respuesta no contiene requestId");
            alert("No fue posible identificar la transacción.");
            return;
        }

        window.location.href =
            "/resultado?requestId=" +
            encodeURIComponent(response.requestId);
    });
}
