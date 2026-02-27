(function () {
    function getValue(id) {
        const node = document.getElementById(id);
        return node ? node.value : "";
    }

    window.selectVehicle = function selectVehicle(vehicleId, vehicleName, pricePerDay) {
        const token = localStorage.getItem("access_token");

        if (!token) {
            if (window.confirm("Debes iniciar sesión para hacer una reservación. ¿Deseas ir al login?")) {
                window.location.href = "/login";
            }
            return;
        }

        const reservationData = {
            vehicle_id: Number(vehicleId),
            vehicle_name: String(vehicleName || ""),
            price_per_day: Number(pricePerDay || 0),
            origin: getValue("origen"),
            destination: getValue("destino"),
            start_date: getValue("fecha"),
            passengers: getValue("pasajeros"),
        };

        localStorage.setItem("pending_reservation", JSON.stringify(reservationData));
        window.location.href = "/payment";
    };
})();
