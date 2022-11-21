//import mapboxgl from './assets/index.9e7ef0f8.js'; // or "const mapboxgl = require('mapbox-gl');"
console.log('main.js ...')

import mapboxgl from 'https://cdn.skypack.dev/mapbox-gl'

let mapMoved;
let layerAdded;
let layerName;
let layerGroupName;
let jsonString;
let idCounter = 0;

console.log('Adding MapBox map ...')

mapboxgl.accessToken = 'pk.eyJ1IjoiZnJlZGVyaXF1ZTEyMyIsImEiOiJjbGFxcHBmYnAxbWdzM3JvYmFkdTBscjJmIn0.PZlYCN_VXpiX90ik-8C3rw';

const map = new mapboxgl.Map({
  container: 'map', // container ID
  style: 'mapbox://styles/mapbox/streets-v11', // style URL
  center: [-2.5, 52.0], // starting position [lng, lat]
  zoom: 5, // starting zoom
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
        layerAdded        = function() { console.log("Added " + layerName); MapBox.layerAdded(layerName, layerGroupName, idCounter.toString()); };
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

export function addImageLayer(fileName, name, group, bounds) {
	console.log('Loading ' + fileName);
	idCounter += 1;
	layerName = name;
	layerGroupName = group;
    map.addSource(idCounter.toString(), {
        'type': 'image',
        'url': fileName,
        'coordinates': [
        [bounds[0][0], bounds[1][1]],
        [bounds[0][1], bounds[1][1]],
        [bounds[0][1], bounds[1][0]],
        [bounds[0][0], bounds[1][0]]
        ]
    });

	console.log('Adding ' + name + ' to ' + group + ' - id=' + idCounter);

    map.addLayer({
        'id': idCounter.toString(),
        'source': idCounter.toString(),
        'type': 'raster',
        'paint': {
            'raster-resampling': 'nearest'
        }
    });

    console.log("Added")

    console.log(layerAdded)

    layerAdded();

}

export function removeLayer(idString) {
	// Remove layer
	console.log("Removing " + idString);
	map.removeLayer(idString);
	console.log("Layer " + idString + " removed");
	// Remove source
	map.removeSource(idString);
	console.log("Source " + idString + " removed");


}
