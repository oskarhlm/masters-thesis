import { Component } from 'solid-js';
import showdown from 'showdown';
import './styles.css';

type Props = {
  toolName: string;
  toolInput?: string;
  toolOuput?: string;
};

const converter = new showdown.Converter();

const ToolMessage: Component<Props> = (props) => {
  return (
    <span class="message bot tool">
      <span class="" innerHTML={converter.makeHtml(props.toolName)} />
    </span>
  );
};

export default ToolMessage;
