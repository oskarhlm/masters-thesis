import './styles.css';
import maplibregl from 'maplibre-gl';

import 'maplibre-gl/dist/maplibre-gl.css';
import { createSignal, onMount } from 'solid-js';

export const [map, setMap] = createSignal<maplibregl.Map>();

export function addGeoJSONToMap(geojson: GeoJSON.FeatureCollection) {
  const sourceId = `geojson_data-${new Date().getTime()}`;
  const layerId = sourceId;
  console.log(sourceId);

  const randomHexColor = () =>
    '#' + ((Math.random() * 0xffffff) << 0).toString(16).padStart(6, '0');

  map()!.addSource(sourceId, {
    type: 'geojson',
    data: geojson,
    // data: 'output.geojson',
  });

  if (geojson.features[0].geometry.type === 'MultiLineString') {
    console.log(geojson);
    map()!.addLayer({
      id: layerId,
      type: 'line',
      source: sourceId,
      paint: {
        'line-color': randomHexColor(),
        'line-width': 3,
      },
    });
  } else if (geojson.features[0].geometry.type === 'Polygon') {
    console.log(geojson);
    map()!.addLayer({
      id: layerId,
      type: 'fill',
      source: sourceId,
      paint: {
        'fill-color': randomHexColor(),
      },
    });
  } else {
    console.error(
      `Geometry ${geojson.features[0].geometry.type} is not yet supported.`
    );
  }
}

export default function Map() {
  let mapRef: HTMLDivElement | undefined;

  onMount(() => {
    const map = new maplibregl.Map({
      container: mapRef as HTMLElement,
      style:
        'https://api.maptiler.com/maps/bright-v2/style.json?key=Ef2vgWdLvtIRszls4CV1',
      center: [10.421906, 63.4],
      zoom: 10,
    });
    setMap(map);
  });

  return <div id="map" ref={mapRef} />;
}
