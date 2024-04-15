import './styles.css';
import maplibregl from 'maplibre-gl';

import 'maplibre-gl/dist/maplibre-gl.css';
import { createSignal, onMount, Show } from 'solid-js';
import bbox from '@turf/bbox';
import { updateMapState } from '../../api/mapState';
import LayerList from './LayerList';

export const [map, setMap] = createSignal<maplibregl.Map>();

export const [addedLayers, setAddedLayers] = createSignal<string[]>([]);

export function addGeoJSONToMap(
  geojson: GeoJSON.FeatureCollection | GeoJSON.Feature,
  layerName: string
) {
  const sourceId = layerName;
  const layerId = sourceId;

  const randomHexColor = () =>
    '#' + ((Math.random() * 0xffffff) << 0).toString(16).padStart(6, '0');

  function adjustColor(color: string, amount: number) {
    color = color.replace(/^#/, '');
    if (color.length === 3)
      color = color[0] + color[0] + color[1] + color[1] + color[2] + color[2];

    let [r, g, b]: any = color.match(/.{2}/g);
    [r, g, b] = [
      parseInt(r, 16) + amount,
      parseInt(g, 16) + amount,
      parseInt(b, 16) + amount,
    ];

    r = Math.max(Math.min(255, r), 0).toString(16);
    g = Math.max(Math.min(255, g), 0).toString(16);
    b = Math.max(Math.min(255, b), 0).toString(16);

    const rr = (r.length < 2 ? '0' : '') + r;
    const gg = (g.length < 2 ? '0' : '') + g;
    const bb = (b.length < 2 ? '0' : '') + b;

    return `#${rr}${gg}${bb}`;
  }

  map()!.addSource(sourceId, {
    type: 'geojson',
    data: geojson,
  });

  console.log(geojson);

  const geometryType =
    geojson.type === 'Feature'
      ? geojson.geometry.type
      : geojson.features[0].geometry.type;

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
      const hex = randomHexColor();
      map()!.addLayer({
        id: layerId,
        type: 'fill',
        source: sourceId,
        paint: {
          'fill-color': randomHexColor(),
        },
      });

      const borderColor = adjustColor(hex, -40);
      map()!.addLayer({
        id: layerId + '-border',
        type: 'line',
        source: sourceId,
        paint: {
          'line-color': borderColor,
          'line-width': 2,
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

  setAddedLayers([...addedLayers(), layerId]);

  const bounds = bbox(geojson);
  map()!.fitBounds(bounds as any, { padding: 20 });
  console.log(
    map()!
      .getStyle()
      .layers.filter((l) => addedLayers().includes(l.id))
  );
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
      maxZoom: 17,
    });

    map.on('load', updateMapState);
    map.on('moveend', updateMapState);

    setMap(map);
  });

  return (
    <div id="map-container">
      <div id="map" ref={mapRef} />
      <Show when={addedLayers().length}>
        <LayerList />
      </Show>
    </div>
  );
}
