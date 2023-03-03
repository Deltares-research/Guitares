import { map, featureClicked, mapboxgl } from '/js/main.js';

export function addLayer(id, data, fillColor, fillOpacity, lineWidth, circleRadius, selectionOption, hoveredId) {

  let selectedId = null
  let fillId = "fill_" + id
  let lineId = "line_" + id
  var selectedFeatures = []
  console.log(data)

  map.loadImage('./js/img/cross-marker-48-green.png',
    (error, image) => {
       if (error) throw error;
         map.addImage('custom-marker', image);
    }
  );

  map.addSource(id, {
    type: 'geojson',
    data: data
  });

//const marker = new map.Marker({draggable: true});

//  map.addLayer({
//    'id': 'points',
//    'type': 'symbol',
//    'source': id
//  });

  // Add a symbol layer
  map.addLayer({
    'id': id,
    'type': 'circle',
    'source': id,
    'paint': {
      'circle-color': fillColor,
      'circle-stroke-width': lineWidth,
      'circle-radius': circleRadius,
      'circle-opacity': 0.75
    }
  });

//  // Add a symbol layer
//  map.addLayer({
//    'id': 'points',
//    'type': 'symbol',
//    'source': id,
//    'layout': {
//      'icon-image': 'custom-marker',
//      'icon-size': 0.25,
//      // get name from the source's "name" property
//      'text-field': ['get', 'name'],
//      'text-font': [
//        'Open Sans Semibold',
//        'Arial Unicode MS Bold'
//      ],
//      'text-offset': [0, 0.5],
//      'text-anchor': 'top'
//    }
//  });

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
                var description   = e.features[0].properties[hoveredId];
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
                popup.setLngLat(coordinates).setHTML(hoveredId + ": " + description).addTo(map);

            });

            map.on('mouseleave', id, () => {
                map.getCanvas().style.cursor = '';
                popup.remove();
            });

  // When the user moves their mouse over the fill layer, we'll update the
  // feature state for the feature under the mouse.
  map.on('mousemove', fillId, (e) => {
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
