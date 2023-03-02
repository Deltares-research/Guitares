// © Deltares 2023.
// License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
// 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
// Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.
//
// This tool is developed for demonstration purposes only.

console.log('main.js ...')

import mapboxgl from 'https://cdn.skypack.dev/mapbox-gl'

let mapMoved;
let layerAdded;
let mapBoxReady;
let layerName;
let layerGroupName;
let jsonString;
let coordsClicked;
let coords;
let layerID = 'abc';
let color;

console.log('Adding MapBox map ...')

mapboxgl.accessToken = mapbox_token;

const map = new mapboxgl.Map({
  container: 'map', // container ID
  style: 'mapbox://styles/mapbox/streets-v11', // style URL
  center: [84.10, 28.39], // starting position [lng, lat]
  zoom: 6, // starting zoom
//  projection: 'globe' // display the map as a 3D globe
  projection: 'mercator' // display the map as a 3D globe
});


new QWebChannel(qt.webChannelTransport, function (channel) {

    window.MapBox = channel.objects.MapBox;

    if(typeof MapBox != 'undefined') {
        mapMoved          = function() { MapBox.mapMoved(jsonString) };
        layerAdded        = function() { MapBox.layerAdded(layerID); };
        coordsClicked     = function() { MapBox.coordsClicked(coords); };
//        mapBoxReady       = function() { MapBox.mapBoxReady("okay"); };
    }

});

map.on('moveend', () => {
//    console.log('A moveend event occurred.');
    onMoveEnd();
});


function onMoveEnd(evt) {
	// Called after moving map ended
	// Get new map extents
    var extent = map.getBounds();
    var se = extent.getSouthEast();
    var nw = extent.getNorthWest();
    var bottomLeft = [se["lng"], se["lat"]];
    var topRight   = [nw["lng"], nw["lat"]];
    jsonString = JSON.stringify([bottomLeft, topRight]);
    mapMoved();
}

map.scrollZoom.setWheelZoomRate(1 / 200);

// Add navigation controls
map.addControl(new mapboxgl.NavigationControl());

// Create a marker and update it's coordinates on click.
var marker = new mapboxgl.Marker();

function add_marker (event) {
  var coordinates = event.lngLat;
  console.log('Lng:', coordinates.lng, 'Lat:', coordinates.lat);
  marker.setLngLat(coordinates).addTo(map);
  coords = JSON.stringify(coordinates);
  coordsClicked();
}

map.on('click', add_marker);


export function addLineGeojsonLayer (geojson, id, layerName, layerGroupName, color) {
  // Show the lines as GeoJSON
    map.addSource(id, {
        type: 'geojson',
        data: geojson
    });

    map.addLayer({
        'id': id,
        'type': 'line',
        'source': id,
        'layout': {
            'line-join': 'round',
            'line-cap': 'round'
        },
        'paint': {
            'line-width': 3,
            'line-color': color
        }
    });

    layerAdded(layerName, layerGroupName, id);
};


export function addLineGeojsonLayerColorByProperty (geojson, id, layerName, layerGroupName, color_by) {
  // Show the lines as GeoJSON
    map.addSource(id, {
        type: 'geojson',
        data: geojson
    });

    map.addLayer({
        'id': id,
        'type': 'line',
        'source': id,
        'layout': {
            'line-join': 'round',
            'line-cap': 'round'
        },
        'paint': {
            'line-width': 3,
            'line-color':  [
              "match",
              ["get", color_by],
              0,
              "orange",
              1,
              "#a81df2",
              "white"
            ]
        },
    });

    layerAdded(layerName, layerGroupName, id);
};


export function addImageLayer(fileName, id, bounds, colorbar) {

    map.addSource(id, {
        'type': 'image',
        'url': fileName,
        'coordinates': [
        [bounds[0][0], bounds[1][1]],
        [bounds[0][1], bounds[1][1]],
        [bounds[0][1], bounds[1][0]],
        [bounds[0][0], bounds[1][0]]
        ]
    });

    map.addLayer({
        'id': id,
        'source': id,
        'type': 'raster',
        'paint': {
            'raster-resampling': 'nearest'
        }
    });

    map.fitBounds([
        [bounds[0][0], bounds[1][1]],
        [bounds[0][1], bounds[1][0]]
        ]);

    // Legend
    const legend     = document.createElement("div");
    legend.id        = "legend" + id;
    legend.className = "overlay_legend";
    var newSpan = document.createElement('span');
    newSpan.class = 'title';
    newSpan.innerHTML = '<b>' + colorbar["title"] + '</b>';
    legend.appendChild(newSpan);
    legend.appendChild(document.createElement("br"));
    for (let i = 0; i < colorbar["contour"].length; i++) {
    let cnt = colorbar["contour"][i]
        var newI = document.createElement('i');
        newI.setAttribute('style','background:' + cnt["color"]);
        legend.appendChild(newI);
        var newSpan = document.createElement('span');
        newSpan.innerHTML = cnt["text"];
        legend.appendChild(newSpan);
        legend.appendChild(document.createElement("br"));
    }
    document.body.appendChild(legend);

    layerAdded();

}

export function removeLayer(id) {
	// Remove layer
	var mapLayer = map.getLayer(id);
	    if(typeof mapLayer !== 'undefined') {
	      // Remove map layer & source.
	      map.removeLayer(id).removeSource(id);
    }
    var legend = document.getElementById("legend" + id);
    if (legend) {
        legend.remove();
    }
}


export function flyTo(lon, lat, zoom) {
	// Called after moving map ended
	// Get new map extents
	map.flyTo({center: [lon, lat], zoom: zoom});
}
