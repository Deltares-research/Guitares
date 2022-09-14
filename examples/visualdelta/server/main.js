//import mapboxgl from './assets/index.9e7ef0f8.js'; // or "const mapboxgl = require('mapbox-gl');"
console.log('main.js ...')

import mapboxgl from 'https://cdn.skypack.dev/mapbox-gl'

let mapMoved;
let layerAdded;
let layerName;
let layerGroupName;
let jsonString;
let idCounter = 0;
let layerID = 'abc';

console.log('Adding MapBox map ...')

mapboxgl.accessToken = 'pk.eyJ1IjoibXZhbm9ybW9uZHQiLCJhIjoiY2w1cnkyMHM3MGh3aTNjbjAwajh0NHUyZiJ9.5h1GFWjmJGW5hAK2FFCVDQ';

const map = new mapboxgl.Map({
  container: 'map', // container ID
  style: 'mapbox://styles/mapbox/streets-v11', // style URL
  center: [5.0, 52.0], // starting position [lng, lat]
  zoom: 6, // starting zoom
//  projection: 'globe' // display the map as a 3D globe
  projection: 'mercator' // display the map as a 3D globe
});

map.on('moveend', () => {
    console.log('A moveend event occurred.');
    onMoveEnd();
});

map.scrollZoom.setWheelZoomRate(1 / 200);
//map.on('style.load', () => {
//  map.setFog({}); // Set the default atmosphere style
//});


//export function updateImageLayer(overlayFile, extent, srs, proj4String) {
//
//    proj4.defs(srs, proj4String);
//    register(proj4);
//	imageLayer.setSource(new Static({
//        url: 'http://localhost:3000/' + overlayFile,
//        projection: srs,
//        imageExtent: extent,
//      })
//    )
//    imageLayer.setOpacity(0.5);
//}

new QWebChannel(qt.webChannelTransport, function (channel) {

    window.MapBox = channel.objects.MapBox;

    if(typeof MapBox != 'undefined') {
        mapMoved          = function() { MapBox.mapMoved(jsonString) };
//        layerAdded        = function() { console.log("Added " + layerName); MapBox.layerAdded(layerName, layerGroupName, idCounter.toString()); };
        layerAdded        = function() { MapBox.layerAdded(layerID); };
    }

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

//export function addImageLayer(fileName, name, group, id, bounds) {
export function addImageLayer(fileName, id, bounds, colorbar) {

//	console.log('Loading ' + fileName + ' - id=' + id);
//	layerID = id;

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


    // Legend
    const legend     = document.createElement("div");
    legend.id        = "overlay_legend";
    legend.className = "map-overlay";
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


//export function addMarkerLayer(geojson, markerFile, name, group) {
export function addMarkerLayer(geojson, markerFile, id) {

	layerID = id;

    map.removeImage('icons/' + markerFile);

    map.loadImage('icons/' + markerFile,
        (error, image) => {
            if (error) throw error;
            map.addImage(id, image);

            // Add a GeoJSON source with 2 points
            map.addSource(id, {
			      type: 'geojson',
			      data: geojson
            })

            // Add a symbol layer
            map.addLayer({
                'id': id,
                'type': 'symbol',
                'source': id,
                'layout': {
                    'icon-image': id,
                    'icon-size': 0.5,
                    'text-field': ['get', 'title'],
                    'text-font': [
                        'Open Sans Semibold',
                        'Arial Unicode MS Bold'
                    ],
                    'text-offset': [0, 1.25],
                    'text-anchor': 'top'
                }
            });
        }
    );

    layerAdded();

}


export function removeLayer(id) {
	// Remove layer
	console.log("Removing " + id + " ...");
	var mapLayer = map.getLayer(id);
	    if(typeof mapLayer !== 'undefined') {
	      // Remove map layer & source.
	      map.removeLayer(id).removeSource(id);
    }
    var legend = document.getElementById("overlay_legend")
    if (legend) {
		legend.remove();
    }
	console.log("Removed " + id + ".");
}
