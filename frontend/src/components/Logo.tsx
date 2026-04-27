const SIZES = {
  sm: 24,
  md: 32,
  lg: 64,
  xl: 96,
} as const;

interface Props {
  size?: keyof typeof SIZES;
  className?: string;
}

const Logo = ({ size = "md", className }: Props) => {
  const px = SIZES[size];
  return (
    <svg
      width={px}
      height={px}
      viewBox="0 0 64 64"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
      className={className}
    >
      <rect width="64" height="64" rx="12" fill="#022c22" />
      <circle cx="32" cy="32" r="24" fill="#065f46" />
      <circle cx="32" cy="32" r="18" fill="#ecfdf5" />
      <circle cx="32" cy="32" r="12" fill="#0b6e4f" />
      <circle cx="32" cy="32" r="5" fill="#022c22" />
      <circle cx="34" cy="30" r="1.4" fill="#ecfdf5" />
    </svg>
  );
};

export default Logo;
