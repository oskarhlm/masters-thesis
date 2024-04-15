import { onMount, onCleanup, For, createSignal } from 'solid-js';
import { addedLayers, map, setAddedLayers } from './Map';

type Direction = 'up' | 'down';

export default function LayerList() {
  const [focusedIndex, setFocusedIndex] = createSignal<number | null>(null);

  function moveLayer(index: number, direction: Direction) {
    const currentLayers = addedLayers();
    let moved = false;

    if (direction === 'up' && index > 0) {
      [currentLayers[index - 1], currentLayers[index]] = [
        currentLayers[index],
        currentLayers[index - 1],
      ];
      moved = true;
    } else if (direction === 'down' && index < currentLayers.length - 1) {
      [currentLayers[index + 1], currentLayers[index]] = [
        currentLayers[index],
        currentLayers[index + 1],
      ];
      moved = true;
    }

    if (moved) {
      setAddedLayers([...currentLayers]);
      setFocusedIndex(index + (direction === 'up' ? -1 : 1));
      updateLayerOrder();
    }

    console.log(focusedIndex());
    console.log(map()!.getLayersOrder());
    console.log(addedLayers());
  }

  function updateLayerOrder() {
    const layers = addedLayers();
    for (let i = layers.length - 1; i >= 0; i--) {
      map()!.moveLayer(layers[i]); // This moves the layer to the top
    }
  }

  const handleKeyDown = (e: any) => {
    if (focusedIndex() === null) return;
    if (e.key === 'ArrowUp') {
      moveLayer(focusedIndex()!, 'up');
    } else if (e.key === 'ArrowDown') {
      moveLayer(focusedIndex()!, 'down');
    }
  };

  onMount(() => {
    window.addEventListener('keydown', handleKeyDown);
  });

  onCleanup(() => {
    window.removeEventListener('keydown', handleKeyDown);
  });

  return (
    <div id="layer-list-container">
      <ul>
        <For each={addedLayers()}>
          {(layer, index) => (
            <li
              onclick={() =>
                setFocusedIndex(focusedIndex() === index() ? null : index())
              }
              class={`layer-list-item ${
                index() === focusedIndex() ? 'selected' : ''
              }`}
            >
              {layer}
            </li>
          )}
        </For>
      </ul>
    </div>
  );
}
