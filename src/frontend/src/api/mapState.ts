import { post } from './apiHelper';
import { map, addedLayers } from '../components/Map/Map';

export async function updateMapState() {
  await post('/update-map-state', {
    center: map()!.getCenter(),
    bounds: map()!.getBounds(),
    zoom: {
      current: map()!.getZoom(),
      max: map()!.getMaxZoom(),
      min: map()!.getMinZoom(),
    },
    layers: map()!
      .getStyle()
      .layers.filter((l) => addedLayers().includes(l.id)),
  });
}
