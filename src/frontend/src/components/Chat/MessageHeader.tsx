import { MessageSource } from './types';
import './styles.css';

type Props = {
  source: MessageSource;
};

export function MessageHeader(props: Props) {
  return (
    <div class={`group-header ${props.source}`}>
      {props.source === 'bot' ? 'GeoGPT' : 'You'}
    </div>
  );
}
