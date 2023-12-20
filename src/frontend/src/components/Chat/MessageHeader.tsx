import { MessageSource } from './types';
import styles from './styles.module.css';

type Props = {
  source: MessageSource;
};

export function MessageHeader(props: Props) {
  return (
    <div class={`${styles['group-header']} ${styles[props.source]}`}>
      {props.source}
    </div>
  );
}
