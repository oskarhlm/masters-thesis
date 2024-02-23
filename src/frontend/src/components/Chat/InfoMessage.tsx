import { Component, JSX } from 'solid-js';
import './styles.css';

type Props = {
  content: string | JSX.Element;
};

const InfoMessage: Component<Props> = (props) => {
  // return <div class="info-msg">{props.content}</div>;
  return <></>;
};

export default InfoMessage;
