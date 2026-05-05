export default function Button({ variant = 'primary', children, ...props }) {
  const className = `button button-${variant}`;
  return (
    <button className={className} {...props}>
      {children}
    </button>
  );
}
