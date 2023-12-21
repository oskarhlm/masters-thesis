import styles from './styles.module.css';
import maplibregl from 'maplibre-gl';

import 'maplibre-gl/dist/maplibre-gl.css';
import { onMount } from 'solid-js';

export default function Map() {
  let mapRef: HTMLDivElement | undefined;

  onMount(() => {
    const map = new maplibregl.Map({
      container: mapRef as HTMLElement,
      style: 'https://demotiles.maplibre.org/style.json', // style URL
      center: [139.753, 35.6844],
      zoom: 3,
    });
  });

  return <div id={styles['map']} ref={mapRef} />;
}
