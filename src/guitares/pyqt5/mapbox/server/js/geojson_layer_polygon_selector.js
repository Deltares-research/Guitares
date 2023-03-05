import { map, featureClicked, mapboxgl} from '/js/main.js';

export function addLayer(id, data, fillColor, fillOpacity, lineColor, lineWidth, selectionOption, highlight) {

  let selectedId = null
  let hoveredId = null
  let fillId = id + ".fill"
  let fillId2 = id + ".fill2"
  let lineId = id + ".line"
  let lineId2 = id + ".line2"
  var selectedFeatures = []

  map.addSource(id, {
    type: 'geojson',
    data: data
  });

  map.addLayer({
    'id': lineId,
    'type': 'line',
    'source': id,
    'layout': {},
    'paint': {
      'line-color': lineColor,
      'line-width': lineWidth
     }
  });

  map.addLayer({
    'id': lineId2,
    'type': 'line',
    'source': id,
    'paint': {
      'line-color': fillColor,
      'line-width': 2
    },
    "filter": ["==", highlight, ""]
  });

  map.addLayer({
    'id': fillId,
    'type': 'fill',
    'source': id,
    'paint': {
      'fill-color': fillColor,
      'fill-opacity': ['case', ['any', ['boolean', ['feature-state', 'hover'], false], ['boolean', ['feature-state', 'selected'], false]], fillOpacity, 0.0],
      'fill-outline-color': 'transparent'
    }
  });

  map.addLayer({
    'id': fillId2,
    'type': 'fill',
    'source': id,
    'paint': {
      'fill-color': fillColor,
      'fill-opacity': 0.3,
      'fill-outline-color': '#000'
    },
    "filter": ["==", highlight, ""]
  });

//  map.addLayer({
//    'id': 'points',
//    'type': 'symbol',
//    'source': id,
//    'layout': {
//      // get the title name from the source's "title" property
//      'text-field': ['get', 'utm_number'],
//      'text-font': [
//        'Open Sans Semibold',
//        'Arial Unicode MS Bold'
//      ],
//      'text-offset': [0, 0],
//      'text-anchor': 'top',
//      'text-size': 12
//    }
//  });
  // Create a popup, but don't add it to the map yet.
  const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
  });
  // When the user moves their mouse over the fill layer, we'll update the
  // feature state for the feature under the mouse.
  map.on('mousemove', fillId, (e) => {
    // Change the cursor style as a UI indicator.
    map.getCanvas().style.cursor = 'pointer';
    if (e.features.length > 0) {
      if (hoveredId !== null) {
        map.setFeatureState(
          { source: id, id: hoveredId },
          { hover: false }
        );
      }
      hoveredId = e.features[0].id;
      map.setFeatureState(
        { source: id, id: hoveredId },
        { hover: true }
      );

      // Display a popup with the name of area
      popup.setLngLat(e.lngLat)
      .setText(e.features[0].properties[highlight])
      .addTo(map);
    }
  });

  // When the mouse leaves the fill layer, update the feature state of the
  // previously hovered feature.
  map.on('mouseleave', fillId, () => {
    if (hoveredId !== null) {
      map.setFeatureState(
        { source: id, id: hoveredId },
        { hover: false }
      );
    }
    hoveredId = null;
    popup.remove();
  });

  if (selectionOption == "single") {
    map.on('click', fillId, (e) => {
      if (e.features.length > 0) {
        // Set previous selected to False
        map.setFeatureState(
          { source: id, id: selectedId },
          { selected: false }
        );
        selectedId = e.features[0].id
        map.setFeatureState(
          { source: id, id: e.features[0].id },
          { selected: true }
        );
        featureClicked(id, e.features[0]);
      };
    });
  } else {
    map.on('click', fillId, (e) => {
      if (e.features.length > 0) {
        var featureState = map.getFeatureState({ source: id, id: e.features[0].id });
        if (featureState.selected) {
          // Was selected, now deselect
          map.setFeatureState(
            { source: id, id: e.features[0].id },
            { selected: false }
          );
          selectedFeatures.pop(e.features[0]);
        } else {
          // Select
          map.setFeatureState(
            { source: id, id: e.features[0].id },
            { selected: true }
          );
          selectedFeatures.push(e.features[0]);
        };
        // Now make a list of all selected features
//        var selectedFeatureProperties = []
//        selectedFeatures.forEach((feature) => {
//          var featureState = map.getFeatureState({ source: id, id: feature.id });
//          if (featureState.selected) {
//            selectedFeatureProperties.push(feature);
//          }
//        });
        featureClicked(id, selectedFeatures);
      };
    });


  }
};

export function setData(id, data) {
  console.log('setting data in ' + id);
  console.log(data);
  var source = map.getSource(id);
  source.setData(data);
}

export function highlightData(id, highlight, value) {
  map.setFilter(id + ".line2", ["==", highlight, value])
  map.setFilter(id + ".fill2", ["==", highlight, value])
}
