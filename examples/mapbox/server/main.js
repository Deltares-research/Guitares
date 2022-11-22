//import mapboxgl from './assets/index.9e7ef0f8.js'; // or "const mapboxgl = require('mapbox-gl');"
console.log('main.js ...');

import mapboxgl from 'https://cdn.skypack.dev/mapbox-gl'
//import mapboxMapboxGlDraw from 'https://cdn.skypack.dev/@mapbox/mapbox-gl-draw'

let mapMoved;
let layerAdded;
export let polygonDrawn;
export let featureSelected;
let layerName;
let layerGroupName;
let jsonString;
let idCounter = 0;
let layerID = 'abc';
let featureId = '';
let activeLayerId;
let drawLayer = {};

console.log('Adding MapBox map ...')

mapboxgl.accessToken = 'pk.eyJ1IjoibXZhbm9ybW9uZHQiLCJhIjoiY2w1cnkyMHM3MGh3aTNjbjAwajh0NHUyZiJ9.5h1GFWjmJGW5hAK2FFCVDQ';

export const map = new mapboxgl.Map({
  container: 'map', // container ID
  style: 'mapbox://styles/mapbox/streets-v11', // style URL
  center: [5.0, 52.0], // starting position [lng, lat]
  zoom: 6, // starting zoom
//  projection: 'globe' // display the map as a 3D globe
  projection: 'mercator' // display the map as a 3D globe
});

map.on('moveend', () => {
//    console.log('A moveend event occurred.');
    onMoveEnd();
});

export const draw = new MapboxDraw({displayControlsDefault: false});
map.addControl(draw, 'top-left');


//function selectionChange(e) {
//  console.log('selection changed')
//  console.log('mode = ' + draw.getMode())
//}

//map.on('draw.selectionchange', selectionChange);



//map.on('load', function() {
//  // ALL YOUR APPLICATION CODE
//});

//  draw.changeMode('draw_polygon');
//  console.log('mode2=' + draw.getMode())
//  draw.changeMode('direct_select');

//  if (data.features.length > 0) {
//   console.log(data.features.length)
//    }
//  else {
//    if (e.type !== 'draw.delete') {
//      alert('Click the map to draw a polygon.');
//    }
//}


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
//    if (typeof MapBox != 'undefined') {
        mapMoved          = function() { MapBox.mapMoved(jsonString)};
        layerAdded        = function() { MapBox.layerAdded(layerID)};
        polygonDrawn      = function() { console.log(jsonString); console.log(featureId); MapBox.polygonDrawn(jsonString, featureId)};
        featureSelected   = function(id) { MapBox.featureSelected(id)};
//        mapBoxReady       = function() { MapBox.mapBoxReady("okay")};
//    }
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


export function addMarkerLayer(geojson, markerFile, id) {

	layerID = id;

    if (map.hasImage(id)) {
        map.removeImage(id);
    }

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

            // Create a popup, but don't add it to the map yet.
            const popup = new mapboxgl.Popup({
                closeButton: false,
                closeOnClick: false
            });

            map.on('mouseenter', id, (e) => {

                // Change the cursor style as a UI indicator.
                map.getCanvas().style.cursor = 'pointer';

                // Copy coordinates array.
                const coordinates = e.features[0].geometry.coordinates.slice();
                var description   = e.features[0].properties.hover_popup_text;
                if (e.features[0].properties.hasOwnProperty('hover_popup_width')) {
					popup.setMaxWidth(e.features[0].properties.hover_popup_width);
			    }

                // Ensure that if the map is zoomed out such that multiple
                // copies of the feature are visible, the popup appears
                // over the copy being pointed to.
                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                }

                // Populate the popup and set its coordinates
                // based on the feature found.
                popup.setLngLat(coordinates).setHTML(description).addTo(map);

            });

            map.on('mouseleave', id, () => {
                map.getCanvas().style.cursor = '';
                popup.remove();
            });

        }
    );

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

// export function checkMapBoxReady() {
//  console.log("Checking ...")
//  mapBoxReady();
// }
