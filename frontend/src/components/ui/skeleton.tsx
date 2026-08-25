import type { CSSProperties } from "react";

interface SkeletonProps {
  className?: string;
  style?: CSSProperties;
}

export default function Skeleton({
  className = "",
  style,
}: SkeletonProps) {
  return (
    <div
      style={style}
      className={`animate-pulse rounded-lg bg-slate-200 ${className}`}
    />
  );
}