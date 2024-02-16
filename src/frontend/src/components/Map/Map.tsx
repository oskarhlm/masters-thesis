import './styles.css';
import maplibregl from 'maplibre-gl';

import 'maplibre-gl/dist/maplibre-gl.css';
import { createSignal, onMount } from 'solid-js';

export const [map, setMap] = createSignal<maplibregl.Map>();

export function addGeoJSONToMap(
  geojson: GeoJSON.FeatureCollection,
  layerName: string
) {
  // const sourceId = `geojson_data-${new Date().getTime()}`;
  const sourceId = layerName;
  const layerId = sourceId;

  const randomHexColor = () =>
    '#' + ((Math.random() * 0xffffff) << 0).toString(16).padStart(6, '0');

  map()!.addSource(sourceId, {
    type: 'geojson',
    data: geojson,
  });

  const geometryType = geojson.features[0].geometry.type;
  if (!geometryType) {
    console.error('Empty FeatureCollection');
  }

  switch (geometryType) {
    case 'MultiLineString':
    case 'LineString':
      map()!.addLayer({
        id: layerId,
        type: 'line',
        source: sourceId,
        paint: {
          'line-color': randomHexColor(),
          'line-width': 3,
        },
      });
      break;

    case 'Polygon':
    case 'MultiPolygon':
      map()!.addLayer({
        id: layerId,
        type: 'fill',
        source: sourceId,
        paint: {
          'fill-color': randomHexColor(),
        },
      });
      break;

    case 'Point':
    case 'MultiPoint':
      map()!.addLayer({
        id: layerId,
        type: 'circle',
        source: sourceId,
        paint: {
          'circle-radius': 5,
          'circle-color': randomHexColor(),
        },
      });
      break;

    default:
      console.error(`Geometry ${geometryType} is not yet supported.`);
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
