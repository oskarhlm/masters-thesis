import { Component, Show } from 'solid-js';
import showdown from 'showdown';
import './styles.css';

type Props = {
  message: string;
};

const converter = new showdown.Converter();

const SpinnerMessage: Component<Props> = (props) => {
  return (
    <span class="spinner-wrapper">
      <Show when={props.message}>
        <div class={`message`} innerHTML={converter.makeHtml(props.message)} />
      </Show>
      <span class="loader"></span>
    </span>
  );
};

export default SpinnerMessage;
