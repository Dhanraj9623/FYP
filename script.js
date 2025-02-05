let map = L.map('map').setView([18.52, 73.85], 12); // Center on Pune

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

let drawControl = new L.Control.Draw({
    draw: {
        polygon: true,   // drawing polygons
        rectangle: true, // drawing rectangles
        polyline: false,
        circle: false,
        marker: false,
        circlemarker: false
    },
    edit: {
        featureGroup: drawnItems,
        remove: true
    }
});
map.addControl(drawControl);

let selectedPolygon = null;

map.on(L.Draw.Event.CREATED, function (event) {
    let layer = event.layer;

    drawnItems.clearLayers();
    drawnItems.addLayer(layer);
    selectedPolygon = layer.toGeoJSON();
});

// Fetching Data from Python Backend
document.getElementById('calculate').addEventListener('click', function () {
    if (!selectedPolygon) {
        alert("Please draw a polygon or rectangle first.");
        return;
    }

    // Convert to coordinate format expected by backend
    let coordinates = selectedPolygon.geometry.coordinates[0].map(coord => coord.reverse());

    fetch('http://127.0.0.1:5000/get_solar_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ polygon: coordinates })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').innerText = `Total Building Area: ${data.total_area} m²`;
    })
    .catch(error => console.error('Error:', error));
});
