import { PropsWithChildren } from 'react';

interface Props extends PropsWithChildren {
  title: string;
  subtitle?: string;
}

export function Section({ title, subtitle, children }: Props) {
  return (
    <section className="section">
      <div className="section-header">
        <div>
          <h2>{title}</h2>
          {subtitle ? <p className="muted">{subtitle}</p> : null}
        </div>
      </div>
      {children}
    </section>
  );
}
